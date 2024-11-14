"""
beat.config.schemas.input
 
This module contains the Pydantic schemas for the page input data.
"""

from typing import List, Dict, Optional, Final
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid
from pydantic import BaseModel, Field, field_validator, model_validator
from budge.schemas.meta import MetaInput
from budge.schemas.estimation import EstimationInput


class ProjectData(BaseModel):
    meta_input: MetaInput
    estimation_input: EstimationInput

