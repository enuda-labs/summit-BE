from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
import random
from pydantic import BaseModel, EmailStr, constr, ConfigDict
import string
from app.models.user import User

SUBSCRIPTION_TYPES = [
    "free",
    "light",
    "standard",
    "pro"
]

SUBSCRIPTION_FREQUENCY = [
    "monthly",
    "yearly"
]

class UserSubscription(models.Model):
    id = fields.IntField(pk=True)
    user = fields.CharField(max_length=255)
    subscription_plan = fields.CharField(max_length=10, choices=SUBSCRIPTION_TYPES)
    subscription_frequency = fields.CharField(max_length=7, choices=SUBSCRIPTION_FREQUENCY)
    start_date = fields.DatetimeField(auto_now_add=True)
    end_date = fields.DatetimeField(null=True)
    stripe_subscription_id = fields.CharField(max_length=255, null=True)
    is_active = fields.BooleanField(default=True)

    def __str__(self):
        return f"{self.subscription_plan}"
    
#     # Get the subscription type for a user
    @property
    async def my_subscription(self):
        # get a user's subscription plan
        subscription = await UserSubscription.filter(user=self.user).first()
        return subscription.subscription_plan if subscription else None

    # Check if user's subscription is expired
    @property
    async def is_expired(self):
        return self.end_date is not None and self.end_date < fields.DatetimeField.now()
    

UserSubscription_Pydantic = pydantic_model_creator(
    UserSubscription,
    name="UserSubscription",
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)

UserSubscriptionIn_Pydantic = pydantic_model_creator(
    UserSubscription,
    name="UserSubscriptionIn",
    exclude_readonly=True,
    model_config=ConfigDict(extra="ignore")
)


class Quota(models.Model):
    id = fields.IntField(pk=True)
    user = fields.CharField(max_length=255)
    total = fields.IntField()
    used = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}"

    @property
    async def remaining(self):
        return self.total - self.used
    
    @property
    async def is_full(self):
        return self.used >= self.total
    
    @property
    async def is_empty(self):
        return self.used == 0
    
    
