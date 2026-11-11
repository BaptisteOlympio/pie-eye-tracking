FROM bolympio/openface:latest

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --python /usr/bin/python3

RUN mkdir /opt/pyopenface \
 && cp /usr/lib/python3/dist-packages/pyopenface*.so /opt/pyopenface/ \
 && echo "/opt/pyopenface" > /app/.venv/lib/python3.8/site-packages/pyopenface.pth

COPY ./app .

EXPOSE 8081


