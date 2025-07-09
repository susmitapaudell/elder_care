from pydantic import BaseModel, field_validator
from datetime import date
from fastapi import FastAPI, HTTPException

app = FastAPI()

class UserProfile(BaseModel):
    full_name: str
    role: str
    dob: date
    height_cm: float
    weight_kg: float
    blood_group: str

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
    @classmethod
    def validate_blood_group(cls, v):
        valid_groups = {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
        bg = v.upper()
        if bg not in valid_groups:
            raise ValueError(f"Invalid blood group: {v}")
        return bg

@app.post("/userprofile")
def create_user_profile(profile: UserProfile):
    return {
        "full_name": profile.full_name,
        "role": profile.role,
        "dob": profile.dob,
        "age": profile.age,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "bmi": profile.bmi,
        "blood_group": profile.blood_group,
    }
