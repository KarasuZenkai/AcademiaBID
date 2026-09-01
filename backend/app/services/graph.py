from typing import Any, Optional, Tuple

import httpx
import msal
from fastapi import HTTPException, status

from app.core.config import get_settings


class GraphService:
    """Small delegated Graph client used only for the live SharePoint proof."""

    graph_base_url = "https://graph.microsoft.com/v1.0"

    @staticmethod
    def _drive_item(item: dict[str, Any]) -> dict[str, Any]:
        mime_type = item.get("file", {}).get("mimeType", "")
        return {
            "id": item["id"],
            "name": item["name"],
            "is_folder": "folder" in item,
            "is_video": mime_type.startswith("video/"),
            "mime_type": mime_type,
            "duration_seconds": int(item.get("video", {}).get("duration", 0) / 1000) or None,
            "web_url": item.get("webUrl"),
        }

    def _graph_token(self, user_access_token: str) -> str:
        settings = get_settings()
        if not settings.azure_backend_client_secret:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="AZURE_BACKEND_CLIENT_SECRET is not configured")
        client = msal.ConfidentialClientApplication(
            settings.azure_backend_client_id,
            authority=f"https://login.microsoftonline.com/{settings.azure_tenant_id}",
            client_credential=settings.azure_backend_client_secret,
        )
        result = client.acquire_token_on_behalf_of(
            user_assertion=user_access_token,
            scopes=["https://graph.microsoft.com/Files.Read.All", "https://graph.microsoft.com/Sites.Read.All", "https://graph.microsoft.com/User.Read"],
        )
        token = result.get("access_token")
        if not token:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft Graph token exchange failed")
        return token

    def _get(self, path: str, user_access_token: str, follow_redirects: bool = True, graph_token: str = "") -> httpx.Response:
        response = httpx.get(
            f"{self.graph_base_url}{path}",
            headers={"Authorization": f"Bearer {graph_token or self._graph_token(user_access_token)}"},
            timeout=20,
            follow_redirects=follow_redirects,
        )
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail="Microsoft Graph rejected the SharePoint request")
        return response

    def inspect_site(self, user_access_token: str) -> dict[str, Any]:
        settings = get_settings()
        graph_token = self._graph_token(user_access_token)
        site = self._get(f"/sites/{settings.sharepoint_site_host}:{settings.sharepoint_site_path}", user_access_token, graph_token=graph_token).json()
        drives = self._get(f"/sites/{site['id']}/drives", user_access_token, graph_token=graph_token).json().get("value", [])
        result_drives = []
        for drive in drives:
            children = self._get(f"/drives/{drive['id']}/root/children?$select=id,name,folder,file,video,webUrl", user_access_token, graph_token=graph_token).json().get("value", [])
            result_drives.append({
                "id": drive["id"],
                "name": drive["name"],
                "items": [self._drive_item(item) for item in children],
            })
        return {"site": {"id": site["id"], "name": site.get("displayName"), "web_url": site.get("webUrl")}, "drives": result_drives}

    def list_children(self, drive_id: str, item_id: str, user_access_token: str) -> list[dict[str, Any]]:
        items = self._get(
            f"/drives/{drive_id}/items/{item_id}/children?$select=id,name,folder,file,video,webUrl",
            user_access_token,
        ).json().get("value", [])
        return [self._drive_item(item) for item in items]

    def playback_url(self, drive_id: str, item_id: str, user_access_token: str) -> str:
        response = self._get(f"/drives/{drive_id}/items/{item_id}/content", user_access_token, follow_redirects=False)
        location = response.headers.get("location")
        if not location:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft Graph did not return a playback URL")
        return location

    def download_file(self, drive_id: str, item_id: str, user_access_token: str) -> Tuple[bytes, str]:
        response = self._get(f"/drives/{drive_id}/items/{item_id}/content", user_access_token)
        return response.content, response.headers.get("content-type", "application/octet-stream")

    def profile_photo(self, user_access_token: str) -> Optional[Tuple[bytes, str]]:
        response = httpx.get(
            f"{self.graph_base_url}/me/photos/120x120/$value",
            headers={"Authorization": f"Bearer {self._graph_token(user_access_token)}"},
            timeout=20,
            follow_redirects=True,
        )
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft Graph rejected the profile photo request")
        return response.content, response.headers.get("content-type", "image/jpeg")

    def profile_details(self, user_access_token: str) -> dict[str, Optional[str]]:
        profile = self._get("/me?$select=jobTitle,companyName", user_access_token).json()
        return {"job_title": profile.get("jobTitle"), "company_name": profile.get("companyName")}

    def thumbnail(self, drive_id: str, item_id: str, user_access_token: str) -> Optional[Tuple[bytes, str]]:
        response = httpx.get(
            f"{self.graph_base_url}/drives/{drive_id}/items/{item_id}/thumbnails/0/medium/content",
            headers={"Authorization": f"Bearer {self._graph_token(user_access_token)}"},
            timeout=20,
            follow_redirects=True,
        )
        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Microsoft Graph rejected the thumbnail request")
        return response.content, response.headers.get("content-type", "image/jpeg")
