from pathlib import Path
from typing import List, Optional

import fastavro

from ..configs import AvroConfig
from ..logger import get_logger
from .type import Dialog, Survey

__all__ = ["AvroSaver"]

PROFILE_SCHEMA = {
    "doc": "Agent属性",
    "name": "AgentProfile",
    "namespace": "com.agentsociety",
    "type": "record",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "name", "type": "string"},
        {"name": "gender", "type": "string"},
        {"name": "age", "type": "float"},
        {"name": "education", "type": "string"},
        {"name": "skill", "type": "string"},
        {"name": "occupation", "type": "string"},
        {"name": "family_consumption", "type": "string"},
        {"name": "consumption", "type": "string"},
        {"name": "personality", "type": "string"},
        {"name": "income", "type": "float"},
        {"name": "currency", "type": "float"},
        {"name": "residence", "type": "string"},
        {"name": "race", "type": "string"},
        {"name": "religion", "type": "string"},
        {"name": "marital_status", "type": "string"},
    ],
}

DIALOG_SCHEMA = {
    "doc": "Agent对话",
    "name": "AgentDialog",
    "namespace": "com.agentsociety",
    "type": "record",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "type", "type": "int"},
        {"name": "speaker", "type": "string"},
        {"name": "content", "type": "string"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}


STATUS_SCHEMA = {
    "doc": "Agent状态",
    "name": "AgentStatus",
    "namespace": "com.agentsociety",
    "type": "record",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "lng", "type": "double"},
        {"name": "lat", "type": "double"},
        {"name": "parent_id", "type": "int"},
        {"name": "current_need", "type": "string"},
        {"name": "intention", "type": "string"},
        {"name": "action", "type": "string"},
        {"name": "hungry", "type": "float"},
        {"name": "tired", "type": "float"},
        {"name": "safe", "type": "float"},
        {"name": "social", "type": "float"},
        {"name": "sadness", "type": "int"},
        {"name": "joy", "type": "int"},
        {"name": "fear", "type": "int"},
        {"name": "disgust", "type": "int"},
        {"name": "anger", "type": "int"},
        {"name": "surprise", "type": "int"},
        {"name": "emotion_types", "type": "string"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}

INSTITUTION_STATUS_SCHEMA = {
    "doc": "Institution状态",
    "name": "InstitutionStatus",
    "namespace": "com.agentsociety",
    "type": "record",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "type", "type": "int"},
        {
            "name": "nominal_gdp",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "real_gdp",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "unemployment",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "wages",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "prices",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {"name": "inventory", "type": ["int", "null"]},
        {"name": "price", "type": ["float", "null"]},
        {"name": "interest_rate", "type": ["float", "null"]},
        {
            "name": "bracket_cutoffs",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "bracket_rates",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
        {
            "name": "employees",
            "type": {"type": "array", "items": ["float", "int", "string", "null"]},
        },
    ],
}

SURVEY_SCHEMA = {
    "doc": "Agent问卷",
    "name": "AgentSurvey",
    "namespace": "com.agentsociety",
    "type": "record",
    "fields": [
        {"name": "id", "type": "int"},
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "survey_id", "type": "string"},
        {"name": "result", "type": "string"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}


class AvroSaver:
    """Save data to avro file as local storage saving and logging"""

    def __init__(self, config: AvroConfig, exp_id: str, group_id: Optional[str]):
        """
        Initialize the AvroSaver.

        - **Args**:
            - `config` (AvroConfig): The configuration for the AvroSaver.
            - `exp_id` (str): The ID of the experiment.
            - `group_id` (Optional[str]): The ID of the group.
        """
        self._config = config
        self._exp_id = exp_id
        self._group_id = group_id
        if not self.enabled:
            get_logger().warning("AvroSaver is not enabled")
            return
        self._avro_path = Path(self._config.path) / f"{self._exp_id}"
        if self._group_id is not None:
            self._avro_path = self._avro_path / f"{self._group_id}"
            self._avro_path.mkdir(parents=True, exist_ok=True)
            get_logger().info(f"AvroSaver initialized with path: {self._avro_path}")
            self._avro_file = {
                "profile": self._avro_path / f"profile.avro",
                "dialog": self._avro_path / f"dialog.avro",
                "status": self._avro_path / f"status.avro",
                "survey": self._avro_path / f"survey.avro",
            }

    @property
    def enabled(self):
        return self._config.enabled

    @property
    def exp_info_file(self):
        return self._avro_path / f"experiment_info.yaml"

    def close(self): ...

    def _check_is_group_avro_saver(self):
        if not self.enabled:
            raise RuntimeError("AvroSaver is not enabled")
        if self._group_id is None:
            raise RuntimeError("AvroSaver is not initialized")

    def append_surveys(self, surveys: List[Survey]):
        """
        Append a survey to the avro file.

        - **Args**:
            - `surveys` (List[AvroSurvey]): The surveys to append.
        """
        self._check_is_group_avro_saver()
        with open(self._avro_file["survey"], "a+b") as f:
            fastavro.writer(
                f,
                SURVEY_SCHEMA,
                surveys,
                codec="snappy",
            )

    def append_dialogs(self, dialogs: List[Dialog]):
        """
        Append a dialog to the avro file.

        - **Args**:
            - `dialogs` (List[AvroDialog]): The dialogs to append.
        """
        self._check_is_group_avro_saver()
        with open(self._avro_file["dialog"], "a+b") as f:
            fastavro.writer(
                f,
                DIALOG_SCHEMA,
                dialogs,
                codec="snappy",
            )
