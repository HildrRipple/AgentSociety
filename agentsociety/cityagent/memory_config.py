import copy
import random
from collections import deque
from typing import Any, Callable, List, Optional, Union

import jsonc
import numpy as np
from mosstool.map._map_util.const import AOI_START_ID
from pydantic import BaseModel

from ..configs import DistributionConfig
from ..environment.economy import EconomyEntityType
from ..logger import get_logger

pareto_param = 8
payment_max_skill_multiplier_base = 950
payment_max_skill_multiplier = float(payment_max_skill_multiplier_base)
pmsm = payment_max_skill_multiplier
pareto_samples = np.random.pareto(pareto_param, size=(1000, 10))
clipped_skills = np.minimum(pmsm, (pmsm - 1) * pareto_samples + 1)
sorted_clipped_skills = np.sort(clipped_skills, axis=1)
agent_skills = list(sorted_clipped_skills.mean(axis=0))

__all__ = [
    "Distribution",
    "ChoiceDistribution",
    "UniformIntDistribution",
    "UniformFloatDistribution",
    "NormalDistribution",
    "ConstantDistribution",
    "MemoryConfigGenerator",
    "MemoryT",
    "memory_config_societyagent",
    "memory_config_firm",
    "memory_config_government",
    "memory_config_bank",
    "memory_config_nbs",
]


# Distribution system for memory configuration
class Distribution:
    """
    Abstract base class for all distribution types.
    - **Description**:
        - Provides an interface for sampling values from a distribution.

    - **Args**:
        - None

    - **Returns**:
        - None
    """

    def sample(self) -> Any:
        """
        Sample a value from this distribution.
        - **Description**:
            - Abstract method to be implemented by subclasses.

        - **Args**:
            - None

        - **Returns**:
            - Any: A value sampled from the distribution.
        """
        raise NotImplementedError("Subclasses must implement sample()")

    @staticmethod
    def create(dist_type: str, **kwargs) -> "Distribution":
        """
        Factory method to create a distribution of the specified type.
        - **Description**:
            - Creates and returns a distribution instance based on the provided type.

        - **Args**:
            - `dist_type` (str): Type of distribution to create ('uniform', 'normal', etc.)
            - `**kwargs`: Parameters specific to the distribution type

        - **Returns**:
            - Distribution: A distribution instance
        """
        if dist_type == "choice":
            return ChoiceDistribution(**kwargs)
        elif dist_type == "uniform_int":
            return UniformIntDistribution(**kwargs)
        elif dist_type == "uniform_float":
            return UniformFloatDistribution(**kwargs)
        elif dist_type == "normal":
            return NormalDistribution(**kwargs)
        elif dist_type == "constant":
            return ConstantDistribution(**kwargs)
        else:
            raise ValueError(f"Unknown distribution type: {dist_type}")

    @staticmethod
    def from_config(config: DistributionConfig) -> "Distribution":
        """
        Create a distribution from a configuration.
        - **Description**:
            - Creates a distribution instance from a DistributionConfig object.

        - **Args**:
            - `config` (DistributionConfig): The distribution configuration.

        - **Returns**:
            - Distribution: A distribution instance
        """
        return Distribution.create(
            dist_type=config.dist_type.value,
            choices=config.choices,
            weights=config.weights,
            min_value=config.min_value,
            max_value=config.max_value,
            mean=config.mean,
            std=config.std,
            value=config.value,
        )


class ChoiceDistribution(Distribution):
    """
    Distribution that samples from a list of choices with equal probability.
    - **Description**:
        - Randomly selects one item from a provided list of choices.

    - **Args**:
        - `choices` (List[Any]): List of possible values to sample from
        - `weights` (Optional[List[float]]): Optional probability weights for choices

    - **Returns**:
        - None
    """

    def __init__(self, choices: List[Any], weights: Optional[List[float]] = None):
        self.choices = choices
        self.weights = weights

    def sample(self) -> Any:
        return random.choices(self.choices, weights=self.weights, k=1)[0]


class UniformIntDistribution(Distribution):
    """
    Distribution that samples integers uniformly from a range.
    - **Description**:
        - Samples integers with equal probability from [min_value, max_value].

    - **Args**:
        - `min_value` (int): Minimum value (inclusive)
        - `max_value` (int): Maximum value (inclusive)

    - **Returns**:
        - None
    """

    def __init__(self, min_value: int, max_value: int):
        self.min_value = min_value
        self.max_value = max_value

    def sample(self) -> int:
        return random.randint(self.min_value, self.max_value)


