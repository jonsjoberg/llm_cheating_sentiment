import json
from log import log
import httpx
from steam_product import SteamReview, SteamProduct
import os
from .client import LLMClient, ReviewWithSentiment, CheatingSentiment


DEVSTRAL_FREE = "mistralai/devstral-2512:free"


class OpenRouter(LLMClient):

    def __init__(self, model: str):
        self.model = model

        self.api_key = os.getenv("OPEN_ROUTER_API_KEY")
        if self.api_key is None:
            raise RuntimeError("OPEN_ROUTER_API_KEY is missing")

    def get_model(self):
        return self.model

    async def cheating_ref_in_review(
        self,
        review: SteamReview,
        steam_product: SteamProduct
    ) -> ReviewWithSentiment:
        prompt = self.generate_prompt(review)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": 'application/json',
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
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
                                        "description": "The cheating sentiment in the review, either 'positive', 'negative' or 'not mentioned'"
                                    }
                                }
                            },
                            "required": ["cheating_sentiment"],
                            "additionalProperties": False,
                        }
                    }
                },
                timeout=60
            )
            resp.raise_for_status()

        resp_json = resp.json()
        # TODO: Prettify this

        cheating_sentiment = None
        try:
            cheating_sentiment_dict = json.loads(
                resp_json['choices'][0]['message']['content'])
            cheating_sentiment = CheatingSentiment.from_str(
                cheating_sentiment_dict.get("cheating_sentiment"))

        except KeyError as e:
            log.error(f"failed to find key: {e}")

        review_with_sentiment = ReviewWithSentiment(
            steam_product=steam_product,
            steam_review=review,
            cheating_sentiment=cheating_sentiment
        )

        return review_with_sentiment

    def close(self):
        pass
