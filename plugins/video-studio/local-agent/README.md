# Video Studio local connection

This helper opens Studio for approval, stores the resulting personal credential in your operating system credential store, and supplies it to the remote MCP service. Tokens do not pass through chat, command arguments, environment variables, or configuration files.

Use Python 3.9 or newer. Install the helper dependency from the public PyPI registry into a dedicated environment:

```text
python -m venv /absolute/path/to/video-studio-agent-env
/absolute/path/to/video-studio-agent-env/bin/python -m pip install -r /absolute/path/to/local-agent/requirements.txt
```

On Windows, use the environment's `Scripts\python.exe` instead of `bin/python`. Keep the environment outside plugin cache folders so plugin updates do not remove it.

Run with that environment's interpreter:

```text
python /absolute/path/to/local-agent/helper.py connect
```

Compare the displayed code with Studio's browser approval page, then approve with your own Studio account. The helper waits up to ten minutes. If approval expires or delivery is interrupted, start a fresh connection. The service releases a token once; it cannot be recovered from an expired request.

Supported credential stores are Windows Credential Manager, macOS Keychain, and supported Linux Secret Service, KWallet, or libsecret backends. An unlocked OS store must be available in the same user session as the agent. Plaintext files, null stores, and generic fallback backends are rejected. This helper never installs packages automatically and never falls back to token files or environment variables.

Configure Codex using the actual absolute interpreter and helper paths, preserving unrelated settings:

```toml
[mcp_servers.video_studio]
command = "/absolute/path/to/video-studio-agent-env/bin/python"
args = ["/absolute/path/to/local-agent/helper.py", "serve"]
```

For Windows TOML, use literal strings for paths, for example `command = 'C:\Users\Example\video-studio-agent-env\Scripts\python.exe'`. Do not configure an HTTP URL or bearer environment variable on this stdio entry. The helper supplies the credential securely on each HTTPS request to the fixed Studio service.

`helper.py status` reports only whether a credential is saved. `helper.py disconnect` removes the local copy. Revoke the connection in Studio to disable all copies immediately. Successful agent use retains the existing rolling renewal policy. The helper reads its credential for each request, so reconnecting does not require replacing a token in MCP configuration.

The helper's stdout is reserved for MCP JSON when running `serve`. Browser approval notices go to stderr. It does not play, download, edit, upload, or publish a video during connection setup.
