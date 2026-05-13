# RADKit NetOps Agent

A network operations agent powered by Cisco RADKit and MCP (Model Context Protocol).

## Quick Start

```bash
# Create and activate virtual environment
uv venv -p 3.13
source .venv/bin/activate
```

### Run the MCP Server (eval-based, recommended)

```bash
# --sandbox subprocess  : simple sandbox; use bubblewrap on Linux for isolation
# --service-config      : direct connection config (see service.config.direct.example)
# --auto-approve        : required for LibreChat (no elicitation support)
# --mcp-log-dir         : session logs written here
uv run --no-sync radkit-llm mcp-server \
  --port 8082 \
  --sandbox subprocess \
  --service-config service.config.direct \
  --profile radkit-mcp-profile.py \
  --prompt radkit-mcp-prompt.txt \
  --auto-approve \
  --mcp-log-dir logs/
```

> **LibreChat note:** Keep `--auto-approve` enabled. LibreChat's MCP client does not complete RADKit's approval elicitation flow, so disabling auto-approval causes tool calls like inventory refresh to stall and eventually time out.

---

## `radkit-llm mcp-server` — Parameter Reference

> Version discovered from: `cisco_radkit_llm 2.0.0a1` (installed in `.venv`)

| Parameter | Type | Required | Options / Default | Description |
|---|---|---|---|---|
| `--port` | integer | No | any port (e.g. `8082`) | TCP port the MCP server listens on |
| `--sandbox` | choice | **Yes** | `subprocess` \| `bubblewrap` | `subprocess` — simple, cross-platform, no isolation. `bubblewrap` — Linux-only, network- and filesystem-isolated sandbox. |
| `--service-config` | path | No | — | Path to a JSON service connection config. Omit to allow the MCP client to connect to any service interactively (elicitation flow). |
| `--auto-approve` | flag | No | off by default | Automatically approve every RADKit interaction. **Required for LibreChat** — its MCP client cannot complete the elicitation flow. |
| `--profile` | file | No | — | Python script executed at sandbox startup (like `~/.radkit/client/profile.py`). Use to pre-configure devices, credentials, etc. |
| `--prompt` | file | No | — | Text/Markdown file whose content is **appended** to the built-in LLM system prompt. |
| `--override-prompt` | file | No | — | Text/Markdown file that **replaces** the entire LLM system prompt (overrides `--prompt` and all built-in content). |
| `--mcp-log-dir` | directory | No | logging disabled | Directory where MCP session logs (`.log.md` files) are written. |

### `--service-config` connection types

The JSON file passed to `--service-config` supports four connection types (`radkit-llm example-service-config`):

| `type` | `method` | Auth mechanism | Notes |
|---|---|---|---|
| `direct` | — | username + password (base64) | Connects directly to a local RADKit service (`host`:`rpc_port`) |
| `cloud` | `api_key` | Encrypted access token file | Token stored in `access_token_path`; passphrase via `prompt` or keyring |
| `cloud` | `certificate` | Client certificate | Certificate must already be provisioned |
| `cloud` | `sso` | Single Sign-On (browser) | Browser-based SSO flow |

### Other `radkit-llm` commands

| Command | Purpose | Key differences vs `mcp-server` |
|---|---|---|
| `mcp-server` | Eval-based MCP server | Agent reasoning loop; supports `--prompt`, `--override-prompt`, `--profile` |
| `simple-mcp-server` | Non-eval MCP server | No agent loop; requires `--service-config`; no sandbox/profile/prompt options |
| `chat` | Stand-alone CLI agent | Adds `--model`, `--api` (`aws-bedrock`\|`openai`), `--max-tokens`, AWS Bedrock options |
