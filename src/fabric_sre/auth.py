from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from azure.core.credentials import AccessToken, TokenCredential
from azure.identity import DefaultAzureCredential


class NotebookCredential(TokenCredential):
    def __init__(self, credentials_utility: Any) -> None:
        self._credentials_utility = credentials_utility

    def get_token(self, *scopes: str, **kwargs: Any) -> AccessToken:
        if len(scopes) != 1:
            raise ValueError("Fabric notebook credentials require exactly one token scope.")
        resource = scopes[0].removesuffix("/.default")
        if resource in {
            "https://api.fabric.microsoft.com",
            "https://api.powerbi.com",
            "https://analysis.windows.net/powerbi/api",
        }:
            audience = "pbi"
        elif resource == "https://storage.azure.com":
            audience = "storage"
        elif resource == "https://vault.azure.net":
            audience = "keyvault"
        else:
            raise ValueError(
                f"Fabric NotebookUtils does not support token audience '{resource}'."
            )
        token = self._credentials_utility.getToken(audience)
        expires_on = int(datetime.now(UTC).timestamp()) + 3600
        return AccessToken(token, expires_on)


def get_credential() -> TokenCredential:
    try:
        from notebookutils import credentials
    except ImportError:
        return DefaultAzureCredential()
    return NotebookCredential(credentials)
