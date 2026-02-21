from datetime import datetime, timezone
from defined_types import Author, SteamReview, SteamProduct


def generate_mock_author() -> Author:
    return Author(
        steamid=0,
        num_games_owned=0,
        num_reviews=0,
        playtime_forever=0,
        playtime_last_two_weeks=0,
        playtime_at_review=0,
        last_played=0,
    )


def generate_mock_review(review_text: str) -> SteamReview:
    return SteamReview(
        recommendationid=0,
        author=generate_mock_author(),
        language="en",
        review=review_text,
        timestamp_created=datetime.now(tz=timezone.utc),
        timestamp_updated=datetime.now(tz=timezone.utc),
        voted_up=True,
        votes_up=0,
        votes_funny=0,
        weighted_vote_score=0,
        comment_count=0,
        steam_purchase=True,
        received_for_free=False,
        written_during_early_access=False,
        primarily_steam_deck=False,
    )


def generate_mock_steam_product() -> SteamProduct:
    return SteamProduct(name="test product", app_id=0)
