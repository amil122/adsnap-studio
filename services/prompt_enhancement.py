import os
import logging
from typing import Optional, Any
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenRouter client using API key from environment variable
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),  
)

def enhance_prompt(
    prompt: str,
    referer_url: Optional[str] = None,
    site_title: Optional[str] = None,
    model: str = "mistralai/mistral-nemo:free",
    **kwargs: Any
) -> str:
    """
    Enhance a product description prompt for better ad generation using OpenRouter's free Gemma model.

    Args:
        prompt (str): Original product prompt.
        referer_url (Optional[str]): Site URL for OpenRouter rankings (optional).
        site_title (Optional[str]): Site title for OpenRouter rankings (optional).
        model (str): Model used for enhancement (default: google/gemma-3-4b-it:free).
        **kwargs: Extra parameters for customization.

    Returns:
        str: Enhanced prompt, or original prompt if enhancement fails.
    """
    try:
        if not client.api_key:
            logger.error("OpenRouter API key is missing. Set OPENROUTER_API_KEY in environment variables.")
            return prompt

        logger.info(f"Enhancing prompt using model {model} via OpenRouter")

        # Optional headers for OpenRouter rankings
        extra_headers = {}
        if referer_url:
            extra_headers["HTTP-Referer"] = referer_url
        if site_title:
            extra_headers["X-Title"] = site_title

        # Strong enhancement instruction
        system_instruction = (
            "You are an AI that specializes in marketing copywriting."
            "just enhance product descriptions to make them ideal for high-conversion advertisements. "
            "Focus on emotions, benefits, and a premium feel. Keep it concise but impactful."
        )

        # API call
        completion = client.chat.completions.create(
            extra_headers=extra_headers,
            model=model,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Enhance this product description: {prompt}"}
            ]
        )

        enhanced_prompt = completion.choices[0].message.content.strip()

        if enhanced_prompt:
            logger.info("Prompt enhancement successful.")
            return enhanced_prompt
        else:
            logger.warning("No enhancement returned. Using original prompt.")
            return prompt

    except Exception as e:
        logger.error(f"Error during prompt enhancement: {e}")
        return prompt
