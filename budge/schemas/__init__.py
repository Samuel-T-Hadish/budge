"""
beat.config.schemas.input
 
This module contains the Pydantic schemas for the page input data.
"""

from typing import List, Dict, Optional, Final
from pydantic import BaseModel, Field, field_validator, model_validator
import uuid
from pydantic import BaseModel, Field, field_validator, model_validator
from budge.schemas.meta import MetaInput
from budge.schemas.page1 import Page1Input
from budge.schemas.page2 import Page2Input
from budge.schemas.estimation import EstimationInput


class ProjectData(BaseModel):
    meta_input: MetaInput
    page1_input: Page1Input
    page2_input: Page2Input
    page3_input: EstimationInput

