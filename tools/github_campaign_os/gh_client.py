import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional


class GitHubError(RuntimeError):
    pass


class GitHubClient:
    def __init__(self, token: Optional[str] = None, api_url: str = "https://api.github.com"):
        self._token = token or os.environ.get("GH_TOKEN")
        if not self._token:
            raise GitHubError("GH_TOKEN is required")
        self.api_url = api_url.rstrip("/")

    def request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Any:
        url = path if path.startswith("https://") else self.api_url + path
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("Authorization", f"Bearer {self._token}")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        if data is not None:
            request.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            safe = exc.read().decode("utf-8", errors="replace")[:500]
            raise GitHubError(f"GitHub API {method} {urllib.parse.urlparse(url).path} failed with {exc.code}: {safe}") from None

    def paginate(self, path: str) -> List[Any]:
        items: List[Any] = []
        separator = "&" if "?" in path else "?"
        page = 1
        while True:
            batch = self.request("GET", f"{path}{separator}per_page=100&page={page}")
            if not isinstance(batch, list):
                raise GitHubError("paginated GitHub response was not a list")
            items.extend(batch)
            if len(batch) < 100:
                return items
            page += 1

    def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        response = self.request("POST", "/graphql", {"query": query, "variables": variables or {}})
        if response.get("errors"):
            raise GitHubError("GitHub GraphQL failed: " + json.dumps(response["errors"], ensure_ascii=False)[:500])
        return response["data"]
