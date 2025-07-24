from typing import Dict, Any, Optional
import requests
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BRIA_ERASE_FOREGROUND_URL = "https://engine.prod.bria-api.com/v1/erase_foreground"


def erase_foreground(
    api_key: Optional[str] = None,
    image_data: bytes = None,
    image_url: str = None,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Remove the main foreground object from an image and generate
    a realistic background to fill the erased area.

    Args:
        api_key (Optional[str]): Bria API key (falls back to BRIA_API_KEY env var if not provided).
        image_data (bytes): Image data in bytes (used if image_url is not provided).
        image_url (str): URL of the image (used if image_data is not provided).
        content_moderation (bool): Whether to apply content moderation filters.

    Returns:
        Dict[str, Any]: JSON response from the API containing the generated image details.

    Raises:
        ValueError: If neither `image_data` nor `image_url` is provided.
        Exception: For network or API errors.
    """
    # Resolve API key
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Validate image input
    if not image_data and not image_url:
        raise ValueError("Either image_data or image_url must be provided.")

    # Build payload
    data = {
        'content_moderation': content_moderation
    }

    if image_url:
        data['image_url'] = image_url
    else:
        data['file'] = base64.b64encode(image_data).decode('utf-8')

    try:
        logger.info("Sending erase foreground request to Bria API...")
        response = requests.post(
            BRIA_ERASE_FOREGROUND_URL,
            headers={
                'api_token': api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=15
        )

        response.raise_for_status()
        logger.info("Erase foreground request successful.")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Erase foreground request timed out.")
        raise Exception("Erase foreground failed: Request timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during erase foreground: {http_err} | Response: {response.text}")
        raise Exception(f"Erase foreground failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception during erase foreground: {req_err}")
        raise Exception(f"Erase foreground failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Invalid JSON response during erase foreground: {json_err}")
        raise Exception("Erase foreground failed: Invalid JSON response.")



# Export function
__all__ = ['erase_foreground']


