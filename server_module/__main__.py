import uvicorn

from settings import settings

if __name__ == '__main__':
    uvicorn.run("server:app", host=settings.host, port=settings.port)
