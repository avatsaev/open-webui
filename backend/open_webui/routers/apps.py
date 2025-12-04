from typing import Optional
import io
import base64
import json
import asyncio
import logging

from open_webui.models.apps import (
    AppForm,
    AppModel,
    AppResponse,
    AppListResponse,
    Apps,
)

from pydantic import BaseModel
from open_webui.constants import ERROR_MESSAGES
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    Response,
)
from fastapi.responses import FileResponse, StreamingResponse


from open_webui.utils.auth import get_admin_user, get_verified_user
from open_webui.utils.access_control import has_access, has_permission
from open_webui.config import BYPASS_ADMIN_ACCESS_CONTROL, STATIC_DIR

log = logging.getLogger(__name__)

router = APIRouter()



###########################
# GetApps
###########################


PAGE_ITEM_COUNT = 30


@router.get(
    "/list", response_model=AppListResponse
)  # do NOT use "/" as path, conflicts with main.py
async def get_apps(
    query: Optional[str] = None,
    view_option: Optional[str] = None,
    tag: Optional[str] = None,
    order_by: Optional[str] = None,
    direction: Optional[str] = None,
    page: Optional[int] = 1,
    user=Depends(get_verified_user),
):

    limit = PAGE_ITEM_COUNT

    page = max(1, page)
    skip = (page - 1) * limit

    filter = {}
    if query:
        filter["query"] = query
    if view_option:
        filter["view_option"] = view_option
    if tag:
        filter["tag"] = tag
    if order_by:
        filter["order_by"] = order_by
    if direction:
        filter["direction"] = direction

    if not user.role == "admin" or not BYPASS_ADMIN_ACCESS_CONTROL:
        filter["user_id"] = user.id

    return Apps.search_apps(user.id, filter=filter, skip=skip, limit=limit)


###########################
# GetAppTags
###########################


@router.get("/tags", response_model=list[str])
async def get_app_tags(user=Depends(get_verified_user)):
    if user.role == "admin" and BYPASS_ADMIN_ACCESS_CONTROL:
        apps = Apps.get_apps()
    else:
        apps = Apps.get_apps_by_user_id(user.id)

    tags_set = set()
    for app in apps:
        if app.meta:
            meta = app.meta.model_dump()
            for tag in meta.get("tags", []):
                tags_set.add(tag)

    tags = [tag for tag in tags_set]
    tags.sort()
    return tags


############################
# CreateNewApp
############################


@router.post("/create", response_model=Optional[AppModel])
async def create_new_app(
    request: Request,
    form_data: AppForm,
    user=Depends(get_verified_user),
):
    if user.role != "admin" and not has_permission(
        user.id, "workspace.apps", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    app = Apps.get_app_by_id(form_data.id)
    if app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.MODEL_ID_TAKEN,
        )


    else:
        app = Apps.insert_new_app(form_data, user.id)
        if app:
            return app
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.DEFAULT(),
            )


############################
# ExportApps
############################


