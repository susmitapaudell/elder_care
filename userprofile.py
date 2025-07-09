from pydantic import BaseModel, field_validator
from datetime import date
import json, os
from fastapi import FastAPI, HTTPException

app = FastAPI()

class UserProfile(BaseModel):
    full_name: str
    role: str
    dob: date               # Date of birth, user input
    height_cm: float        # Height in centimeters
    weight_kg: float        # Weight in kilograms
    blood_group: str        # Blood group string like "A+", "O-", etc.

    @app.post("/userprofile")
    @property
    def age(self) -> int:
        today = date.today()
        age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return age

    @property
    def bmi(self) -> float:
        height_m = self.height_cm / 100
        bmi_value = self.weight_kg / (height_m ** 2)
        return round(bmi_value, 2)

    @field_validator('blood_group')
    def validate_blood_group(cls, v):
        valid_groups = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        bg = v.upper()
        if bg not in valid_groups:
            raise ValueError(f"Invalid blood group: {v}")
        return bg
