from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SteamProduct(BaseModel):
    name: str
    app_id: int

    def to_dict(self) -> dict[str, str | int]:
        return {'name': self.name, 'app_id': self.app_id}


class Author(BaseModel):
    steam_id: int = Field(alias='steamid')
    num_games_owned: int
    num_reviews: int
    playtime_forever: int
    playtime_last_two_weeks: int
    playtime_at_review: int
    last_played: int


class SteamReview(BaseModel):
    recommendation_id: int = Field(alias="recommendationid")
    author: Author
    language: str
    review: str
    timestamp_created: datetime
    timestamp_updated: datetime
    voted_up: bool
    votes_up: int
    votes_funny: int
    weighted_vote_score: float
    comment_count: int
    steam_purchase: bool
    received_for_free: bool
    written_during_early_access: bool
    primarily_steam_deck: bool


class SteamQuerySummary(BaseModel):
    num_reviews: int
    review_score: Optional[float] = None
    review_score_desc: Optional[str] = None
    total_positive: Optional[int] = None
    total_negative: Optional[int] = None
    total_reviews: Optional[int] = None


class SteamReviews(BaseModel):
    success: int
    query_summary: SteamQuerySummary
    reviews: list[SteamReview]
    cursor: str


class CheatingSentiment(Enum):
    POSITIVE = 'positive'
    NOT_MENTIONED = 'not mentioned'
    NEGATIVE = 'negative'

    @classmethod
    def from_str(cls, s: str | None):
        if s is None:
            return None
        elif (s.lower() == 'positive'):
            return CheatingSentiment.POSITIVE
        elif s.lower() in ["not mentioned", "not_mentioned"]:
            return CheatingSentiment.NOT_MENTIONED
        elif s.lower() == 'negative':
            return CheatingSentiment.NEGATIVE

        return None


class FirestoreReview(BaseModel):
    sentiment: CheatingSentiment | None
    timestamp_created: datetime

    def to_dict(self) -> dict[str, str | None]:
        if self.sentiment is None:
            value = None
        else:
            value = self.sentiment.value

        return {"sentiment": value}


class ReviewWithSentiment(BaseModel):
    steam_product: SteamProduct
    steam_review: SteamReview
    cheating_sentiment: CheatingSentiment | None

    def to_firestore_review(self) -> FirestoreReview:
        return FirestoreReview(
            sentiment=self.cheating_sentiment,
            timestamp_created=self.steam_review.timestamp_created
        )
