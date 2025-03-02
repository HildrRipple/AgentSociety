import random
from collections import deque
import json
from typing import Any, Type, List, Union, Optional, Callable, Tuple

import numpy as np
import pycityproto.city.economy.v2.economy_pb2 as economyv2
from mosstool.map._map_util.const import AOI_START_ID

from .firmagent import FirmAgent

pareto_param = 8
payment_max_skill_multiplier_base = 950
payment_max_skill_multiplier = float(payment_max_skill_multiplier_base)
pmsm = payment_max_skill_multiplier
pareto_samples = np.random.pareto(pareto_param, size=(1000, 10))
clipped_skills = np.minimum(pmsm, (pmsm - 1) * pareto_samples + 1)
sorted_clipped_skills = np.sort(clipped_skills, axis=1)
agent_skills = list(sorted_clipped_skills.mean(axis=0))

work_locations = [AOI_START_ID + random.randint(1000, 10000) for _ in range(1000)]


async def memory_config_init(simulation):
    global work_locations
    number_of_firm = simulation.agent_count[FirmAgent]
    work_locations = [
        AOI_START_ID + random.randint(1000, 10000) for _ in range(number_of_firm)
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
    def create(dist_type: str, **kwargs) -> 'Distribution':
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
    def __init__(self, mean: float, std: float, min_value: Optional[float] = None, 
                 max_value: Optional[float] = None):
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
    "name": ChoiceDistribution(choices=[
        "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Helen", 
        "Ivy", "Jack", "Kelly", "Lily", "Mike", "Nancy", "Oscar", "Peter", 
        "Queen", "Rose", "Sam", "Tom", "Ulysses", "Vicky", "Will", "Xavier", 
        "Yvonne", "Zack"
    ]),
    "gender": ChoiceDistribution(choices=["male", "female"]),
    "age": UniformIntDistribution(min_value=18, max_value=65),
    "education": ChoiceDistribution(choices=[
        "Doctor", "Master", "Bachelor", "College", "High School"
    ]),
    "skill": ChoiceDistribution(choices=[
        "Good at problem-solving", "Good at communication", 
        "Good at creativity", "Good at teamwork", "Other"
    ]),
    "occupation": ChoiceDistribution(choices=[
        "Student", "Teacher", "Doctor", "Engineer", "Manager", 
        "Businessman", "Artist", "Athlete", "Other"
    ]),
    "family_consumption": ChoiceDistribution(choices=["low", "medium", "high"]),
    "consumption": ChoiceDistribution(choices=[
        "low", "slightly low", "medium", "slightly high", "high"
    ]),
    "personality": ChoiceDistribution(choices=[
        "outgoint", "introvert", "ambivert", "extrovert"
    ]),
    "income": UniformIntDistribution(min_value=1000, max_value=20000),
    "currency": UniformIntDistribution(min_value=1000, max_value=100000),
    "residence": ChoiceDistribution(choices=["city", "suburb", "rural"]),
    "city": ConstantDistribution(value="New York"),
    "race": ChoiceDistribution(choices=[
        "Chinese", "American", "British", "French", "German", 
        "Japanese", "Korean", "Russian", "Other"
    ]),
    "religion": ChoiceDistribution(choices=[
        "none", "Christian", "Muslim", "Buddhist", "Hindu", "Other"
    ]),
    "marital_status": ChoiceDistribution(choices=[
        "not married", "married", "divorced", "widowed"
    ]),
}

# User-configurable distributions
CUSTOM_DISTRIBUTIONS = {}

def set_distribution(field: str, dist_type: str, **kwargs):
    """
    Set a custom distribution for a specific field.
    - **Description**:
        - Configures a custom distribution for sampling values for a specific field.

    - **Args**:
        - `field` (str): The field name to configure
        - `dist_type` (str): Type of distribution (e.g., 'choice', 'uniform_int')
        - `**kwargs`: Parameters specific to the distribution type

    - **Returns**:
        - None
    """
    CUSTOM_DISTRIBUTIONS[field] = Distribution.create(dist_type, **kwargs)

