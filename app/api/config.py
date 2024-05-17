import os
import socket
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    placeholder: str = "This is a placeholder setting."
    hostname: str = socket.gethostname()
    bert_model_name: Literal["roberta-base"] = "roberta-base"
    path_to_model_checkpoint: str = os.path.join(
        str(Path(__file__).resolve().parent.parent.parent),
        "models",
        "AlignScore-base.ckpt",
    )
