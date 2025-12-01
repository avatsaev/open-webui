import logging
import time
from typing import Optional

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.env import SRC_LOG_LEVELS

from open_webui.models.groups import Groups
from open_webui.models.users import User, UserModel, Users, UserResponse


from pydantic import BaseModel, ConfigDict

from sqlalchemy import String, cast, or_, and_, func
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy import BigInteger, Column, Text, JSON, Boolean


from open_webui.utils.access_control import has_access


log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["APPS"])


####################
# Apps DB Schema
####################


# AppParams is a app for the data stored in the params field of the App table
class AppParams(BaseModel):
    model_config = ConfigDict(extra="allow")
    pass


# AppMeta is a app for the data stored in the meta field of the App table
class AppMeta(BaseModel):
    icon_image_url: Optional[str] = "/static/favicon.png"
    thumbnail_image_url: Optional[str] = "/static/favicon.png"

    description: Optional[str] = None
    tags: Optional[list[str]] = []

    pass


class App(Base):
    __tablename__ = "app"

    id = Column(Text, primary_key=True)
    """
        The app's id as used in the API. If set to an existing app, it will override the app.
    """
    user_id = Column(Text)

    source_chat_id = Column(Text, nullable=True)
    """
        An optional pointer to the actual chat where the app was created from.
    """

    title = Column(Text)
    """
        The human-readable display name of the app.
    """
    
    source_code = Column(Text)
    """
        base64 encoded source code of the app.
    """

    params = Column(JSONField)
    """
        Holds a JSON encoded blob of parameters, see `AppParams`.
    """

    meta = Column(JSONField)
    """
        Holds a JSON encoded blob of metadata, see `AppMeta`.
    """

    access_control = Column(JSON, nullable=True)  # Controls data access levels.
    # Defines access control rules for this entry.
    # - `None`: Public access, available to all users with the "user" role.
    # - `{}`: Private access, restricted exclusively to the owner.
    # - Custom permissions: Specific access control for reading and writing;
    #   Can specify group or user-level restrictions:
    #   {
    #      "read": {
    #          "group_ids": ["group_id1", "group_id2"],
    #          "user_ids":  ["user_id1", "user_id2"]
    #      },
    #      "write": {
    #          "group_ids": ["group_id1", "group_id2"],
    #          "user_ids":  ["user_id1", "user_id2"]
    #      }
    #   }

    is_active = Column(Boolean, default=True)

    updated_at = Column(BigInteger)
    created_at = Column(BigInteger)


class AppModel(BaseModel):
    id: str
    user_id: str
    source_chat_id: Optional[str] = None
    title: str
    source_code: str
    params: AppParams
    meta: AppMeta
    access_control: Optional[dict] = None
    is_active: bool
    updated_at: int
    created_at: int


####################
# Forms
####################

class AppUserResponse(AppModel):
    user: Optional[UserResponse] = None


class AppResponse(AppModel):
    pass


class AppListResponse(BaseModel):
    items: list[AppUserResponse]
    total: int




class AppForm(BaseModel):
    id: str
    source_chat_id: Optional[str] = None
    title: str
    source_code: str
    meta: AppMeta
    params: AppParams
    access_control: Optional[dict] = None
    is_active: bool = True


