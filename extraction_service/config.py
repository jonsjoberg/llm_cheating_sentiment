from steam_product import SteamProduct

finals = SteamProduct(name="The FINALS", app_id=2073850)
arc = SteamProduct(name="ARC Raiders", app_id=1808500)
bf6 = SteamProduct(name="Battlefield™ 6", app_id=2807960)
cs2 = SteamProduct(name="Counter-Strike 2", app_id=730)
pubg = SteamProduct(name="PUBG: BATTLEGROUNDS", app_id=578080)
marvel = SteamProduct(name="Marvel Rivals", app_id=2767030)
tarkov = SteamProduct(name="Escape from Tarkov", app_id=3932890)

products_to_check: list[SteamProduct] = [finals, arc, bf6]

STEAM_REQUEST_PER_SECOND = 2
LLM_MAX_CONCURRENT = 10
LLM_MAX_REQUESTS_PER_SECOND = 10


FIREBASE_JSON = "cheating-sentiment-firebase-adminsdk.json"
DEFAULT_LOOKBACK_WINDOW_HOURS = 24 * 7
