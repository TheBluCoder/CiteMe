from groq import Groq
import os
import re
import json
from src.config.log_config import setup_logging
from typing import Optional
from json.decoder import JSONDecodeError
from src.custom_exceptions.llm_exceptions import SearchKeyGenerationError

filename = os.path.basename(__file__)
logger = setup_logging(filename=filename)


class Summarize_llm:

    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY"),
                 llm_model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.client = Groq(api_key=self.api_key)
        self.llm_model = llm_model

    def getKeywordSearchTerm(self, document: str) -> Optional[str]:
        """
        Generate a search term from the provided document using LLM.

        Args:
            document: Input text to generate search term from

        Returns:
            str: Generated search term or error message

        Raises:
            LLMError: If there's an error in LLM processing
        """
        try:
            # Input validation
            if not document or not isinstance(document, str):
                logger.warning("Invalid or empty document provided")
                return "No content to summarize"

            # Trim document if too long
            max_length = 4000  # Adjust based on model's context window
            if len(document) > max_length:
                logger.warning(f"Document truncated from {len(document)} to {max_length} characters")
                document = document[:max_length]

            # Make API call with error handling

            completion = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {
                        "role": "user",
                        "content": f"summarize the provided into a google search term and return a json response as 'search_term : value', if no content provided, your response should be 'message:no content to summarize'. Here is the content: {document}"
                    },
                ],
                temperature=0.9,
                top_p=1,
                max_tokens=1024,
                stream=False,
                stop=None,
                response_format={"type": "json_object"}
            )
            result = completion.choices[0].message.content
            return json.loads(result).get(
                "search_term") or json.loads(result).get("message")
        except JSONDecodeError:
            logger.error("Failed to decode JSON response")
            result = re.sub(
                r'^(```json\n|```|json|\n|\{)|(```|\n|\})$', '', result)
            return result

        except Exception as e:
            logger.error(f"Unexpected error in getKeywordSearchTerm: {str(e)}")
            raise SearchKeyGenerationError(f"Unexpected error: {str(e)}")
