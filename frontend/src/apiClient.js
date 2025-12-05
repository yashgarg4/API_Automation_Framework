const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const resp = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const text = await resp.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!resp.ok) {
    const error = new Error(
      data && data.detail ? data.detail : `Request failed: ${resp.status}`
    );
    error.status = resp.status;
    error.data = data;
    throw error;
  }

  return data;
}

export function apiGet(path, options = {}) {
  return request(path, { ...options, method: "GET" });
}

export function apiPost(path, body, options = {}) {
  return request(path, {
    ...options,
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function apiPut(path, body, options = {}) {
  return request(path, {
    ...options,
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function apiPatch(path, body, options = {}) {
  return request(path, {
    ...options,
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function apiDelete(path, options = {}) {
  return request(path, { ...options, method: "DELETE" });
}
