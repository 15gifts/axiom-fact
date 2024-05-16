# required for loguru types to work during runtime
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, List, Literal, Protocol, TypeAlias, TypedDict

import loguru
from typing_extensions import NotRequired

# from app.utils.misc import safe_json_dump


class JsonLogRecord(TypedDict):
    date: float
    env: str
    hostname: str
    level: str
    msg: str
    pid: int | None
    reqId: NotRequired[str | None]
    file: str | None
    function: str
    line: int
    exception: loguru.RecordException | str | None
    extra: NotRequired[Dict[str, Any]]
    taskName: NotRequired[str | None]


LoggingLevel: TypeAlias = Literal[
    "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
]


class LoggingConfig(TypedDict):
    sink: Any
    level: LoggingLevel
    enqueue: bool
    backtrace: bool
    format: str | loguru.FormatFunction
    retention: NotRequired[str]


DeploymentType: TypeAlias = Literal["local", "cloud"]

CONFIG_MAPPING: Dict[DeploymentType, List[LoggingConfig]] = {
    "local": [
        {
            "sink": sys.stderr,
            "level": "DEBUG",
            "enqueue": False,
            "backtrace": True,
            "format": "<level>{level}</level> <green>{time}</green> <red>{extra[request_id]}</red> - <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        },
        {
            "sink": os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "logs",
                "app_{time}.log",
            ),
            "level": "DEBUG",
            "retention": "5 days",
            "enqueue": True,
            "backtrace": True,
            "format": "{extra[serialized]}",
        },
    ],
    "cloud": [
        {
            "sink": sys.stderr,
            "enqueue": True,
            "backtrace": True,
            "level": "INFO",
            "format": "{extra[serialized]}",
        }
    ],
}


# class UvicornJsonFormatter(jsonlogger.JsonFormatter):
#     """
#     Custom formatter for Uvicorn logs that outputs logs in JSON format. It's used for the few log messages that Uvicorn
#     outputs before we initialise our logging middleware which overtakes Uvicorn's own logging.
#     """

#     _cached_settings: Settings | None = None

#     @classmethod
#     def get_cached_settings(cls) -> Settings:
#         if cls._cached_settings is None:
#             cls._cached_settings = get_settings()
#         return cls._cached_settings

#     @classmethod
#     def update_settings(cls, new_settings: Settings):
#         cls._cached_settings = new_settings

#     def add_fields(
#         self,
#         log_record: Dict[str, Any],
#         record: logging.LogRecord,
#         message_dict: Dict[str, Any],
#     ):
#         super().add_fields(log_record, record, message_dict)

#         settings = self.get_cached_settings()

#         custom_log_record: JsonLogRecord = {
#             "date": record.created,
#             "env": settings.app_execution_env,
#             "hostname": settings.hostname,
#             "level": record.levelname.lower(),
#             "msg": record.message,
#             "pid": record.process,
#             "file": record.filename,
#             "function": record.funcName,
#             "line": record.lineno,
#             "exception": record.exc_text,
#         }

#         log_record.update(custom_log_record)

#         remove_extra_fields = ["color_message", "message"]
#         for field in remove_extra_fields:
#             log_record.pop(field, None)


class HasDict(Protocol):
    __dict__: Dict[str, Any]


def object_to_dict(obj: HasDict) -> Dict[str, Any]:
    """
    Converts an object's non-callable attributes to a dictionary. Attributes starting with an underscore are
    ignored.
    """
    return {
        key: value
        for key, value in obj.__dict__.items()
        if not key.startswith("_") and not callable(value)
    }


def safe_json_dump(data: Any) -> str:
    """Safe version of json.dumps that handles non-serializable objects."""
    return json.dumps(
        data,
        default=lambda o: object_to_dict(o)
        if not isinstance(o, type)
        else f"<non-serializable: {type(o).__qualname__}>",
    )


def get_deployment_type(environment: str) -> DeploymentType:
    """
    Get the deployment type for the given environment.
    """
    return "local" if environment == "local" else "cloud"


def get_logging_configs(environment: str) -> List[LoggingConfig]:
    """
    Get the logging configurations required for each environment.
    """
    deployment_type = get_deployment_type(environment)
    return CONFIG_MAPPING.get(deployment_type, CONFIG_MAPPING["cloud"])


def serialize_loguru_record(record: loguru.Record) -> str:
    """
    This is the function that will be called to serialize the log record so that we can write logs to a file
    in a structured format.

    Args:
        record: The loguru record to serialize.

    Returns:
        A JSON string representing the dictionary of the log record with fields for the message, level, request_id,
            file, function, line and an extra dictionary. When kwargs are added to the logger they will be added to the
            extra dictionary.
    """
    meta = record["extra"].get("meta", {})
    record["extra"].pop("meta", None)

    subset: JsonLogRecord = {
        "env": meta.get("env"),
        "hostname": meta.get("hostname"),
        "date": record["time"].timestamp(),
        "level": record["level"].name.lower(),
        "msg": record["message"],
        "pid": record["process"].id,
        "file": record["name"],
        "function": record["function"],
        "line": record["line"],
        "reqId": record["extra"].get("request_id"),
        "exception": record["exception"],
        "extra": record["extra"],
    }

    # althought this is a safe dump, which should handle unserializable objects, there is another dump() that's
    # internally used in Loguru when a record is added to a queue which will still fail on unserializable objects
    return safe_json_dump(subset)


def patch_record(record: loguru.Record):
    """
    This is the function that will be called to patch the log record and add in the serialised version to the extra
    field.
    """
    record["extra"]["serialized"] = serialize_loguru_record(record)


def configure_logger(environment: str = "local", hostname: str = ""):
    """
    This function configures the logger for the app. The logger is configured based on the environment.
    It will disable the uvicorn logs which we will replace with our own middleware during the app startup.
    """
    # This disables the uvicorn logs that we will replace in our middleware
    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.disabled = True
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.disabled = True

    logger = loguru.logger

    logger.configure(
        extra={
            "request_id": "",
            "meta": {
                "env": environment,
                "hostname": hostname,
            },
        },
    )

    logger.remove()

    logging_configs = get_logging_configs(environment)
    for logging_config in logging_configs:
        logger.add(**logging_config)

    return logger.patch(patch_record)


def get_logger() -> loguru.Logger:
    return loguru.logger.patch(patch_record)
