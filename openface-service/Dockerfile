# Inspired from https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile
# And https://github.com/philippschmalen/devcontainer-python-uv-template/blob/main/Dockerfile

FROM bolympio/openface:latest

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# This is actually very important
# The problem I had : The Dockerfile specify that uv should install .venv under /app
# But then the devcontainer mount the host repo under /app overwritting .venv
# Now .venv lives outside of /app, no overwritting possible
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project --frozen

COPY pyproject.toml uv.lock ./

COPY src src

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

RUN mkdir /opt/pyopenface \
    && cp /usr/lib/python3/dist-packages/pyopenface*.so /opt/pyopenface/ \
    && echo "/opt/pyopenface" > ${UV_PROJECT_ENVIRONMENT}/lib/python3.8/site-packages/pyopenface.pth

EXPOSE 8081


