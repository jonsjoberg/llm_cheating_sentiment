import json
from log import log
import httpx
from steam_product import SteamReview, SteamProduct
import os
from .client import LLMClient
from defined_types import ReviewWithSentiment, CheatingSentiment


LLM_MAX_CONCURRENT = 5
LLM_MAX_REQUESTS_PER_SECOND = 2


class OpenRouter(LLMClient):
    def __init__(self, model: str, base_prompt: str | None = None):
        if base_prompt is not None:
            self.base_prompt = base_prompt

        self.model = model

        self.api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if self.api_key is None:
            raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    def get_model(self):
        return self.model

    async def cheating_ref_in_review(
        self, review: SteamReview, steam_product: SteamProduct
    ) -> ReviewWithSentiment:
        prompt = self.generate_prompt(review)

        cheating_sentiment = None
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {
                            "type": "json_schema",
                            "json_schema": {
                                "name": "cheating_sentiment",
                                "strict": True,
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "cheating_sentiment": {
                                            "type": "string",
                                            "description": "The cheating sentiment in the review, either 'positive', 'negative' or 'not mentioned'",
                                        }
                                    },
                                },
                                "required": ["cheating_sentiment"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    timeout=240,
                )
                resp.raise_for_status()

            resp_json = resp.json()
            cheating_sentiment_dict = json.loads(
                resp_json["choices"][0]["message"]["content"]
            )
            cheating_sentiment = CheatingSentiment.from_str(
                cheating_sentiment_dict.get("cheating_sentiment")
            )
        except httpx.HTTPError as e:
            log.warning(
                f"HTTP error during OpenRouter request for review {review.recommendation_id}: {e}"
            )
        except json.JSONDecodeError as e:
            log.error(
                f"Failed to decode JSON from OpenRouter response for review {review.recommendation_id}: {e}"
            )
        except (KeyError, TypeError) as e:
            log.error(
                f"Unexpected JSON structure in OpenRouter response for review {review.recommendation_id}: {e}"
            )
        except Exception as e:
            log.error(
                f"Unexpected exception during OpenRouter request for review {review.recommendation_id}: {e}",
                exc_info=True
            )

        return ReviewWithSentiment(
            steam_product=steam_product,
            steam_review=review,
            cheating_sentiment=cheating_sentiment,
        )

    def close(self):
        pass
