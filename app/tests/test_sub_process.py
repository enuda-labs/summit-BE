import pytest
from unittest.mock import patch, MagicMock
from app.services import sub_process
from httpx import AsyncClient
from main import app
import json


@pytest.mark.asyncio
@patch("app.services.sub_process.stripe.checkout.Session.create")
async def test_create_subscription_success(mock_stripe_create):
    # Arrange
    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"
    mock_session.id = "cs_test_123"
    mock_stripe_create.return_value = mock_session

    user = "testuser"
    plan = "light"
    frequency = "monthly"
    customer_stripe_id = "cus_test_123"

    # Patch environment variables
    with patch("os.getenv") as mock_getenv:
        def getenv_side_effect(key, default=None):
            envs = {
                "STRIPE_LIGHT_PRICE_ID": "price_1PKukMRqvXozesnLavG7Zmio",
                "FRONTEND_URL": "http://localhost:8000"
            }
            return envs.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        # Act
        result = await sub_process.create_subscription(user, plan, frequency, customer_stripe_id)

        # Assert
        assert result["message"] == "Subscription created successfully"
        assert result["checkout_url"] == "https://checkout.stripe.com/test"
        assert result["session_id"] == "cs_test_123"
        mock_stripe_create.assert_called_once()


@pytest.mark.asyncio
@patch("app.services.sub_process.stripe.checkout.Session.create")
@patch("app.services.sub_process.stripe.Webhook.construct_event")
async def test_create_subscription_e2e(mock_construct_event, mock_stripe_create):
    # 1. Register a user
    user_data = {
        "email": "e2euser@example.com",
        "username": "e2euser",
        "password": "TestPassword123!",
        "full_name": "E2E User"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Register user
        register_resp = await ac.post("/api/v1/register", json=user_data)
        assert register_resp.status_code == 200
        user_id = register_resp.json()["data"]["id"]

        # 2. Mock Stripe checkout session creation
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_session.id = "cs_test_e2e"
        mock_stripe_create.return_value = mock_session

        # 3. Call the create-subscription endpoint
        plan = "light"
        frequency = "monthly"
        with patch("os.getenv") as mock_getenv:
            def getenv_side_effect(key, default=None):
                envs = {
                    "STRIPE_LIGHT_PRICE_ID": "price_1PKukMRqvXozesnLavG7Zmio",
                    "FRONTEND_URL": "http://localhost:8000"
                }
                return envs.get(key, default)
            mock_getenv.side_effect = getenv_side_effect

            resp = await ac.post(f"/create-subscription/{user_id}/{plan}/{frequency}")
            assert resp.status_code == 200
            assert resp.json()["message"] == "Subscription created successfully"
            assert resp.json()["checkout_url"] == "https://checkout.stripe.com/test"
            assert resp.json()["session_id"] == "cs_test_e2e"

        # 4. Simulate a Stripe webhook call
        event_payload = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": str(user_id),
                        "subscription_plan": plan,
                        "subscription_frequency": frequency
                    }
                }
            }
        }
        mock_construct_event.return_value = MagicMock(
            type="checkout.session.completed",
            data=MagicMock(object=MagicMock(metadata=event_payload["data"]["object"]["metadata"]))
        )

        # Stripe sends the payload as bytes
        payload_bytes = json.dumps(event_payload).encode()
        headers = {"stripe-signature": "test_signature"}
        webhook_resp = await ac.post("/webhook/stripe", content=payload_bytes, headers=headers)
        assert webhook_resp.status_code == 200
        assert webhook_resp.json()["message"] == "Webhook received"

        # 5. Verify the subscription is created in the DB
        from app.models.subscription import UserSubscription
        sub = await UserSubscription.filter(user=str(user_id)).first()
        assert sub is not None
        assert sub.subscription_plan == plan
        assert sub.subscription_frequency == frequency
