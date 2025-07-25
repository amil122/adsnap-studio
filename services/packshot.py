import os
import base64
import logging
from typing import Dict, Any, Optional
import requests

# Configure centralized logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BRIA_PACKSHOT_URL = "https://engine.prod.bria-api.com/v1/product/packshot"


def create_packshot(
    image_data: bytes,
    background_color: str = "#FFFFFF",
    sku: Optional[str] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a professional packshot (clean product photo) using Bria AI.

    Args:
        image_data (bytes): Image data in bytes.
        background_color (str): Background color (hex or 'transparent').
        sku (Optional[str]): Optional SKU identifier for tracking.
        force_rmbg (bool): Force background removal even if image has alpha.
        content_moderation (bool): Apply content moderation on output.
        api_key (Optional[str]): Bria API key (defaults to OPENROUTER_API_KEY env var).

    Returns:
        Dict[str, Any]: API response as a dictionary.

    Raises:
        Exception: If API key is missing or request fails.
    """
    # Retrieve API key securely from environment if not passed
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Prepare headers
    headers = {
        "api_token": api_key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # Encode image to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Build request payload
    data = {
        "file": image_base64,
        "background_color": background_color,
        "force_rmbg": force_rmbg,
        "content_moderation": content_moderation,
    }

    if sku:
        data["sku"] = sku

    try:
        logger.info(f"Sending packshot creation request to Bria API...")

        response = requests.post(BRIA_PACKSHOT_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()

        result = response.json()
        logger.info("Packshot creation successful.")

        return result

    except requests.exceptions.Timeout:
        logger.error("Bria API request timed out.")
        raise Exception("Packshot creation failed due to timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err} | Response: {response.text}")
        raise Exception(f"Packshot creation failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise Exception(f"Packshot creation failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Failed to parse JSON response: {json_err}")
        raise Exception("Packshot creation failed: Invalid JSON response.")
