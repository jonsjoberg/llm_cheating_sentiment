from steam_product import SteamProduct

finals = SteamProduct(name="The FINALS", app_id=2073850)
arc = SteamProduct(name="ARC Raiders", app_id=1808500)
bf6 = SteamProduct(name="Battlefield™ 6", app_id=2807960)

products_to_check: list[SteamProduct] = [
    finals,
    arc,
    bf6
]

STEAM_REQUEST_PER_SECOND = 2
LLM_MAX_CONCURRENT = 10
LLM_MODEL = "nvidia/nemotron-nano-9b-v2:free"
FIREBASE_JSON = "cheating-sentiment-firebase-adminsdk-fbsvc-81f714302e.json"
DEFAULT_LOOKBACK_WINDOW_HOURS = 24
