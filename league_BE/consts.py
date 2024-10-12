
class BaseConstants:

    BASE_LIVE_URL_FEED = 'https://feed.lolesports.com/livestats/v1/window/{}?startingTime={}'

    TIME_DELTA_S = 1

    CURRENT_STATIC_DATA_VERSION = "1451"

    # G2 vs MDK, game 2
    TEST_MATCH_ID = 111997906552170268

    # 2 hours behind the time here
    # https://lol.fandom.com/wiki/LEC/2024_Season/Spring_Playoffs/Scoreboards
    TEST_MIN_START_TIME = '2024-03-31 17:37:00+00:00'

    BASE_TB_POST_URL = 'https://api.eu-central-1.aws.tinybird.co/v0/events'