def get_distribution(field: str) -> Distribution:
    """
    Get the distribution for a specific field.
    - **Description**:
        - Returns the configured distribution for a field, preferring custom over default.

    - **Args**:
        - `field` (str): The field name

    - **Returns**:
        - Distribution: The distribution to use for sampling values
    """
    return CUSTOM_DISTRIBUTIONS.get(field, DEFAULT_DISTRIBUTIONS.get(field))

def sample_field_value(field: str) -> Any:
    """
    Sample a value for a specific field using its configured distribution.
    - **Description**:
        - Samples a value using the field's configured distribution.

    - **Args**:
        - `field` (str): The field name

    - **Returns**:
        - Any: A sampled value for the field
    """
    dist = get_distribution(field)
    if dist:
        return dist.sample()
    raise ValueError(f"No distribution configured for field: {field}")


def memory_config_societyagent():
    global work_locations
    EXTRA_ATTRIBUTES = {
        "type": (str, "citizen"),
        # Needs Model
        "hunger_satisfaction": (float, random.random(), False),  # hunger satisfaction
        "energy_satisfaction": (float, random.random(), False),  # energy satisfaction
        "safety_satisfaction": (float, random.random(), False),  # safety satisfaction
        "social_satisfaction": (float, random.random(), False),  # social satisfaction
        "current_need": (str, "none", False),
        # Plan Behavior Model
        "current_plan": (list, [], False),
        "current_step": (dict, {"intention": "", "type": ""}, False),
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
    }

    PROFILE = {
        "name": (str, sample_field_value("name"), True),
        "gender": (str, sample_field_value("gender"), True),
        "age": (int, sample_field_value("age"), True),
        "education": (str, sample_field_value("education"), True),
        "skill": (str, sample_field_value("skill"), True),
        "occupation": (str, sample_field_value("occupation"), True),
        "family_consumption": (str, sample_field_value("family_consumption"), True),
        "consumption": (str, sample_field_value("consumption"), True),
        "personality": (str, sample_field_value("personality"), True),
        "income": (float, sample_field_value("income"), True),
        "currency": (float, sample_field_value("currency"), True),
        "residence": (str, sample_field_value("residence"), True),
        "city": (str, sample_field_value("city"), True),
        "race": (str, sample_field_value("race"), True),
        "religion": (str, sample_field_value("religion"), True),
        "marital_status": (str, sample_field_value("marital_status"), True),
    }

    BASE = {
        "home": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
        "work": {"aoi_position": {"aoi_id": random.choice(work_locations)}},
    }

    return EXTRA_ATTRIBUTES, PROFILE, BASE


def memory_config_firm():
    global work_locations
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_FIRM),
        "location": {"aoi_position": {"aoi_id": random.choice(work_locations)}},
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
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_government():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_GOVERNMENT),
        # 'bracket_cutoffs': (list, list(np.array([0, 97, 394.75, 842, 1607.25, 2041, 5103])*100/12)),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "citizens": (list, []),
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
        "employees_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_bank():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_BANK),
        "interest_rate": (float, 0.03),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
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
        "employees_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_nbs():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_NBS),
        "nominal_gdp": (list, []),
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
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
        "employees_agent_id": (list, []),
        "forward_times": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {}, {}


def memory_config_load_file(file_path):
    """
    Loads the memory configuration from the given file.
    - **Description**:
        - Loads the memory configuration from the given file.

    - **Args**:
        - `file_path` (str): The path to the file containing the memory configuration.

    - **Returns**:
        - `memory_data` (list): The memory data.
    """
    with open(file_path, 'r') as f:
        memory_data = json.load(f)
    return memory_data


def memory_config_merge(file_data, base_extra_attrs, base_profile, base_base):
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
    location_fields = ['home', 'work']
    
    for key, value in file_data.items():
        # Check where this key exists in the base configuration
        if key in extra_attrs:
            extra_attrs[key] = value
        elif key in profile:
            profile[key] = value
        elif key in location_fields:
            # Typically these would go in profile, but follow your specific needs
            profile[key] = {
                "aoi_position": {"aoi_id": value}
            }
        else:
            # For any new fields not in base config, add to extra_attrs
            extra_attrs[key] = value
    
    return {
        "extra_attributes": extra_attrs,
        "profile": profile,
        "base": base
    }
