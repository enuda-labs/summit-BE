# """
# Module for handling OTP (One-Time Password) processing and email sending functionality.
# This module provides functions to send OTP verification emails to users.
# """

# import json
# import logging
# from typing import Dict, Any

# import requests
# from django.conf import settings
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# logger = logging.getLogger(__name__)

# SMTP_API_URL = p
# SMTP_API_SECRET = settings.SMTP_API_SECRET
# SMTP_SENDER_EMAIL = settings.SMTP_SENDER_EMAIL


# def send_email(otp: int, recipient_name: str, recipient_email: str) -> JsonResponse:
#     """
#     Send an OTP verification email to the specified recipient.

#     Args:
#         otp (int): The one-time password to be sent
#         recipient_name (str): Name of the email recipient
#         recipient_email (str): Email address of the recipient

#     Returns:
#         JsonResponse: Response indicating success or failure of the email sending operation
#     """
#     try:
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {SMTP_API_SECRET}"
#         }

#         payload: Dict[str, Any] = {
#             "subject": "OTP Verification",
#             "template": {
#                 "id": "43rWHH9qPrB4fr9UaQqTG",
#                 "variables": {
#                     "oTP": str(otp)
#                 }
#             },
#             "sender": {
#                 "name": "Milestone",
#                 "email": SMTP_SENDER_EMAIL
#             },
#             "recipients": {
#                 "name": recipient_name,
#                 "email": recipient_email
#             }
#         }

#         response = requests.post(SMTP_API_URL, headers=headers, json=payload)

#         if response.status_code == 200:
#             logger.info("Email sent successfully to %s", recipient_email)
#             return JsonResponse({"status": "success", "message": "Email sent successfully"})
        
#         logger.error("Failed to send email to %s: %s", recipient_email, response.json())
#         return JsonResponse(
#             {"status": "error", "message": "Failed to send email"},
#             status=response.status_code
#         )

#     except requests.RequestException as e:
#         logger.error("Error sending email: %s", str(e))
#         return JsonResponse(
#             {"status": "error", "message": "Failed to send email due to network error"},
#             status=500
#         )
#     except Exception as e:
#         logger.error("Unexpected error sending email: %s", str(e))
#         return JsonResponse(
#             {"status": "error", "message": "An unexpected error occurred"},
#             status=500
#         )