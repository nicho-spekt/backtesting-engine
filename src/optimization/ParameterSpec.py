
from dataclasses import dataclass

@dataclass
class ParameterSpec:
    minimum: float
    maximum: float
    step: float
    parameter_type: type