# mvm FastMCP + FastAPI Server

A dual-interface server for [clockworksspheres/mvm](https://github.com/clockworksspheres/mvm):

| Interface | Use case |
|-----------|----------|
| **MCP tools** (FastMCP) | LLMs – Claude Desktop, Cursor, Qwen Code, etc. |
| **REST API** (FastAPI + Pydantic) | Scripts, CI, browsers – full OpenAPI at `/docs` |

Supported hypervisors: VMware Fusion/Workstation, VirtualBox, UTM (macOS), Hyper-V (Windows).

## Layout

```
mvm-mcp-server/
├── models.py        # Pydantic request/response models
├── core.py          # mvm path setup + shared do_* business logic
├── mcp_tools.py     # FastMCP server + tool definitions
├── rest_api.py      # FastAPI app + REST routes
├── main.py          # CLI entry point
├── requirements.txt
└── README.md
```

## Prerequisites

1. **Python 3.10+**
2. **mvm** on `PYTHONPATH` (or installed editable):

   ```bash
   git clone https://github.com/clockworksspheres/mvm.git
   export PYTHONPATH="/path/to/mvm/src:$PYTHONPATH"
   ```

3. The target hypervisor process must already be **running**.
4. Guest tools are required for reliable IP retrieval.

## Install

```bash
cd mvm-mcp-server
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

### MCP (stdio – recommended for Claude / Cursor / Qwen Code)

```bash
python main.py
# or
python main.py --mode mcp --transport stdio
```

### MCP over HTTP

```bash
python main.py --mode mcp --transport http --port 8000
```

### Pure FastAPI REST API

```bash
python main.py --mode rest --port 8000
# OpenAPI interactive docs → http://127.0.0.1:8000/docs
```

## Claude Desktop / Cursor config

```json
{
  "mcpServers": {
    "mvm": {
      "command": "python",
      "args": ["/absolute/path/to/main.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mvm/src"
      }
    }
  }
}
```

## Qwen Code

```bash
qwen mcp add mvm --transport stdio -- python /absolute/path/to/main.py
```

Or in `~/.qwen/settings.json`:

```json
{
  "mcpServers": {
    "mvm": {
      "command": "python",
      "args": ["/absolute/path/to/main.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mvm/src"
      }
    }
  }
}
```

## REST endpoints

| Method | Path | Body / query | Description |
|--------|------|--------------|-------------|
| `GET` | `/health` | – | Liveness |
| `GET` | `/vms?hypervisor=` | query | List VMs |
| `POST` | `/vms/start` | `StartVmRequest` | Power-on |
| `POST` | `/vms/stop` | `VmIdentifier` | Shut down |
| `POST` | `/vms/pause` | `VmIdentifier` | Suspend |
| `POST` | `/vms/unpause` | `VmIdentifier` | Resume |
| `POST` | `/vms/reset` | `ResetVmRequest` | Soft/hard reset |
| `GET` | `/vms/status` | `hypervisor`, `vm` | Power state |
| `GET` | `/vms/ip` | `hypervisor`, `vm` | Guest IP |

### Example (curl)

```bash
curl "http://127.0.0.1:8000/vms?hypervisor=virtualbox"

curl -X POST http://127.0.0.1:8000/vms/start \
  -H "Content-Type: application/json" \
  -d '{"hypervisor":"virtualbox","vm":"Win11-Test","headless":true}'

curl "http://127.0.0.1:8000/vms/status?hypervisor=virtualbox&vm=Win11-Test"
```

## MCP tools

`list_vms`, `start_vm`, `stop_vm`, `pause_vm`, `unpause_vm`, `reset_vm`,
`get_vm_status`, `get_vm_ip`

## Notes

- Business logic lives in `core.py` and is shared by MCP tools and REST routes.
- The hypervisor application must be running before calls succeed.
- Intended for local, trusted use – no auth is implemented.
