
# mvm-mcp-server

##### Grok generated documentation:

---
# I need a fastmcp server for for [https://github.com/clockworksspheres/mvm](https://github.com/clockworksspheres/mvm)

Here’s a ready-to-use **FastMCP server** that wraps [clockworksspheres/mvm](https://github.com/clockworksspheres/mvm).

### What it does
Exposes these MCP tools so an LLM can drive your local VMs:

| Tool | Purpose |
|------|---------|
| `list_vms` | List VMs + state (+ IP when available) |
| `start_vm` | Power-on (`headless` optional) |
| `stop_vm` | Shut down / power-off |
| `pause_vm` | Suspend / save state |
| `unpause_vm` | Resume |
| `reset_vm` | Soft or hard reset |
| `get_vm_status` | `running` / `suspended` / `off` |
| `get_vm_ip` | Guest IP (needs guest tools) |

Supported hypervisors: **vmware**, **virtualbox**, **utm**, **hyperv** (same set as upstream mvm).

### Files created
```
mvm-mcp-server/
├── mvm_mcp_server.py   # the FastMCP server
├── requirements.txt
└── README.md
```

### Quick start
```bash
# 1. Get mvm itself
git clone https://github.com/clockworksspheres/mvm.git
export PYTHONPATH="/path/to/mvm/src:$PYTHONPATH"

# 2. Install FastMCP
cd mvm-mcp-server
pip install -r requirements.txt

# 3. Run (stdio – works with Claude Desktop, Cursor, etc.)
python mvm_mcp_server.py
```

### Claude Desktop / Cursor snippet
```json
{
  "mcpServers": {
    "mvm": {
      "command": "python",
      "args": ["/absolute/path/to/mvm_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mvm/src"
      }
    }
  }
}
```

The hypervisor process must already be running on the host (mvm checks for it). The server is intentionally thin and delegates all real work to the upstream `ManageVirtualMachines` factory.

# can you add fastapi and pydantic?

Done. The server now uses **FastAPI** and **Pydantic** alongside FastMCP.

### What changed

**Pydantic models** (request/response validation):
- `Hypervisor` enum
- `VmIdentifier`, `StartVmRequest`, `ResetVmRequest`
- `ActionResult`, `StatusResult`, `IpResult`, `ListResult`

**FastAPI REST API** (same operations as the MCP tools):
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness |
| `GET` | `/vms` | List VMs |
| `POST` | `/vms/start` | Start |
| `POST` | `/vms/stop` | Stop |
| `POST` | `/vms/pause` | Pause |
| `POST` | `/vms/unpause` | Resume |
| `POST` | `/vms/reset` | Reset |
| `GET` | `/vms/status` | Status |
| `GET` | `/vms/ip` | Guest IP |

**Shared core** – MCP tools and REST routes both call the same `do_*` helpers, so behaviour stays consistent.

### Run modes

```bash
# MCP for Claude / Cursor (stdio)
python mvm_mcp_server.py

# Pure REST + interactive OpenAPI docs at /docs
python mvm_mcp_server.py --mode rest --port 8000

# MCP over HTTP
python mvm_mcp_server.py --mode mcp --transport http --port 8000
```

### Dependencies added

```
fastapi>=0.115.0
pydantic>=2.0.0
uvicorn[standard]>=0.30.0
```

# can this work with qwen llms?

**Yes.** Your mvm FastMCP server works with Qwen LLMs. MCP is model-agnostic; Qwen has solid first-party support.

### How it works with Qwen

| Path | What it is | How to connect this server |
|------|------------|----------------------------|
| **Qwen Code** | Official CLI / agent (like Claude Code) | Native MCP client – stdio, HTTP, SSE |
| **Qwen-Agent** | Official Python agent framework | `pip install "qwen-agent[mcp]"` + `mcpServers` config |
| **DashScope / Model Studio** | Cloud Qwen API | Responses API can attach MCP servers (SSE) |
| **Local Qwen** (Ollama, vLLM, Unsloth, LM Studio) | Self-hosted models | Use an MCP-aware client or Qwen-Agent in front of the model |

Qwen3 / Qwen3.5 / Qwen3.6 models are trained for tool use and work well with MCP-style tool calling.

### Quick setup options

**1. Qwen Code (easiest for interactive use)**

```bash
# stdio (local process)
qwen mcp add mvm --transport stdio -- \
  python /absolute/path/to/mvm_mcp_server.py

# or HTTP
python mvm_mcp_server.py --mode mcp --transport http --port 8000
qwen mcp add --transport http mvm http://127.0.0.1:8000/mcp
```

Or put this in `~/.qwen/settings.json`:

```json
{
  "mcpServers": {
    "mvm": {
      "command": "python",
      "args": ["/absolute/path/to/mvm_mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/mvm/src"
      }
    }
  }
}
```

**2. Qwen-Agent (Python)**

```python
from qwen_agent.agents import Assistant

llm_cfg = {
    "model": "qwen3-max",          # or a local endpoint
    "model_type": "qwen_dashscope",
    # "model_server": "http://localhost:8000/v1",  # for local vLLM/Ollama
}

mcp_config = {
    "mcpServers": {
        "mvm": {
            "command": "python",
            "args": ["/absolute/path/to/mvm_mcp_server.py"],
            "env": {"PYTHONPATH": "/absolute/path/to/mvm/src"},
        }
    }
}

agent = Assistant(
    llm=llm_cfg,
    function_list=[mcp_config],
    system_message="You can manage local VMs via the mvm tools.",
)
```

**3. REST only (any Qwen that can call HTTP tools)**

```bash
python mvm_mcp_server.py --mode rest --port 8000
```

Then point any tool-calling setup (including custom function-calling prompts) at the OpenAPI endpoints under `/docs`.

### Practical tips

- Prefer **stdio** for local Qwen Code / Qwen-Agent; use **HTTP** when the model runs remotely or in a container.
- Keep the hypervisor process running before the model tries to call tools.
- Smaller local Qwen models (7B–32B) can use the tools; larger ones (Qwen3-Max / 235B-class) are more reliable on multi-step “list → start → status → ip” flows.

So: same server, no code changes required — just register it with Qwen Code, Qwen-Agent, or any other MCP client that sits in front of a Qwen model.

# can you zip up the server for me so I can download it?

Here's the zip: (mvm-mcp-server-01)

****

Contents:
- `mvm_mcp_server.py` — FastMCP + FastAPI server
- `requirements.txt` — dependencies
- `README.md` — setup & usage

After download:

```bash
unzip mvm-mcp-server.zip
cd mvm-mcp-server
pip install -r requirements.txt
# set PYTHONPATH to your mvm src, then:
python mvm_mcp_server.py
```

# can you put the different sections in different files? and zip it up for me again?

Split into separate modules and re-zipped: (mvm-mcp-server-02)

****

```
mvm-mcp-server/
├── models.py        # Pydantic request/response models
├── core.py          # mvm path setup + shared do_* logic
├── mcp_tools.py     # FastMCP server + tools
├── rest_api.py      # FastAPI app + REST routes
├── main.py          # CLI entry point
├── requirements.txt
└── README.md
```

Run with:

```bash
unzip mvm-mcp-server.zip
cd mvm-mcp-server
pip install -r requirements.txt
python main.py
```

# Add Docker Support

Docker support is in place. Updated zip: (mvm-mcp-server-03)

****

### New files

| File | Purpose |
|------|---------|
| `Dockerfile` | Python 3.12 image, clones mvm, runs as non-root |
| `docker-compose.yml` | One-command REST stack on `:8000` |
| `.dockerignore` | Keeps the build context clean |

### Quick use

```bash
# REST API + OpenAPI docs
docker compose up --build
# → http://127.0.0.1:8000/docs

# MCP over HTTP
docker compose run --rm -p 8000:8000 mvm-mcp \
  --mode mcp --transport http --host 0.0.0.0 --port 8000
```

**Note:** The container is the control plane only. Hypervisors still run on the host. For full start/stop of real VMs, prefer a native install on the same machine; Docker is ideal for remote clients, CI, or API development.