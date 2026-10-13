from __future__ import annotations

import random
import time
from collections.abc import Iterator
from email.utils import parsedate_to_datetime
from typing import Any

import requests
from azure.core.credentials import TokenCredential


class ApiError(RuntimeError):
    """Raised when an API request cannot be completed safely."""


class RestClient:
    def __init__(
        self,
        credential: TokenCredential,
        scope: str,
        *,
        timeout_seconds: int = 60,
        max_attempts: int = 6,
        session: requests.Session | None = None,
    ) -> None:
        self.credential = credential
        self.scope = scope
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts
        self.session = session or requests.Session()

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        headers = dict(kwargs.pop("headers", {}))
        headers["Authorization"] = f"Bearer {self.credential.get_token(self.scope).token}"
        headers.setdefault("Accept", "application/json")

        for attempt in range(1, self.max_attempts + 1):
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout_seconds,
                **kwargs,
            )
            if response.status_code < 400:
                return response
            if response.status_code not in {408, 429, 500, 502, 503, 504}:
                raise ApiError(
                    f"{method} {url} failed with {response.status_code}: {response.text[:2000]}"
                )
            if attempt == self.max_attempts:
                raise ApiError(
                    f"{method} {url} exhausted {self.max_attempts} attempts; "
                    f"last status {response.status_code}: {response.text[:2000]}"
                )
            time.sleep(self._retry_delay_seconds(response, attempt))
        raise AssertionError("Retry loop terminated unexpectedly")

    def get_json(self, url: str, **kwargs: Any) -> dict[str, Any]:
        response = self.request("GET", url, **kwargs)
        payload = response.json()
        if not isinstance(payload, dict):
            raise ApiError(f"Expected an object response from {url}")
        return payload

    def paginate(
        self,
        url: str,
        *,
        items_key: str = "value",
        next_link_keys: tuple[str, ...] = ("continuationUri", "@odata.nextLink", "nextLink"),
        **kwargs: Any,
    ) -> Iterator[dict[str, Any]]:
        next_url: str | None = url
        while next_url:
            payload = self.get_json(next_url, **kwargs)
            items = payload.get(items_key, [])
            if not isinstance(items, list):
                raise ApiError(f"Expected '{items_key}' to be a list in response from {next_url}")
            for item in items:
                if isinstance(item, dict):
                    yield item
            next_url = next(
                (
                    value
                    for key in next_link_keys
                    if isinstance((value := payload.get(key)), str) and value
                ),
                None,
            )

    @staticmethod
    def _retry_delay_seconds(response: requests.Response, attempt: int) -> float:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            if retry_after.isdigit():
                return min(float(retry_after), 120.0)
            try:
                return min(
                    max((parsedate_to_datetime(retry_after).timestamp() - time.time()), 0.0),
                    120.0,
                )
            except (TypeError, ValueError):
                pass
        return min((2 ** (attempt - 1)) + random.random(), 60.0)

