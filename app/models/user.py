from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
import random
from pydantic import BaseModel, EmailStr, constr, ConfigDict
import string


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    username = fields.CharField(max_length=255, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.username


# Create Pydantic models for API
User_Pydantic = pydantic_model_creator(
    User,
    name="User",
    exclude=("hashed_password",),
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)

UserIn_Pydantic = pydantic_model_creator(
    User,
    name="UserIn",
    exclude=("hashed_password",),
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)

# User registration model with validation
class UserRegister(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=8, max_length=50)
    full_name: constr(max_length=255)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }
    )


# OTP verification model
class OTPVerify(BaseModel):
    otp: constr(min_length=6, max_length=6)
    recipient_email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "otp": "123456",
                "recipient_email": "user@example.com"
            }
        }
    )


class OTPSystem(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="otp_system")
    otp = fields.CharField(max_length=255)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "otp_system"

    def __str__(self):
        return str(self.otp)

    async def save(self, *args, **kwargs):
        if not self.otp:
            self.otp = self.generate_otp()
        await super().save(*args, **kwargs)

    def generate_otp(self) -> str:
        """Generate a 6-digit OTP and return it as a string"""
        return ''.join(random.choices(string.digits, k=6))


OTP_Pydantic = pydantic_model_creator(
    OTPSystem,
    name="OTP",
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)

OTPIn_Pydantic = pydantic_model_creator(
    OTPSystem,
    name="OTPIn",
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)
