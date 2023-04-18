## Для запуска нужно создать файл config.py где нужно указать данные в таком формате:

SERVER_HOST = 

SERVER_PORT = 

MONGO_HOST = 

MONGO_PORT = 

MONGO_TABLE = 

MONGO_WORDS = 

MONGO_FORMS = 

SYNONYMS_LOGIN = 

SYNONYMS_PASSWORD = 

NEWS_API_KEY = 


## Примечания:

search возвращает json новостей объедененных по скорам, чем больше score тем лучше новость подходит для данного query.


API синонимов работает только с русскими словами


В общей концепции я использовал алгоритм в котором учитываются синонимы и их формы
