import json
import requests

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from settings import settings

app = FastAPI()

mongo_client = MongoClient(f"mongodb://{settings.mongo_host}:{settings.mongo_port}")

mongo_db = mongo_client[settings.mongo_table]
mongo_words = mongo_db[settings.mongo_data]


def make_404_response(text):
    response = {"Status code": 404, "Details": text}
    return json.dumps(response)


def make_200_response(text):
    response = {"Status code": 200, "Details": text}
    return json.dumps(response)


def get_synonyms_api(word):
    payload = {'c': 'syns',
               'query': word,
               'top': 10,
               'scores': 0,
               'forms': 0,
               'format': 'json',
               'lang': 'ru',
               'token': settings.synonyms_api_key}

    r = requests.post('http://paraphraser.ru/api/',
                      data=payload)
    response = r.json()

    if response["code"] == 0:
        result = response["response"]["1"]["syns"]
        print(result)
        return result

    return None


## Look for cached results, request if not cached
def check_synonym(word):
    result = mongo_words.find_one({"word": word})

    if result is None:
        synonyms = get_synonyms_api(word)

        if synonyms:
            _ = mongo_words.insert_one({"word": word, "synonyms": synonyms})
            result = synonyms
    else:
        result = result["synonyms"]

    return result


@app.get("/synonyms/{word}")
async def synonyms_manager(word: str):
    if word is None:
        return JSONResponse(make_404_response("No word provided"))
    else:
        result = check_synonym(word)

        if result:
            return JSONResponse(make_200_response(result))
        else:
            return JSONResponse(make_404_response("No synonyms found"))


@app.get("/search/{query}")
async def news_manager(query: str):
    if query is None:
        return JSONResponse(make_404_response("No query provided"))
    else:
        return JSONResponse(make_200_response("Ok"))
