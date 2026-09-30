# mvm FastMCP + FastAPI server
# ---------------------------------------------------------------------------
# Note: Hypervisors (VirtualBox, VMware, UTM, Hyper-V) run on the *host*.
# This image only runs the MCP/REST control plane. To manage real VMs you
# typically need --privileged + host binary/socket mounts, or run the server
# natively on the host. See README for details.
# ---------------------------------------------------------------------------

FROM python:3.12-slim-bookworm AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps (git for optional mvm clone; curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
COPY models.py core.py mcp_tools.py rest_api.py main.py ./

# Optional: bake a copy of mvm into the image (override with volume in compose)
ARG MVM_REPO=https://github.com/clockworksspheres/mvm.git
ARG MVM_REF=main
RUN git clone --depth 1 --branch "${MVM_REF}" "${MVM_REPO}" /opt/mvm \
    && echo "/opt/mvm/src" > /app/mvm.pth \
    || echo "WARNING: could not clone mvm; mount it at runtime"

ENV PYTHONPATH=/opt/mvm/src:/app

# Non-root user
RUN useradd --create-home --shell /bin/bash mvm \
    && chown -R mvm:mvm /app /opt/mvm
USER mvm

EXPOSE 8000

# Default: REST API (HTTP). Override CMD for MCP stdio / HTTP.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/health || exit 1

ENTRYPOINT ["python", "main.py"]
CMD ["--mode", "rest", "--host", "0.0.0.0", "--port", "8000"]
