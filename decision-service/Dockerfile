FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY ./app .

EXPOSE 8083
