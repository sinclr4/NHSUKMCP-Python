"""Data models for NHS Organisations"""

from typing import Optional
from pydantic import BaseModel


class PostcodeResult(BaseModel):
    """Result of postcode to coordinates conversion"""
    latitude: float
    longitude: float
    postcode: str


class Organisation(BaseModel):
    """NHS Organisation details"""
    organisation_code: str
    organisation_name: str
    organisation_type: str
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    town: Optional[str] = None
    county: Optional[str] = None
    postcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance_miles: Optional[float] = None


# NHS Organisation Types
ORGANISATION_TYPES = {
    "CCG": "Clinical Commissioning Group",
    "CLI": "Clinic",
    "DEN": "Dental Practice",
    "GPB": "GP Branch Surgery",
    "GPP": "GP Practice",
    "HOS": "Hospital",
    "OPT": "Optician",
    "PHA": "Pharmacy",
    "PRO": "Provider Organisation",
    "WAL": "Walk-in Centre",
    "CAR": "Care Home",
    "MHT": "Mental Health Trust",
    "AMB": "Ambulance Trust",
    "ACU": "Acute Trust",
    "CHC": "Community Health Centre",
    "ICB": "Integrated Care Board",
    "PCN": "Primary Care Network",
    "SUR": "Surgical Centre",
    "URG": "Urgent Treatment Centre",
    "IMC": "Independent Medical Centre",
    "LAB": "Laboratory",
    "RAD": "Radiology Centre",
    "BLD": "Blood Donation Centre",
    "SCR": "Screening Service"
}