class AppsTable:
    def insert_new_app(
        self, form_data: AppForm, user_id: str
    ) -> Optional[AppModel]:
        app = AppModel(
            **{
                **form_data.model_dump(),
                "user_id": user_id,
                "created_at": int(time.time()),
                "updated_at": int(time.time()),
            }
        )
        try:
            with get_db() as db:
                result = App(**app.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)

                if result:
                    return AppModel.model_validate(result)
                else:
                    return None
        except Exception as e:
            log.exception(f"Failed to insert a new app: {e}")
            return None

    def get_apps(self) -> list[AppModel]:
        with get_db() as db:
            return [AppModel.model_validate(app) for app in db.query(App).all()]

    def get_apps_by_user_id(
        self, user_id: str, permission: str = "write"
    ) -> list[AppUserResponse]:
        apps = self.get_apps()
        user_group_ids = {group.id for group in Groups.get_groups_by_member_id(user_id)}
        return [
            app
            for app in apps
            if app.user_id == user_id
            or has_access(user_id, permission, app.access_control, user_group_ids)
        ]

    def search_apps(
        self, user_id: str, filter: dict = {}, skip: int = 0, limit: int = 30
    ) -> AppListResponse:
        with get_db() as db:
            # Join GroupMember so we can order by group_id when requested
            query = db.query(App, User).outerjoin(User, User.id == App.user_id)


            if filter:
                query_key = filter.get("query")
                if query_key:
                    query = query.filter(App.title.ilike(f"%{query_key}%"))

                if filter.get("user_id"):
                    query = query.filter(App.user_id == filter.get("user_id"))

                view_option = filter.get("view_option")

                if view_option == "created":
                    query = query.filter(App.user_id == user_id)
                elif view_option == "shared":
                    query = query.filter(App.user_id != user_id)

                tag = filter.get("tag")
                if tag:
                    # TODO: This is a simple implementation and should be improved for performance
                    like_pattern = f'%"{tag.lower()}"%'  # `"tag"` inside JSON array
                    meta_text = func.lower(cast(App.meta, String))

                    query = query.filter(meta_text.like(like_pattern))

                order_by = filter.get("order_by")
                direction = filter.get("direction")

                if order_by == "title":
                    if direction == "asc":
                        query = query.order_by(App.title.asc())
                    else:
                        query = query.order_by(App.title.desc())
                elif order_by == "created_at":
                    if direction == "asc":
                        query = query.order_by(App.created_at.asc())
                    else:
                        query = query.order_by(App.created_at.desc())
                elif order_by == "updated_at":
                    if direction == "asc":
                        query = query.order_by(App.updated_at.asc())
                    else:
                        query = query.order_by(App.updated_at.desc())

            else:
                query = query.order_by(App.created_at.desc())

            # Count BEFORE pagination
            total = query.count()

            if skip:
                query = query.offset(skip)
            if limit:
                query = query.limit(limit)

            items = query.all()

            apps = []
            for app, user in items:
                apps.append(
                    AppUserResponse(
                        **AppModel.model_validate(app).model_dump(),
                        user=(
                            UserResponse(**UserModel.model_validate(user).model_dump())
                            if user
                            else None
                        ),
                    )
                )

            return AppListResponse(items=apps, total=total)

    def get_app_by_id(self, id: str) -> Optional[AppModel]:
        try:
            with get_db() as db:
                app = db.get(App, id)
                return AppModel.model_validate(app)
        except Exception:
            return None

    def toggle_app_by_id(self, id: str) -> Optional[AppModel]:
        with get_db() as db:
            try:
                is_active = db.query(App).filter_by(id=id).first().is_active

                db.query(App).filter_by(id=id).update(
                    {
                        "is_active": not is_active,
                        "updated_at": int(time.time()),
                    }
                )
                db.commit()

                return self.get_app_by_id(id)
            except Exception:
                return None

    def update_app_by_id(self, id: str, app: AppForm) -> Optional[AppModel]:
        try:
            with get_db() as db:
                # update only the fields that are present in the app
                data = app.model_dump(exclude={"id"})
                result = db.query(App).filter_by(id=id).update(data)

                db.commit()

                app = db.get(App, id)
                db.refresh(app)
                return AppModel.model_validate(app)
        except Exception as e:
            log.exception(f"Failed to update the app by id {id}: {e}")
            return None

    def delete_app_by_id(self, id: str) -> bool:
        try:
            with get_db() as db:
                db.query(App).filter_by(id=id).delete()
                db.commit()

                return True
        except Exception:
            return False

    def delete_all_apps(self) -> bool:
        try:
            with get_db() as db:
                db.query(App).delete()
                db.commit()

                return True
        except Exception:
            return False



Apps = AppsTable()
