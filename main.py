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
    id: int
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


models_history=[[], [], [], [], [], [],]
models = [
    DicrisModel(id=1, name = 'Fire', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(id=2, name = 'Insulator', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(id=3, name = 'Voiceprocessing', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(id=4, name = 'Model 4', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(id=5, name = 'Model 5', status = StatusEnum.undefined, time = datetime.now()),
    DicrisModel(id=6, name = 'Model 6', status = StatusEnum.undefined, time = datetime.now()),
]
favicon_path = 'images/favicon.ico'


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = DicrisModel(id=0, name='', status=StatusEnum.undefined, time=datetime.now())
    try:
        with open("models.bin", 'rb') as f:
            try:
                while True:
                    model = pickle.load(f)
                    for idx, m in enumerate(models):
                        if model.name == m.name:
                            m_temp = models_history[model.id - 1]
                            m_temp.append(model.copy())
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
    model = DicrisModel(id=0, name='', status=StatusEnum.undefined, time=datetime.now())
    #models = app.state.models
    for idx, m in enumerate(models):
        if model_status.name == m.name:
            m.status = model_status.status
            m.time = datetime.now()
            models[idx] = m
            model = m
            m_temp = models_history[model.id - 1]
            m_temp.append(model.copy())
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


@app.get("/Fire.html", response_class=HTMLResponse)
async def fire(request: Request):
    context = {
        "name": "Fire",
        "models": models_history[0],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


@app.get("/Insulator.html", response_class=HTMLResponse)
async def model2(request: Request):
    context = {
        "name": "Insulator",
        "models": models_history[1],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


@app.get("/Voiceprocessing.html", response_class=HTMLResponse)
async def model3(request: Request):
    context = {
        "name": "Voiceprocessing",
        "models": models_history[2],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


@app.get("/Model 4.html", response_class=HTMLResponse)
async def model4(request: Request):
    context = {
        "name": "Model 4",
        "models": models_history[3],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


@app.get("/Model 5.html", response_class=HTMLResponse)
async def model5(request: Request):
    context = {
        "name": "Model 5",
        "models": models_history[4],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


@app.get("/Model 6.html", response_class=HTMLResponse)
async def model6(request: Request):
    context = {
        "name": "Model 6",
        "models": models_history[5],
    }
    return templates.TemplateResponse(
        request=request, name="model.html", context=context
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, ssl_keyfile="/etc/ssl/harica/dicris.sk.key", ssl_certfile="/etc/ssl/harica/dicris.sk.pem")
    #uvicorn.run("main:app", host="0.0.0.0", port=8000)