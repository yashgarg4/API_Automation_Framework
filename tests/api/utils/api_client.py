import requests
from typing import Dict, Any


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def get(self, path: str, headers: Dict[str, str] | None = None, params: Dict[str, Any] | None = None):
        return requests.get(self._url(path), headers=headers, params=params)

    def post(self, path: str, json: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None, data=None):
        return requests.post(self._url(path), json=json, headers=headers, data=data)

    def put(self, path: str, json: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None):
        return requests.put(self._url(path), json=json, headers=headers)

    def patch(self, path: str, json: Dict[str, Any] | None = None, headers: Dict[str, str] | None = None):
        return requests.patch(self._url(path), json=json, headers=headers)

    def delete(self, path: str, headers: Dict[str, str] | None = None):
        return requests.delete(self._url(path), headers=headers)