class UniformFloatDistribution(Distribution):
    """
    Distribution that samples floats uniformly from a range.
    - **Description**:
        - Samples floating point values with equal probability from [min_value, max_value).

    - **Args**:
        - `min_value` (float): Minimum value (inclusive)
        - `max_value` (float): Maximum value (exclusive)

    - **Returns**:
        - None
    """

    def __init__(self, min_value: float, max_value: float):
        self.min_value = min_value
        self.max_value = max_value

    def sample(self) -> float:
        return self.min_value + random.random() * (self.max_value - self.min_value)


class NormalDistribution(Distribution):
    """
    Distribution that samples from a normal (Gaussian) distribution.
    - **Description**:
        - Samples values from a normal distribution with given mean and standard deviation.

    - **Args**:
        - `mean` (float): Mean of the distribution
        - `std` (float): Standard deviation of the distribution
        - `min_value` (Optional[float]): Minimum allowed value (for truncation)
        - `max_value` (Optional[float]): Maximum allowed value (for truncation)

    - **Returns**:
        - None
    """

    def __init__(
        self,
        mean: float,
        std: float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ):
        self.mean = mean
        self.std = std
        self.min_value = min_value
        self.max_value = max_value

    def sample(self) -> float:
        value = random.normalvariate(self.mean, self.std)
        if self.min_value is not None:
            value = max(value, self.min_value)
        if self.max_value is not None:
            value = min(value, self.max_value)
        return value


class ConstantDistribution(Distribution):
    """
    Distribution that always returns the same value.
    - **Description**:
        - Returns a constant value every time sample() is called.

    - **Args**:
        - `value` (Any): The constant value to return

    - **Returns**:
        - None
    """

    def __init__(self, value: Any):
        self.value = value

    def sample(self) -> Any:
        return self.value


# Default distributions for different profile fields
DEFAULT_DISTRIBUTIONS = {
    "name": ChoiceDistribution(
        choices=[
            "Alice",
            "Bob",
            "Charlie",
            "David",
            "Eve",
            "Frank",
            "Grace",
            "Helen",
            "Ivy",
            "Jack",
            "Kelly",
            "Lily",
            "Mike",
            "Nancy",
            "Oscar",
            "Peter",
            "Queen",
            "Rose",
            "Sam",
            "Tom",
            "Ulysses",
            "Vicky",
            "Will",
            "Xavier",
            "Yvonne",
            "Zack",
        ]
    ),
    "gender": ChoiceDistribution(choices=["male", "female"]),
    "age": UniformIntDistribution(min_value=18, max_value=65),
    "education": ChoiceDistribution(
        choices=["Doctor", "Master", "Bachelor", "College", "High School"]
    ),
    "skill": ChoiceDistribution(
        choices=[
            "Good at problem-solving",
            "Good at communication",
            "Good at creativity",
            "Good at teamwork",
            "Other",
        ]
    ),
    "occupation": ChoiceDistribution(
        choices=[
            "Student",
            "Teacher",
            "Doctor",
            "Engineer",
            "Manager",
            "Businessman",
            "Artist",
            "Athlete",
            "Other",
        ]
    ),
    "family_consumption": ChoiceDistribution(choices=["low", "medium", "high"]),
    "consumption": ChoiceDistribution(
        choices=["low", "slightly low", "medium", "slightly high", "high"]
    ),
    "personality": ChoiceDistribution(
        choices=["outgoint", "introvert", "ambivert", "extrovert"]
    ),
    "income": UniformIntDistribution(min_value=1000, max_value=20000),
    "currency": UniformIntDistribution(min_value=1000, max_value=100000),
    "residence": ChoiceDistribution(choices=["city", "suburb", "rural"]),
    "city": ConstantDistribution(value="New York"),
    "race": ChoiceDistribution(
        choices=[
            "Chinese",
            "American",
            "British",
            "French",
            "German",
            "Japanese",
            "Korean",
            "Russian",
            "Other",
        ]
    ),
    "religion": ChoiceDistribution(
        choices=["none", "Christian", "Muslim", "Buddhist", "Hindu", "Other"]
    ),
    "marital_status": ChoiceDistribution(
        choices=["not married", "married", "divorced", "widowed"]
    ),
}

# # User-configurable distributions
# CUSTOM_DISTRIBUTIONS = {}


