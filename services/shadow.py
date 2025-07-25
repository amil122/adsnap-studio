from typing import Dict, Any, List, Optional
import requests
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BRIA_SHADOW_URL = "https://engine.prod.bria-api.com/v1/product/shadow"

def add_shadow(
    api_key: Optional[str] = None,
    image_data: bytes = None,
    image_url: str = None,
    shadow_type: str = "regular",
    background_color: Optional[str] = None,
    shadow_color: str = "#000000",
    shadow_offset: List[int] = [0, 15],
    shadow_intensity: int = 60,
    shadow_blur: Optional[int] = None,
    shadow_width: Optional[int] = None,
    shadow_height: Optional[int] = 70,
    sku: Optional[str] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False
) -> Dict[str, Any]:
    """
    Add shadow to an image using Bria AI's shadow API.

    Args:
        api_key (Optional[str]): Bria API key. Defaults to BRIA_API_KEY env var.
        image_data (bytes): Raw image data (optional if image_url is provided).
        image_url (str): URL to an existing image (optional if image_data is provided).
        shadow_type (str): Shadow type ("regular" or "float").
        background_color (Optional[str]): Background color in hex format.
        shadow_color (str): Shadow color in hex format.
        shadow_offset (List[int]): [x, y] offset for the shadow.
        shadow_intensity (int): Shadow opacity percentage (0–100).
        shadow_blur (Optional[int]): Blur radius for the shadow.
        shadow_width (Optional[int]): Width for float shadows.
        shadow_height (Optional[int]): Height for float shadows.
        sku (Optional[str]): SKU identifier for tracking.
        force_rmbg (bool): Force background removal if transparency exists.
        content_moderation (bool): Enable content moderation for input.

    Returns:
        Dict[str, Any]: JSON response from Bria API.

    Raises:
        Exception: If no image data/url provided or API call fails.
    """

    # Resolve API key from env if not passed
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Prepare headers
    headers = {
        'api_token': api_key,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Prepare request data
    data = {
        'shadow_type': shadow_type,
        'shadow_color': shadow_color,
        'shadow_intensity': shadow_intensity,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation,
        'shadow_offset': shadow_offset
    }

    # Add image source
    if image_url:
        data['image_url'] = image_url
    elif image_data:
        data['file'] = base64.b64encode(image_data).decode('utf-8')
    else:
        raise ValueError("Either image_data or image_url must be provided")

    # Optional params
    if background_color:
        data['background_color'] = background_color
    if shadow_blur is not None:
        data['shadow_blur'] = shadow_blur
    if shadow_width is not None:
        data['shadow_width'] = shadow_width
    if shadow_height is not None:
        data['shadow_height'] = shadow_height
    if sku:
        data['sku'] = sku

    try:
        logger.info(f"Sending shadow addition request to {BRIA_SHADOW_URL}")

        response = requests.post(BRIA_SHADOW_URL, headers=headers, json=data, timeout=15)
        response.raise_for_status()

        logger.info(f"Shadow addition successful (status {response.status_code})")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Shadow API request timed out.")
        raise Exception("Shadow addition failed due to timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err} | Response: {response.text}")
        raise Exception(f"Shadow addition failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise Exception(f"Shadow addition failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Failed to parse JSON response: {json_err}")
        raise Exception("Shadow addition failed: Invalid JSON response.")