@router.get("/export", response_model=list[AppModel])
async def export_apps(request: Request, user=Depends(get_verified_user)):
    if user.role != "admin" and not has_permission(
        user.id, "workspace.models_export", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    if user.role == "admin" and BYPASS_ADMIN_ACCESS_CONTROL:
        return Apps.get_apps()
    else:
        return Apps.get_apps_by_user_id(user.id)


############################
# ImportApps
############################


class AppsImportForm(BaseModel):
    apps: list[dict]


@router.post("/import", response_model=bool)
async def import_apps(
    request: Request,
    user=Depends(get_verified_user),
    form_data: AppsImportForm = (...),
):
    if user.role != "admin" and not has_permission(
        user.id, "workspace.models_import", request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )
    try:
        data = form_data.apps
        if isinstance(data, list):
            for app_data in data:
                # Here, you can add logic to validate app_data if needed
                app_id = app_data.get("id")


                existing_app = Apps.get_app_by_id(app_id)
                if existing_app:
                    # Update existing app
                    app_data["meta"] = app_data.get("meta", {})
                    app_data["params"] = app_data.get("params", {})

                    updated_app = AppForm(
                        **{**existing_app.model_dump(), **app_data}
                    )
                    Apps.update_app_by_id(app_id, updated_app)
                else:
                    # Insert new app
                    app_data["meta"] = app_data.get("meta", {})
                    app_data["params"] = app_data.get("params", {})
                    new_app = AppForm(**app_data)
                    Apps.insert_new_app(new_app, user.id)
            return True
        else:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        log.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


###########################
# GetAppById
###########################
# GetAppById
###########################


class AppIdForm(BaseModel):
    id: str


# Note: We're not using the typical url path param here, but instead using a query parameter to allow '/' in the id
@router.get("/app", response_model=Optional[AppResponse])
async def get_app_by_id(id: str, user=Depends(get_verified_user)):
    app = Apps.get_app_by_id(id)
    if app:
        if (
            (user.role == "admin" and BYPASS_ADMIN_ACCESS_CONTROL)
            or app.user_id == user.id
            or has_access(user.id, "read", app.access_control)
        ):
            return app
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


###########################
# GetAppIconImage
###########################


@router.get("/app/icon/image")
async def get_app_icon_image(id: str, user=Depends(get_verified_user)):
    app = Apps.get_app_by_id(id)
    if app:
        if app.meta.icon_image_url:
            if app.meta.icon_image_url.startswith("http"):
                return Response(
                    status_code=status.HTTP_302_FOUND,
                    headers={"Location": app.meta.icon_image_url},
                )
            elif app.meta.icon_image_url.startswith("data:image"):
                try:
                    header, base64_data = app.meta.icon_image_url.split(",", 1)
                    image_data = base64.b64decode(base64_data)
                    image_buffer = io.BytesIO(image_data)

                    return StreamingResponse(
                        image_buffer,
                        media_type="image/png",
                        headers={"Content-Disposition": "inline; filename=image.png"},
                    )
                except Exception as e:
                    pass

        return FileResponse(f"{STATIC_DIR}/favicon.png")
    else:
        return FileResponse(f"{STATIC_DIR}/favicon.png")


############################
# ToggleAppById
############################


@router.post("/app/toggle", response_model=Optional[AppResponse])
async def toggle_app_by_id(id: str, user=Depends(get_verified_user)):
    app = Apps.get_app_by_id(id)
    if app:
        if (
            user.role == "admin"
            or app.user_id == user.id
            or has_access(user.id, "write", app.access_control)
        ):
            app = Apps.toggle_app_by_id(id)

            if app:
                return app
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=ERROR_MESSAGES.DEFAULT("Error updating app"),
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES.UNAUTHORIZED,
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )


############################
# UpdateAppById
############################


@router.post("/app/update", response_model=Optional[AppModel])
async def update_app_by_id(
    form_data: AppForm,
    user=Depends(get_verified_user),
):
    app = Apps.get_app_by_id(form_data.id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        app.user_id != user.id
        and not has_access(user.id, "write", app.access_control)
        and user.role != "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )

    app = Apps.update_app_by_id(form_data.id, AppForm(**form_data.model_dump()))
    return app


############################
# DeleteAppById
############################


@router.post("/app/delete", response_model=bool)
async def delete_app_by_id(form_data: AppIdForm, user=Depends(get_verified_user)):
    app = Apps.get_app_by_id(form_data.id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.NOT_FOUND,
        )

    if (
        user.role != "admin"
        and app.user_id != user.id
        and not has_access(user.id, "write", app.access_control)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES.UNAUTHORIZED,
        )

    result = Apps.delete_app_by_id(form_data.id)
    return result


@router.delete("/delete/all", response_model=bool)
async def delete_all_apps(user=Depends(get_admin_user)):
    result = Apps.delete_all_apps()
    return result
