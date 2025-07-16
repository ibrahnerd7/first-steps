from typing import  Union
from fastapi import  FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name , "message": "Deep Learning FTW!"}
    if model_name  == 'resnet':
        return {"model_name": model_name , "message": "LeCNN all the images"}
    return {"model_name": model_name , "message": "Have some residuals"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q:Union[int, str] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item:Item):
    return {"item_name": item.price, "item_id": item_id}

@app.get("/files/{file_path}")
def read_file(file_path: str):
    return {"file_path": file_path}