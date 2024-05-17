import socket
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    placeholder: str = "This is a placeholder setting."
    hostname: str = socket.gethostname()
    bert_model_name: Literal["roberta-base"] = "roberta-base"
    path_to_model_checkpoint: str = "models/AlignScore-base.ckpt"
    device: str = "cpu"
