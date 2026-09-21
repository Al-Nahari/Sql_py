"""
Loads config.yaml once and exposes it as a plain dictionary.

Keeping this in its own module means every other module asks for
settings instead of hard-coding paths or thresholds, so the pipeline
can be repointed at new files/servers by editing config.yaml only.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict

import yaml

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")


@lru_cache(maxsize=1)
def load_config() -> Dict[str, Any]:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def resolve_path(relative_path: str) -> str:
    """Turn a path from config.yaml into an absolute path from the project root."""
    return os.path.join(PROJECT_ROOT, relative_path)
