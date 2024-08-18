from pydantic import BaseModel, EmailStr, field_validator
from datetime import date


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    age: int

    # Add validation to check that an email is valid formatted, i.e. contains an '@' character

    # Add validation to check that a Customer's age is between 18 and 120
    @field_validator('age')
    def age_must_be_between_18_and_120(cls, v):
        if v < 18 or v > 120:
            raise ValueError('age cannot be less than 18 or older than 120')
        return v


class CustomerCreate(CustomerBase):
    signup_date: date

    @field_validator('signup_date')
    def signup_date_must_be_today_or_earlier(cls, v):
        if v > date.today():
            raise ValueError('signup date must be today or earlier')
        return v


class CustomerUpdate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    signup_date: date

    class Config:
        from_attributes = True
