import pytest

from fabric_sre.auth import NotebookCredential


class StubCredentials:
    def __init__(self) -> None:
        self.audiences: list[str] = []

    def getToken(self, audience: str) -> str:
        self.audiences.append(audience)
        return "test-token"


@pytest.mark.parametrize(
    "scope",
    [
        "https://api.fabric.microsoft.com/.default",
        "https://api.powerbi.com/.default",
        "https://analysis.windows.net/powerbi/api/.default",
    ],
)
def test_notebook_credential_maps_power_bi_audiences(scope: str) -> None:
    utility = StubCredentials()
    credential = NotebookCredential(utility)

    token = credential.get_token(scope)

    assert token.token == "test-token"
    assert utility.audiences == ["pbi"]


def test_notebook_credential_rejects_unsupported_arm_audience() -> None:
    credential = NotebookCredential(StubCredentials())

    with pytest.raises(ValueError, match="does not support token audience"):
        credential.get_token("https://management.azure.com/.default")
