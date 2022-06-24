import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from docs_gen import construct_plantuml_link_list


def get_description() -> str:
    description = construct_plantuml_link_list()
    return description


app = FastAPI(
    title="plantuml-integration",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    description=get_description(),
    default_response_class=ORJSONResponse,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
