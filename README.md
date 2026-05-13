radkit-llm mcp-server --auto-approve --sandbox subprocess --service-config service.config.direct --profile mcp-profile.py --prompt prompt.txt 
uv venv -p 3.13 
source .venv/bin/activate


uv run --no-sync radkit-llm mcp-server \
  --port 8082 \
  --sandbox subprocess \
  --service-config service.config.direct \
  --profile radkit-mcp-profile.py \
  --prompt radkit-mcp-prompt.txt \
  --auto-approve \
  --mcp-log-dir logs/

For LibreChat deployments, keep auto-approval enabled. LibreChat's MCP client does not complete RADKit's approval elicitation flow, so disabling auto-approval causes tool calls like inventory refresh to stall and eventually time out.
