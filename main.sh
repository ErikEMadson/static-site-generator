#!/usr/bin/env bash
(
    source .venv/bin/activate &&
        uv run src/main.py static-site-generator docs &&
        uv run -m http.server 8888
)
