
from dataclasses import dataclass

@dataclass
class ParameterSpec:
    minimum: int
    maximum: int
    step: int
    parameter_type: type