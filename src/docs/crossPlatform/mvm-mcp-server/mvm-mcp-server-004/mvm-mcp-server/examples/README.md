# Examples

## MCP client (`mcp_client.py`)

Minimal [FastMCP](https://gofastmcp.com/) client that talks to this server over **stdio** or **HTTP**.

### Stdio (client starts the server)

```bash
# From the project root
python examples/mcp_client.py --list-only

python examples/mcp_client.py --hypervisor virtualbox

python examples/mcp_client.py \
  --hypervisor virtualbox \
  --vm "DevBox" \
  --start --headless --ip
```

### HTTP (server already running)

Terminal 1:

```bash
python main.py --mode mcp --transport http --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
python examples/mcp_client.py --http http://127.0.0.1:8000/mcp --list-only
python examples/mcp_client.py --http http://127.0.0.1:8000/mcp --hypervisor virtualbox
```

### What it does

1. Connects and prints discovered tools  
2. Calls `list_vms` for the chosen hypervisor  
3. Optionally `get_vm_status` / `start_vm` / `get_vm_ip` when `--vm` is set  

Real VM operations still need the upstream **mvm** package on `PYTHONPATH` and a running hypervisor process.
