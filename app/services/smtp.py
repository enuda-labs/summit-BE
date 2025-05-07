"""
Module for handling OTP (One-Time Password) processing and email sending functionality.
This module provides functions to send OTP verification emails to users.
"""

import json
import os
import logging
from typing import Dict, Any
import aiohttp
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)



SMTP_API_URL = os.getenv("SMTP_API_URL")
SMTP_API_SECRET = os.getenv("SMTP_API_SECRET")
SMTP_SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL")

print("SMTP_API_URL: ", SMTP_API_URL)

async def send_email(otp: str, recipient_name: str, recipient_email: str) -> Dict[str, Any]:
    """
    Send an OTP verification email to the specified recipient.

    Args:
        otp (str): The one-time password to be sent
        recipient_name (str): Name of the email recipient
        recipient_email (str): Email address of the recipient

    Returns:
        Dict[str, Any]: Response indicating success or failure of the email sending operation
    """
    try:
        # Ensure OTP is a string
        otp_str = str(otp).strip()
        if not otp_str:
            raise ValueError("OTP cannot be empty")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SMTP_API_SECRET}"
        }

        payload: Dict[str, Any] = {
            "subject": "OTP Verification",
            "template": {
                "id": "kn0hHMisavgApISFQZnsh",
                "variables": {
                    "oTP": otp_str
                }
            },
            "sender": {
                "name": "Summit",
                "email": SMTP_SENDER_EMAIL
            },
            "recipients": {
                "name": recipient_name,
                "email": recipient_email
            }
        }

        logger.debug("Sending email with payload: %s", json.dumps(payload))

        async with aiohttp.ClientSession() as session:
            async with session.post(SMTP_API_URL, headers=headers, json=payload) as response:
                response_text = await response.text()
                if response.status == 200:
                    logger.info("Email sent successfully to %s", recipient_email)
                    return {"status": "success", "message": "Email sent successfully"}
                
                logger.error("Failed to send email to %s: %s", recipient_email, response_text)
                raise HTTPException(
                    status_code=response.status,
                    detail="Failed to send email"
                )

    except aiohttp.ClientError as e:
        logger.error("Error sending email: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to send email due to network error"
        )
    except Exception as e:
        logger.error("Unexpected error sending email: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while sending email"
        )