# def set_distribution(field: str, dist_type: str, **kwargs):
#     """
#     Set a custom distribution for a specific field.
#     - **Description**:
#         - Configures a custom distribution for sampling values for a specific field.

#     - **Args**:
#         - `field` (str): The field name to configure
#         - `dist_type` (str): Type of distribution (e.g., 'choice', 'uniform_int')
#         - `**kwargs`: Parameters specific to the distribution type

#     - **Returns**:
#         - None
#     """
#     CUSTOM_DISTRIBUTIONS[field] = Distribution.create(dist_type, **kwargs)


def get_distribution(
    distributions: dict[str, Distribution], field: str
) -> Distribution:
    """
    Get the distribution for a specific field.
    - **Description**:
        - Returns the configured distribution for a field, preferring custom over default.

    - **Args**:
        - `distributions` (dict[str, Distribution]): The distributions to use
        - `field` (str): The field name

    - **Returns**:
        - Distribution: The distribution to use for sampling values
    """
    # if field in CUSTOM_DISTRIBUTIONS:
    #     return CUSTOM_DISTRIBUTIONS[field]
    # elif field in DEFAULT_DISTRIBUTIONS:
    #     return DEFAULT_DISTRIBUTIONS[field]
    # else:
    #     raise ValueError(f"No distribution configured for field: {field}")

    if field in distributions:
        return distributions[field]
    else:
        raise ValueError(f"No distribution configured for field: {field}")


def sample_field_value(distributions: dict[str, Distribution], field: str) -> Any:
    """
    Sample a value for a specific field using its configured distribution.
    - **Description**:
        - Samples a value using the field's configured distribution.

    - **Args**:
        - `field` (str): The field name

    - **Returns**:
        - Any: A sampled value for the field
    """
    dist = get_distribution(distributions, field)
    if dist:
        return dist.sample()
    raise ValueError(f"No distribution configured for field: {field}")


MemoryT = Union[tuple[type, Any], tuple[type, Any, bool]]
"""
MemoryT is a tuple of (type, value, use embedding model)
- type: the type of the value
- value: the value
- use embedding model (optional): whether the value is generated by embedding model
"""


def memory_config_societyagent(
    distributions: dict[str, Distribution],
) -> tuple[dict[str, MemoryT], dict[str, MemoryT], dict[str, Any]]:
    EXTRA_ATTRIBUTES = {
        "type": (str, "citizen"),
        # Needs Model
        "hunger_satisfaction": (float, 0.9, False),  # hunger satisfaction
        "energy_satisfaction": (float, 0.9, False),  # energy satisfaction
        "safety_satisfaction": (float, 0.4, False),  # safety satisfaction
        "social_satisfaction": (float, 0.6, False),  # social satisfaction
        "current_need": (str, "none", False),
        # Plan Behavior Model
        "current_plan": (dict, {}, False),
        "execution_context": (dict, {}, False),
        "plan_history": (list, [], False),
        # cognition
        "emotion": (
            dict,
            {
                "sadness": 5,
                "joy": 5,
                "fear": 5,
                "disgust": 5,
                "anger": 5,
                "surprise": 5,
            },
            False,
        ),
        "attitude": (dict, {}, True),
        "thought": (str, "Currently nothing good or bad is happening", True),
        "emotion_types": (str, "Relief", True),
        # economy
        "work_skill": (
            float,
            random.choice(agent_skills),
            True,
        ),  # work skill
        "tax_paid": (float, 0.0, False),  # tax paid
        "consumption_currency": (float, 0.0, False),  # consumption
        "goods_demand": (int, 0, False),
        "goods_consumption": (int, 0, False),
        "work_propensity": (float, 0.0, False),
        "consumption_propensity": (float, 0.0, False),
        "to_consumption_currency": (float, 0.0, False),
        "firm_id": (int, 0, False),
        "government_id": (int, 0, False),
        "bank_id": (int, 0, False),
        "nbs_id": (int, 0, False),
        "dialog_queue": (deque(maxlen=3), [], False),
        "firm_forward": (int, 0, False),
        "bank_forward": (int, 0, False),
        "nbs_forward": (int, 0, False),
        "government_forward": (int, 0, False),
        "forward": (int, 0, False),
        "depression": (float, 0.0, False),
        "ubi_opinion": (list, [], False),
        "working_experience": (list, [], False),
        "work_hour_month": (float, 160, False),
        "work_hour_finish": (float, 0, False),
        # social
        "friends": (list, [], False),  # friends list
        "relationships": (dict, {}, False),  # relationship strength with each friend
        "relation_types": (dict, {}, False),
        "chat_histories": (dict, {}, False),  # all chat histories
        "interactions": (dict, {}, False),  # all interaction records
        # mobility
        "number_poi_visited": (int, 1, False),
        "location_knowledge": (dict, {}, False),  # location knowledge
    }

    PROFILE = {
        "name": (str, sample_field_value(distributions, "name"), True),
        "gender": (str, sample_field_value(distributions, "gender"), True),
        "age": (int, sample_field_value(distributions, "age"), True),
        "education": (str, sample_field_value(distributions, "education"), True),
        "skill": (str, sample_field_value(distributions, "skill"), True),
        "occupation": (str, sample_field_value(distributions, "occupation"), True),
        "family_consumption": (
            str,
            sample_field_value(distributions, "family_consumption"),
            True,
        ),
        "consumption": (str, sample_field_value(distributions, "consumption"), True),
        "personality": (str, sample_field_value(distributions, "personality"), True),
        "income": (float, sample_field_value(distributions, "income"), True),
        "currency": (float, sample_field_value(distributions, "currency"), True),
        "residence": (str, sample_field_value(distributions, "residence"), True),
        "city": (str, sample_field_value(distributions, "city"), True),
        "race": (str, sample_field_value(distributions, "race"), True),
        "religion": (str, sample_field_value(distributions, "religion"), True),
        "marital_status": (
            str,
            sample_field_value(distributions, "marital_status"),
            True,
        ),
    }

    # TODO: fix it in V1.3
    BASE = {
        "home": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
        "work": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
    }

    return EXTRA_ATTRIBUTES, PROFILE, BASE


