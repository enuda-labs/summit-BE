import pytest
from unittest.mock import patch, MagicMock
from app.services import sub_process
from httpx import AsyncClient
import os
import stripe
from fastapi import HTTPException, Request
import json
import logging
from datetime import datetime
from app.models.user import User
from app.models.subscription import UserSubscription
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
# Initialize Stripe with your secret key
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

print("STRIPE_SECRET_KEY", os.getenv("STRIPE_SECRET_KEY"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_subscription(user_id: int, plan: str, frequency: str = "monthly"):
    """
    Create a subscription for a user with the specified plan and frequency.
    
    Args:
        user_id (int): The ID of the user
        plan (str): The subscription plan (e.g., 'light', 'pro', 'enterprise')
        frequency (str): The billing frequency ('monthly' or 'yearly')
        
    Returns:
        dict: A dictionary containing the checkout URL and session ID
    """
    try:
        # Get the appropriate price ID based on plan and frequency
        price_id = os.getenv(f"STRIPE_{plan.upper()}_PRICE_ID")
        if not price_id:
            raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")
            
        # Create a Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"https://summit.guide",
            cancel_url=f"https://summit.guide/cancel",
            metadata={
                'user_id': str(user_id),
                'subscription_plan': plan,
                'subscription_frequency': frequency
            }
        )
        
        return {
            "message": "Subscription created successfully",
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events.
    
    Args:
        request (Request): The FastAPI request object containing the webhook payload
        
    Returns:
        dict: Response indicating the status of the webhook processing
    """
    try:
        logger.info("Starting webhook processing...")
        
        # Get the webhook payload and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        logger.info(f"Received webhook with signature: {sig_header}")
        
        if not sig_header:
            logger.error("Missing stripe-signature header")
            raise HTTPException(status_code=400, detail="Missing stripe-signature header")
            
        # Get the webhook secret from environment variables
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        logger.info(f"Webhook secret configured: {'Yes' if webhook_secret else 'No'}")
        
        if not webhook_secret:
            logger.error("Webhook secret not configured")
            raise HTTPException(status_code=500, detail="Webhook secret not configured")
            
        try:
            logger.info("Attempting to construct event...")
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            logger.info("Event constructed successfully")
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
            
        logger.info(f"Received Stripe event type: {event.get('type')}")
        
        if event["type"] == "checkout.session.completed":
            logger.info("Processing checkout.session.completed event")
            session = event["data"]["object"]
            subscription_id = session.get("subscription")
            logger.info(f"Subscription ID: {subscription_id}")
            
            metadata = session.get("metadata", {})
            user_id = metadata.get("user_id")
            subscription_plan = metadata.get("subscription_plan")
            subscription_frequency = metadata.get("subscription_frequency")
            
            logger.info(f"Extracted metadata: user_id={user_id}, plan={subscription_plan}, frequency={subscription_frequency}")
            
            if not user_id:
                logger.error("Missing user_id in metadata")
                raise HTTPException(status_code=400, detail="Missing user_id in metadata")
            
            
            # Fetch the Stripe subscription
            try:
                logger.info(f"Retrieving Stripe subscription: {subscription_id}")
                stripe_subscription = stripe.Subscription.retrieve(subscription_id)
                logger.info("Stripe subscription retrieved successfully")
                logger.info(f"Subscription object type: {type(stripe_subscription)}")
                logger.info(f"Subscription data: {stripe_subscription}")
                
                # Create or update the subscription record
                try:
                    logger.info("Processing subscription data...")
                    # Convert Stripe timestamps to datetime
                    current_period_start = datetime.fromtimestamp(int(stripe_subscription['items']['data'][0]['current_period_start']))
                    current_period_end = datetime.fromtimestamp(int(stripe_subscription['items']['data'][0]['current_period_end']))
                    
                    # Get the price from the subscription
                    price = float(stripe_subscription['items']['data'][0]['price']['unit_amount']) / 100  # Convert from cents to dollars
                    
                    logger.info("Creating/updating subscription record...")
                    # Create or update subscription
                    await UserSubscription.update_or_create(
                        user=user_id,
                        defaults={
                            "subscription_plan": subscription_plan,
                            "subscription_frequency": subscription_frequency,
                            "price": price,
                            "is_active": True,
                            "start_date": current_period_start,
                            "end_date": current_period_end,
                            "stripe_subscription_id": subscription_id
                        }
                    )
                    logger.info(f"Subscription successfully updated for user {user_id}")
                    
                except Exception as e:
                    logger.error(f"Database update error: {str(e)}")
                    logger.exception("Full traceback:")
                    raise HTTPException(status_code=500, detail=f"Subscription update error: {str(e)}")
                
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error while retrieving subscription: {e}")
                raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")
                
            return {"status": "success", "message": "Webhook processed successfully"}
            
        logger.warning(f"Unhandled event type: {event['type']}")
        return {"status": "ignored", "message": f"Unhandled event type: {event['type']}"}
        
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"General webhook processing error: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"General error: {str(e)}")
    
    
async def get_subscription_by_user_id(user_id: int):
    """
    Get a user's subscription by user ID.
    
    Args:
        user_id (int): The ID of the user

    Returns:
        dict: A dictionary containing the subscription details
    """
    try:
        # Get the subscription record for the user
        subscription = await UserSubscription.filter(user=str(user_id)).first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
            
        # Convert to dict using Tortoise's serialization
        return {
            "id": int(subscription.id),
            "user": str(subscription.user),
            "subscription_plan": str(subscription.subscription_plan),
            "subscription_frequency": str(subscription.subscription_frequency),
            "is_active": bool(subscription.is_active),
            "start_date": subscription.start_date.isoformat() if subscription.start_date else None,
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "stripe_subscription_id": str(subscription.stripe_subscription_id) if subscription.stripe_subscription_id else None,
        }

        
    except Exception as e:
        logger.error(f"Error getting subscription by user ID: {str(e)}")
        logger.exception("Full traceback:")
        raise HTTPException(status_code=500, detail=f"Error getting subscription by user ID: {str(e)}")
