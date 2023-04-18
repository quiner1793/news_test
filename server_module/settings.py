import requests

import config as env


class Settings:
    host = env.SERVER_HOST
    port = int(env.SERVER_PORT)

    # redis_host = env.REDIS_HOST
    # redis_port = env.REDIS_PORT
    # redis_db = env.REDIS_DATABASE

    mongo_host = env.MONGO_HOST
    mongo_port = env.MONGO_PORT
    mongo_table = env.MONGO_TABLE
    mongo_data = env.MONGO_DATA

    news_api_key = env.NEWS_API_KEY

    r = requests.post('http://paraphraser.ru/token/',
                      data={'login': env.SYNONYMS_LOGIN, 'password': env.SYNONYMS_PASSWORD})
    synonyms_api_key = r.json().get('token', '')


settings = Settings()
