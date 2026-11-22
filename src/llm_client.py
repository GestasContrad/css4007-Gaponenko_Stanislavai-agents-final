import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError, APIError
from pydantic import ValidationError

from src.schemas import StructuredPaperAnalysis

load_dotenv()

SYSTEM_PROMPT = (
    "You are the Scholarly Research Paper & Document Finder Agent. "
    "You help students and researchers find academic papers, understand methodologies, "
    "and analyze experimental benchmarks accurately without hallucinating facts or citations."
)

STRUCTURED_ANALYSIS_SYSTEM_PROMPT = (
    "You are an academic research assistant. Given verified metadata and benchmark metrics "
    "for a scientific paper, return ONLY a valid JSON object matching these exact keys:\n"
    "- paper_id (string)\n"
    "- title (string)\n"
    "- research_area (string)\n"
    "- key_contributions (list of 2-3 concise strings)\n"
    "- reported_metrics (object mapping metric names to string scores, strictly from the provided data)\n"
    "- practical_takeaway (concise 1-2 sentence string)\n"
    "Do not invent metrics or facts that are not present in the provided paper data."
)


class LLMClient:
    """Wrapper around the OpenAI Chat Completions API with validation and error handling."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")

        if not self.api_key or not self.api_key.strip():
            raise ValueError(
                "Missing API key. Set LLM_API_KEY in your .env file or environment variables."
            )

        self.client = OpenAI(api_key=self.api_key)

    def build_messages(
        self, user_prompt: str, system_prompt: str = SYSTEM_PROMPT
    ) -> List[Dict[str, str]]:
        """Validates user input and constructs the message payload for the LLM."""
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise ValueError("User prompt must be a non-empty string.")

        return [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()},
        ]

    def generate_response(
        self,
        user_prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Sends a chat completion request to OpenAI and validates the response."""
        try:
            messages = self.build_messages(user_prompt, system_prompt)
        except ValueError as val_err:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": str(val_err),
            }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
            )

            if not response.choices or not response.choices[0].message.content:
                return {
                    "success": False,
                    "model": self.model,
                    "content": None,
                    "error": "Empty response received from the language model.",
                }

            content = response.choices[0].message.content.strip()
            return {
                "success": True,
                "model": response.model,
                "content": content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "error": None,
            }

        except AuthenticationError:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": "Authentication failed: Invalid LLM_API_KEY.",
            }
        except RateLimitError:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": "Rate limit exceeded or insufficient OpenAI quota.",
            }
        except APIConnectionError:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": "Network error: Could not connect to OpenAI API.",
            }
        except APIError as api_err:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": f"OpenAI API error: {api_err}",
            }
        except Exception as exc:
            return {
                "success": False,
                "model": self.model,
                "content": None,
                "error": f"Unexpected error during LLM call: {exc}",
            }

    def generate_structured_analysis(
        self,
        paper_details: Dict[str, Any],
        paper_metrics: Dict[str, Any],
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """Generates and validates a structured JSON analysis for a retrieved paper."""
        if not isinstance(paper_details, dict) or "paper_id" not in paper_details:
            return {
                "success": False,
                "model": self.model,
                "data": None,
                "error": "Invalid paper_details payload provided.",
            }

        user_prompt = (
            "Generate a structured JSON analysis for the following paper.\n\n"
            f"Paper Details:\n{json.dumps(paper_details, indent=2)}\n\n"
            f"Paper Metrics:\n{json.dumps(paper_metrics, indent=2)}"
        )

        try:
            messages = self.build_messages(user_prompt, STRUCTURED_ANALYSIS_SYSTEM_PROMPT)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )

            if not response.choices or not response.choices[0].message.content:
                return {
                    "success": False,
                    "model": self.model,
                    "data": None,
                    "error": "Empty structured response received from LLM.",
                }

            raw_json = response.choices[0].message.content.strip()
            parsed = json.loads(raw_json)
            validated = StructuredPaperAnalysis.model_validate(parsed)

            return {
                "success": True,
                "model": response.model,
                "data": validated.model_dump(),
                "error": None,
            }

        except json.JSONDecodeError as json_err:
            return {
                "success": False,
                "model": self.model,
                "data": None,
                "error": f"LLM returned invalid JSON: {json_err}",
            }
        except ValidationError as val_err:
            return {
                "success": False,
                "model": self.model,
                "data": None,
                "error": f"Structured output schema validation failed: {val_err}",
            }
        except (AuthenticationError, RateLimitError, APIConnectionError, APIError) as api_err:
            return {
                "success": False,
                "model": self.model,
                "data": None,
                "error": f"OpenAI API error: {api_err}",
            }
        except Exception as exc:
            return {
                "success": False,
                "model": self.model,
                "data": None,
                "error": f"Unexpected error during structured analysis: {exc}",
            }