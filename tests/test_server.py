import subprocess
import sys

import server


def test_redact_secrets_masks_nested_keys():
    data = [{"ssid": "a", "preSharedKey": "hunter2", "nested": {"passphrase": "x"}}]
    out = server.redact_secrets(data)
    assert out[0]["preSharedKey"] == "***REDACTED***"
    assert out[0]["nested"]["passphrase"] == "***REDACTED***"
    assert out[0]["ssid"] == "a"
    assert data[0]["preSharedKey"] == "hunter2"


def test_redact_secrets_leaves_empty_keys_alone():
    assert server.redact_secrets({"preSharedKey": ""}) == {"preSharedKey": ""}


def test_http_transport_requires_token():
    result = subprocess.run(
        [sys.executable, "server.py"],
        # An empty value stops load_dotenv from filling the token in from a local .env
        env={"MCP_TRANSPORT": "streamable-http", "MCP_AUTH_TOKEN": "", "PATH": ""},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0
    assert "MCP_AUTH_TOKEN" in result.stderr
