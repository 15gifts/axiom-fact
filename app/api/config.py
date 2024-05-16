import os
import socket
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings

USE_CACHED_SETTINGS = os.getenv("USE_CACHED_SETTINGS", "true").lower() == "true"


class Settings(BaseSettings):
    placeholder: str = "This is a placeholder setting."
    hostname: str = socket.gethostname()
    model_name: Literal["roberta-base"] = "roberta-base"
    path_to_model_checkpoint: str = "models/AlignScore-base.ckpt"
    device: str = "cpu"


@lru_cache
def get_cached_settings():
    """Utilising the cache if needed."""
    # https://github.com/pydantic/pydantic/issues/3753#issuecomment-1087417884
    return Settings()  # pyright:ignore


def get_settings():
    """
    Will use the cached settings unless _use_cached_settings is False.
    """
    if USE_CACHED_SETTINGS:
        settings = get_cached_settings()
    else:
        settings = Settings()  # pyright:ignore
    return settings
