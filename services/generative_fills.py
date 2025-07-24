from typing import Dict, Any, Optional
import requests
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BRIA_GEN_FILL_URL = "https://engine.prod.bria-api.com/v1/gen_fill"


def generative_fill(
    api_key: Optional[str] = None,
    image_data: bytes = None,
    mask_data: bytes = None,
    prompt: str = "",
    negative_prompt: Optional[str] = None,
    num_results: int = 4,
    sync: bool = False,
    seed: Optional[int] = None,
    content_moderation: bool = False,
    mask_type: str = "manual"
) -> Dict[str, Any]:
    """
    Fill masked areas of an image using generative AI with a text prompt.

    Args:
        api_key (Optional[str]): Bria API key. Falls back to BRIA_API_KEY env var if not provided.
        image_data (bytes): Input image data in bytes (base64 encoded before sending).
        mask_data (bytes): Mask image data in bytes (white = generate, black = keep).
        prompt (str): Text description for the fill (e.g., "add flowers on the table").
        negative_prompt (Optional[str]): Elements to avoid in generation (e.g., "no text").
        num_results (int): Number of variations to generate (1–4).
        sync (bool): Whether to wait for results (True) or get URLs immediately (False).
        seed (Optional[int]): Seed value for reproducibility.
        content_moderation (bool): Apply content moderation on output.
        mask_type (str): Mask mode ('manual' or 'automatic').

    Returns:
        Dict[str, Any]: API response JSON containing generated images or URLs.

    Raises:
        Exception: If API call fails or response is invalid.
    """
    # Resolve API key
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Convert image and mask to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    mask_base64 = base64.b64encode(mask_data).decode("utf-8")

    # Build request payload
    data = {
        'file': image_base64,
        'mask_file': mask_base64,
        'mask_type': mask_type,
        'prompt': prompt,
        'num_results': max(1, min(num_results, 4)),
        'sync': sync,
        'content_moderation': content_moderation
    }

    # Add optional parameters
    if negative_prompt:
        data['negative_prompt'] = negative_prompt
    if seed is not None:
        data['seed'] = seed

    try:
        logger.info("Sending generative fill request to Bria API...")
        response = requests.post(
            BRIA_GEN_FILL_URL,
            headers={
                'api_token': api_key,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            json=data,
            timeout=15
        )

        response.raise_for_status()
        logger.info("Generative fill request completed successfully.")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Generative fill request timed out.")
        raise Exception("Generative fill failed: Request timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error during generative fill: {http_err} | Response: {response.text}")
        raise Exception(f"Generative fill failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception during generative fill: {req_err}")
        raise Exception(f"Generative fill failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Invalid JSON response during generative fill: {json_err}")
        raise Exception("Generative fill failed: Invalid JSON response.")
