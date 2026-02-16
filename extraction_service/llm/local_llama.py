import json
import httpx
from log import log
from defined_types import (
    SteamProduct,
    SteamReview,
    CheatingSentiment,
    ReviewWithSentiment,
)
from .client import LLMClient


class LocalLlama(LLMClient):
    # TODO: This shouldn't be hardcoded
    llm_url = "http://localhost:8080/v1/chat/completions"
    model = "Mistral-Small-3.1-24B-Instruct-2503-GGUF"

    def __init__(self, base_prompt: str | None = None):
        if base_prompt is not None:
            self.base_prompt = base_prompt
        pass

    def get_model(self) -> str:
        return self.model

    async def cheating_ref_in_review(
        self, review: SteamReview, steam_product: SteamProduct
    ) -> ReviewWithSentiment:

        prompt = self.generate_prompt(review)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self.llm_url,
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that only outputs correct JSON.",
                        },
                        {"role": "user", "content": prompt},
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
                                        "description": "The cheating sentiment in the review, either 'positive', 'negative' or 'not mentioned'",
                                    }
                                },
                            },
                            "required": ["cheating_sentiment"],
                            "additionalProperties": False,
                        },
                    },
                },
                timeout=120,
            )

            # resp.raise_for_status()
        if resp.is_error:
            log.warning(
                f"failed to extract sentiment for review: {review.recommendation_id} got error code: {resp.status_code} - {resp.reason_phrase}"
            )
            return ReviewWithSentiment(
                steam_product=steam_product,
                steam_review=review,
                cheating_sentiment=None,
            )

        resp_json = resp.json()

        cheating_sentiment = None
        try:
            cheating_sentiment_dict = json.loads(
                resp_json["choices"][0]["message"]["content"]
            )
            cheating_sentiment = CheatingSentiment.from_str(
                cheating_sentiment_dict.get("cheating_sentiment")
            )

        except KeyError as e:
            log.error(f"failed to find key: {e}")

        review_with_sentiment = ReviewWithSentiment(
            steam_product=steam_product,
            steam_review=review,
            cheating_sentiment=cheating_sentiment,
        )

        return review_with_sentiment

    def close(self):
        pass
