from dataclasses import dataclass
from datetime import date
from piprot.models.requirement import Requirement
from piprot.models.version import PiprotVersion
from typing import Optional


@dataclass
class PiprotResult:
    requirement: Requirement
    latest_version: Optional[PiprotVersion]
    latest_release_date: Optional[date]
    current_version: Optional[PiprotVersion]
    current_release_date: Optional[date]
