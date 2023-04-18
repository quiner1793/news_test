import json
import requests

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient

from settings import settings

app = FastAPI()

mongo_client = MongoClient(f"mongodb://{settings.mongo_host}:{settings.mongo_port}")

mongo_db = mongo_client[settings.mongo_table]
mongo_words = mongo_db[settings.mongo_words]
mongo_forms = mongo_db[settings.mongo_forms]


def make_404_response(text):
    response = {"Status code": 404, "Details": text}
    return json.dumps(response)


def make_200_response(text):
    response = {"Status code": 200, "Details": text}
    return json.dumps(response)


def get_synonyms_api(word: str):
    payload = {'c': 'syns',
               'query': word,
               'top': 10,
               'scores': 1,
               'forms': 1,
               'format': 'json',
               'lang': 'ru',
               'token': settings.synonyms_api_key}

    r = requests.post('http://paraphraser.ru/api/',
                      data=payload)
    response = r.json()

    if response["code"] == 0:
        result = response["response"]["1"]
        return result

    return None


def get_news_api(query: str):
    query = query.lower()

    url = f"https://newsapi.org/v2/everything?q={query}&sortBy=popularity&apiKey={settings.news_api_key}"
    r = requests.get(url)
    response = r.json()

    return response


def give_score_news(article, query):
    words = query.lower().split(" ")
    score = 0
    for word in words:
        synonyms = check_synonym(word)
        for synonym in synonyms:
            forms = mongo_forms.find_one({"form": synonym[0]})["forms"]

            for form in forms:
                if form.lower() in article['title'].lower() or form.lower() in article['description'].lower():
                    score += synonym[1]

    return score


## Look for cached results, request if not cached
def check_synonym(word):
    word = word.lower()

    result = mongo_words.find_one({"word": word})

    if result is None:
        api_result = get_synonyms_api(word)
        synonyms = api_result["syns"]
        forms = api_result["forms"]
        for form in forms:
            for word_form in form:
                if not mongo_forms.find_one({"form": word_form}):
                    mongo_forms.insert_one({"form": word_form, "forms": form[word_form]})

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
        response = get_news_api(query)

        result = {}
        if response["status"] == "ok" and response["totalResults"] > 0:
            for article in response["articles"]:
                result[give_score_news(article, query)] = article
            print(result.keys())
            return JSONResponse(make_200_response(result))
        else:
            return JSONResponse(make_404_response("Nothing was found"))