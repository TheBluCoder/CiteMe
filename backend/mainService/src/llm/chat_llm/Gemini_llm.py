import os
from typing import List, Dict
from src.config.log_config import setup_logging
from google import genai
from google.genai import types
from src.llm.Instructions import MERGE_CITATION_INSTRUCTION 
import json

log_filename = os.path.basename(__file__)
logger = setup_logging(filename=log_filename)


class Genai_cite:
    model = "gemini-2.0-pro-exp-02-05"

    def __init__(self, api_key: str = os.getenv("GOOGLE_API_KEY"),
                 llm_model: str = f'models/{model}'):
        self.api_key = api_key
        self.client = genai.Client(api_key=self.api_key)
        self.llm_model = llm_model

    async def merge_citation(
            self, text: List[Dict[str, str]], format: str) -> Dict | bool:
        try:
            response = await self.client.aio.models.generate_content(
                model=self.llm_model,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
                contents=MERGE_CITATION_INSTRUCTION.format(text=text, format=format)
            )

            logger.info(f"usage: {response.usage_metadata}")

            # Parse the response text to JSON
            try:
                # Remove any potential markdown code block indicators
                clean_text = response.text.strip('`').replace(
                    'json\n', '').replace('\n', '')
                result = json.loads(clean_text)
                return result
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse LLM response as JSON: {je}")
                logger.debug(f"Raw response text: {response.text}")
                raise

        except Exception as e:
            logger.exception(f"Error in merging citation: {e}")
            raise e
