import { WEBUI_API_BASE_URL } from '$lib/constants';

export const getAppItems = async (
    token: string = '',
    query?: string,
    viewOption?: string,
    selectedTag?: string,
    orderBy?: string,
    direction?: string,
    page?: number
) => {
    let error = null;

    const searchParams = new URLSearchParams();
    if (query) {
        searchParams.append('query', query);
    }
    if (viewOption) {
        searchParams.append('view_option', viewOption);
    }
    if (selectedTag) {
        searchParams.append('tag', selectedTag);
    }
    if (orderBy) {
        searchParams.append('order_by', orderBy);
    }
    if (direction) {
        searchParams.append('direction', direction);
    }
    if (page) {
        searchParams.append('page', page.toString());
    }

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/list?${searchParams.toString()}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;
            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getAppTags = async (token: string = '') => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/tags`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;
            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const createNewApp = async (token: string, app: object) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/create`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        },
        body: JSON.stringify(app)
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err.detail;
            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const exportApps = async (token: string = '') => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/export`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;
            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const importApps = async (token: string, apps: object[]) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/import`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ apps: apps })
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .catch((err) => {
            error = err;
            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getAppById = async (token: string, id: string) => {
    let error = null;

    const searchParams = new URLSearchParams();
    searchParams.append('id', id);

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/app?${searchParams.toString()}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;

            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const getAppIconImageUrl = (id: string) => {
    return `${WEBUI_API_BASE_URL}/apps/app/icon/image?id=${id}`;
};

export const toggleAppById = async (token: string, id: string) => {
    let error = null;

    const searchParams = new URLSearchParams();
    searchParams.append('id', id);

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/app/toggle?${searchParams.toString()}`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;

            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const updateAppById = async (token: string, id: string, app: object) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/app/update`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ ...app, id })
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;

            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const deleteAppById = async (token: string, id: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/app/delete`, {
        method: 'POST',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ id })
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err.detail;

            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};

export const deleteAllApps = async (token: string) => {
    let error = null;

    const res = await fetch(`${WEBUI_API_BASE_URL}/apps/delete/all`, {
        method: 'DELETE',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
            authorization: `Bearer ${token}`
        }
    })
        .then(async (res) => {
            if (!res.ok) throw await res.json();
            return res.json();
        })
        .then((json) => {
            return json;
        })
        .catch((err) => {
            error = err;

            console.error(err);
            return null;
        });

    if (error) {
        throw error;
    }

    return res;
};
