from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from enum import Enum
from pydantic import BaseModel
from datetime import datetime

import uvicorn

import pickle


class StatusEnum(str, Enum):
    undefined = 'undefined'
    moderate = 'moderate'
    warning = 'warning'
    critical = 'critical'
    ok = 'ok'


class DicrisModel(BaseModel):
    name: str
    status: StatusEnum
    time: datetime
    class Config:  
        use_enum_values = True


class ModelStatus(BaseModel):
    name: str
    status: StatusEnum
    class Config:  
        use_enum_values = True

models = [
    DicrisModel(name = 'Model 1', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(name = 'Model 2', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(name = 'Model 3', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(name = 'Model 4', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(name = 'Model 5', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(name = 'Model 6', status = StatusEnum.undefined, time = datetime.now()),
]
favicon_path = '/images/favicon.ico'


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = DicrisModel(name='', status=StatusEnum.undefined, time=datetime.now())
    try:
        with open("models.bin", 'rb') as f:
            try:
                while True:
                    model = pickle.load(f)
                    for idx, m in enumerate(models):
                        if model.name == m.name:
                            models[idx] = model
                            break
            except EOFError:
                f.close()
                pass
    except IOError:
        pass
    #app.state.models = models
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")
templates = Jinja2Templates(directory="templates")


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get("/models")
async def get_models():
    return models


@app.get("/model")
async def get_model(name:str):
    for m in models:
        if m.name == name:
            return m
    return 


@app.post("/models", status_code=201)
async def add_status_model(model_status: ModelStatus):
    model = DicrisModel(name='', status=StatusEnum.undefined, time=datetime.now())
    #models = app.state.models
    for idx, m in enumerate(models):
        if model_status.name == m.name:
            m.status = model_status.status
            m.time = datetime.now()
            models[idx] = m
            model = m
            pickle.dump(m, open("models.bin", "ab+"))
            break
    if model.name =='':
        return 
    else:
        return model


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context = {
        "models": models,
    }
    return templates.TemplateResponse(
        request=request, name="models.html", context=context
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, ssl_keyfile="/etc/ssl/harica/dicris.sk.key", ssl_certfile="/etc/ssl/harica/dicris.sk.pem")
    #uvicorn.run("main:app", host="0.0.0.0", port=8000)