def memory_config_firm(
    distributions: dict[str, Distribution],
) -> tuple[dict[str, MemoryT], dict[str, Union[MemoryT, float]], dict[str, Any]]:
    EXTRA_ATTRIBUTES = {
        "type": (int, EconomyEntityType.Firm),
        "location": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
        "price": (float, float(np.mean(agent_skills))),
        "inventory": (int, 0),
        "employees": (list, []),
        "employees_agent_id": (list, []),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "demand": (int, 0),
        "sales": (int, 0),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "interest_rate": (float, 0.03),
        "citizen_ids": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_government(
    distributions: dict[str, Distribution],
) -> tuple[dict[str, MemoryT], dict[str, Union[MemoryT, float]], dict[str, Any]]:
    EXTRA_ATTRIBUTES = {
        "type": (int, EconomyEntityType.Government),
        # 'bracket_cutoffs': (list, list(np.array([0, 97, 394.75, 842, 1607.25, 2041, 5103])*100/12)),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "citizen_ids": (list, []),
        "citizens_agent_id": (list, []),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "inventory": (int, 0),
        "interest_rate": (float, 0.03),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_bank(
    distributions: dict[str, Distribution],
) -> tuple[dict[str, MemoryT], dict[str, Union[MemoryT, float]], dict[str, Any]]:
    EXTRA_ATTRIBUTES = {
        "type": (int, EconomyEntityType.Bank),
        "interest_rate": (float, 0.03),
        "citizen_ids": (list, []),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),  # useless
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "inventory": (int, 0),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_nbs(
    distributions: dict[str, Distribution],
) -> tuple[dict[str, MemoryT], dict[str, MemoryT], dict[str, Any]]:
    EXTRA_ATTRIBUTES = {
        "type": (int, EconomyEntityType.NBS),
        # economy simulator
        "citizen_ids": (list, []),
        "nominal_gdp": (dict, {}),
        "real_gdp": (dict, {}),
        "unemployment": (dict, {}),
        "wages": (dict, {}),
        "prices": (dict, {"0": float(np.mean(agent_skills))}),
        "working_hours": (dict, {}),
        "depression": (dict, {}),
        "consumption_currency": (dict, {}),
        "income_currency": (dict, {}),
        "locus_control": (dict, {}),
        "currency": (float, 1e12),
        # other
        "firm_id": (int, 0),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),  # useless
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "inventory": (int, 0),
        "interest_rate": (float, 0.03),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "forward_times": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {}, {}


class MemoryConfigGenerator:
    """
    Generate memory configuration.
    """

    def __init__(
        self,
        memory_config_func: Callable[
            [dict[str, Distribution]],
            tuple[dict[str, MemoryT], dict[str, Union[MemoryT, float]], dict[str, Any]],
        ],
        memory_from_file: Optional[str] = None,
        memory_distributions: Optional[dict[str, DistributionConfig]] = None,
    ):
        """
        Initialize the memory config generator.

        - **Args**:
            - `memory_config_func` (Callable): The function to generate the memory configuration.
            - `memory_from_file` (Optional[str]): The path to the file containing the memory configuration.
            - `memory_distributions` (Optional[dict[str, DistributionConfig]]): The distributions to use for the memory configuration.
        """
        self._memory_config_func = memory_config_func
        if memory_from_file is not None:
            self._memory_data = memory_config_load_file(memory_from_file)
        else:
            self._memory_data = None
        self._distributions = copy.deepcopy(DEFAULT_DISTRIBUTIONS)
        if memory_distributions is not None:
            for field, distribution in memory_distributions.items():
                self._distributions[field] = Distribution.from_config(distribution)

    def generate(self, i: int):
        """
        Generate memory configuration.

        Args:
            i (int): The index of the memory configuration to generate. Used to find the i-th memory configuration in the file.

        Returns:
            tuple[dict[str, MemoryT], dict[str, MemoryT], dict[str, Any]]: The memory configuration.
        """
        extra_attrs, profile, base = self._memory_config_func(self._distributions)
        if self._memory_data is not None:
            if i >= len(self._memory_data):
                raise ValueError(
                    f"Index out of range. Expected index <= {len(self._memory_data)}, got: {i}"
                )
            memory_data = self._memory_data[i]
        else:
            memory_data = {}
        return memory_config_merge(memory_data, extra_attrs, profile, base)


# TODO: TEST THIS in V1.3
def memory_config_load_file(file_path):
    """
    Loads the memory configuration from the given file.
    - **Description**:
        - Loads the memory configuration from the given file.
        - Supports both .json and .jsonl file types.
        - For .json files, returns the parsed JSON content.
        - For .jsonl files, returns a list of parsed JSON objects from each line.

    - **Args**:
        - `file_path` (str): The path to the file containing the memory configuration.

    - **Returns**:
        - `memory_data` (Union[dict, list]): The memory data - either a single object or list of objects.

    - **Raises**:
        - `ValueError`: If the file type is not supported.
    """
    # Check file extension
    if file_path.endswith(".json"):
        with open(file_path, "r") as f:
            memory_data = jsonc.load(f)
        if not isinstance(memory_data, list):
            raise ValueError(
                f"Invalid memory data. Expected a list, got: {memory_data}"
            )
        return memory_data
    elif file_path.endswith(".jsonl"):
        memory_data = []
        with open(file_path, "r") as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    memory_data.append(jsonc.loads(line))
        return memory_data
    else:
        raise ValueError(
            f"Unsupported file type. Only .json or .jsonl files are supported. Got: {file_path}"
        )


def memory_config_merge(
    file_data: dict,
    base_extra_attrs: dict[str, MemoryT],
    base_profile: dict[str, Union[MemoryT, float]],
    base_base: dict[str, Any],
) -> dict[str, Any]:
    """
    Merges memory configuration from file with base configuration.

    - **Description**:
        - Takes file data and merges it with base configuration components.
        - Special handling for 'home' and 'work' fields which may need to be placed in correct section.

    - **Args**:
        - `file_data` (dict): Memory configuration data loaded from file.
        - `base_extra_attrs` (dict): Base extra attributes configuration.
        - `base_profile` (dict): Base profile configuration.
        - `base_base` (dict): Base memory configuration.

    - **Returns**:
        - `dict`: Merged memory configuration with proper structure.
    """
    # Create copies to avoid modifying the originals
    extra_attrs = base_extra_attrs.copy()
    profile = base_profile.copy()
    base = base_base.copy()

    # Special handling for home and work locations
    location_fields = ["home", "work"]

    for key, value in file_data.items():
        # Check where this key exists in the base configuration
        if key in extra_attrs:
            extra_attrs[key] = value
        elif key in profile:
            profile[key] = value
        elif key in location_fields:
            # Typically these would go in profile, but follow your specific needs
            base[key] = {"aoi_position": {"aoi_id": value}}
        else:
            # For any new fields not in base config, add to extra_attrs
            extra_attrs[key] = value

    return {"extra_attributes": extra_attrs, "profile": profile, "base": base}
