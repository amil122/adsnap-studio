from typing import Dict, Any, Optional, List
import requests
import base64
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BRIA_TEXT_LIFESTYLE_URL = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_text"
BRIA_IMAGE_LIFESTYLE_URL = "https://engine.prod.bria-api.com/v1/product/lifestyle_shot_by_image"


def lifestyle_shot_by_text(
    api_key: Optional[str] = None,
    image_data: bytes = None,
    scene_description: str = "",
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    fast: bool = True,
    optimize_description: bool = True,
    original_quality: bool = False,
    exclude_elements: Optional[str] = None,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using a text description and product image.

    Args:
        api_key (Optional[str]): Bria API key. Defaults to BRIA_API_KEY env var.
        image_data (bytes): Product image data in bytes.
        scene_description (str): Description of lifestyle scene (e.g., "kitchen counter with sunlight").
        placement_type (str): Product placement mode: "original", "automatic", "manual_placement", "manual_padding", "custom_coordinates".
        num_results (int): Number of lifestyle images to generate.
        sync (bool): If True, waits for result; else returns placeholder URLs.
        fast (bool): Enables faster processing (less quality).
        optimize_description (bool): Enhances the scene description automatically.
        original_quality (bool): Preserves original image quality.
        exclude_elements (Optional[str]): Elements to exclude from the generated background.
        shot_size (List[int]): Output image size [width, height].
        manual_placement_selection (List[str]): Positions for manual placement.
        padding_values (List[int]): Padding [left, right, top, bottom].
        foreground_image_size (Optional[List[int]]): Foreground image size.
        foreground_image_location (Optional[List[int]]): Foreground image coordinates.
        force_rmbg (bool): Forces background removal.
        content_moderation (bool): Applies content moderation.
        sku (Optional[str]): SKU for product tracking.

    Returns:
        Dict[str, Any]: API response.

    Raises:
        Exception: If API request fails.
    """
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Convert image to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Prepare request payload
    data = {
        'file': image_base64,
        'scene_description': scene_description,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'fast': fast,
        'optimize_description': optimize_description,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation
    }

    # Optional fields
    if exclude_elements and not fast:
        data['exclude_elements'] = exclude_elements
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    if sku:
        data['sku'] = sku

    try:
        logger.info(f"Sending lifestyle shot (text) request to Bria API...")
        response = requests.post(BRIA_TEXT_LIFESTYLE_URL, headers={
            'api_token': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }, json=data, timeout=15)

        response.raise_for_status()
        logger.info("Lifestyle shot (text) generation successful.")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out.")
        raise Exception("Lifestyle shot generation failed due to timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err} | Response: {response.text}")
        raise Exception(f"Lifestyle shot generation failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise Exception(f"Lifestyle shot generation failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Invalid JSON response: {json_err}")
        raise Exception("Lifestyle shot generation failed: Invalid JSON response.")


def lifestyle_shot_by_image(
    api_key: Optional[str] = None,
    image_data: bytes = None,
    reference_image: bytes = None,
    placement_type: str = "original",
    num_results: int = 4,
    sync: bool = False,
    original_quality: bool = False,
    shot_size: List[int] = [1000, 1000],
    manual_placement_selection: List[str] = ["upper_left"],
    padding_values: List[int] = [0, 0, 0, 0],
    foreground_image_size: Optional[List[int]] = None,
    foreground_image_location: Optional[List[int]] = None,
    force_rmbg: bool = False,
    content_moderation: bool = False,
    sku: Optional[str] = None,
    enhance_ref_image: bool = True,
    ref_image_influence: float = 1.0
) -> Dict[str, Any]:
    """
    Generate a lifestyle shot using a reference image.

    Args:
        api_key (Optional[str]): Bria API key. Defaults to BRIA_API_KEY env var.
        image_data (bytes): Product image data.
        reference_image (bytes): Reference background image data.
        placement_type (str): Placement type (same as lifestyle_shot_by_text).
        num_results (int): Number of lifestyle shots to generate.
        sync (bool): If True, waits for results.
        original_quality (bool): Preserves original quality.
        shot_size (List[int]): Output dimensions [width, height].
        manual_placement_selection (List[str]): Manual placement positions.
        padding_values (List[int]): Padding values.
        foreground_image_size (Optional[List[int]]): Size of foreground object.
        foreground_image_location (Optional[List[int]]): Position of foreground object.
        force_rmbg (bool): Force background removal.
        content_moderation (bool): Enable moderation.
        sku (Optional[str]): SKU identifier.
        enhance_ref_image (bool): Enhance reference image quality.
        ref_image_influence (float): How much reference influences final output (0–1).

    Returns:
        Dict[str, Any]: API response.

    Raises:
        Exception: If request fails.
    """
    api_key = api_key or os.getenv("BRIA_API_KEY")
    if not api_key:
        raise ValueError("Bria API key is missing. Set BRIA_API_KEY in environment variables.")

    # Convert images to base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    reference_base64 = base64.b64encode(reference_image).decode("utf-8")

    # Prepare request payload
    data = {
        'file': image_base64,
        'ref_image_file': reference_base64,
        'placement_type': placement_type,
        'num_results': num_results,
        'sync': sync,
        'original_quality': original_quality,
        'force_rmbg': force_rmbg,
        'content_moderation': content_moderation,
        'enhance_ref_image': enhance_ref_image,
        'ref_image_influence': ref_image_influence
    }

    # Optional fields
    if placement_type in ['automatic', 'manual_placement', 'custom_coordinates']:
        data['shot_size'] = shot_size
    if placement_type == 'manual_placement':
        data['manual_placement_selection'] = manual_placement_selection
    if placement_type == 'manual_padding':
        data['padding_values'] = padding_values
    if placement_type == 'custom_coordinates':
        if foreground_image_size:
            data['foreground_image_size'] = foreground_image_size
        if foreground_image_location:
            data['foreground_image_location'] = foreground_image_location
    if sku:
        data['sku'] = sku

    try:
        logger.info(f"Sending lifestyle shot (image) request to Bria API...")
        response = requests.post(BRIA_IMAGE_LIFESTYLE_URL, headers={
            'api_token': api_key,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }, json=data, timeout=15)

        response.raise_for_status()
        logger.info("Lifestyle shot (image) generation successful.")
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("Request timed out.")
        raise Exception("Lifestyle shot generation failed due to timeout.")
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error: {http_err} | Response: {response.text}")
        raise Exception(f"Lifestyle shot generation failed: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request exception: {req_err}")
        raise Exception(f"Lifestyle shot generation failed: {req_err}")
    except ValueError as json_err:
        logger.error(f"Invalid JSON response: {json_err}")
        raise Exception("Lifestyle shot generation failed: Invalid JSON response.")


