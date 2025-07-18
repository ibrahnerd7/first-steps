from typing import  Union, Annotated, Literal
from fastapi import  FastAPI, Query, Path, Body
from pydantic import BaseModel, AfterValidator, Field, HttpUrl
from enum import Enum

from pygments.lexers import q

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class User(BaseModel):
    username: str
    full_name: str | None = None

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
def read_item(
        item_id: Annotated[int, Path(title="The ID of the item to get", ge=1, le=1000)],
        q:str | None = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(
        item_id: int,
        item:Item,
        user: User,
        importance: Annotated[int, Body(example=['One', 'Two', 'Three', 'Four'])],):
    return {"item_name": item.price, "item_id": item_id, "user": user, "importance": importance}

@app.get("/files/{file_path}")
def read_file(file_path: str):
    return {"file_path": file_path}

fake_items_db =[
    {
        "item_name": "Foo"
    },
    {
        "item_name": "Bar"
    },
    {
        "item_name": "Baz"
    }
]
@app.get("/items/")
async def read_item(skip:int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str, q:str = None, short: bool = False):
    item  = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item

class Image(BaseModel):
    url: HttpUrl
    name: str

class Item2(BaseModel):
    name: str
    description: str | None = Field(
        default=None,title = "The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None

class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item2]

@app.post("/offers")
async def create_offer(offer: Offer):
    return offer

@app.post("/offers/{item_id}")
async def create_multiple_images(images: list[Image]):
    return images

@app.post("/index-weights")
async  def create_index_weights(weights: dict[int, float]):
    return weights
@app.post("/items2/")
async  def create_item(item:Item2):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price * item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items2/{item_id}")
async def update_item(
        item_id:int,
        item:Item2, q:str |None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

@app.get("/items3/")
async def read_items(q: Annotated[str |None, Query(min_length=3,max_length=50, pattern="^fixedquery$")] ):
    results = [{"items": "Foo"}, {"item_id": "Bar"}]
    if q:
        results.update({"q": q})
    return results

data = {
    "isbn-9781529046137": "The Hitchhiker's Guide to the Galaxy",
    "imdb-tt0371724": "The Hitchhiker's Guide to the Galaxy",
    "isbn-9781439512982": "Isaac Asimov: The Complete Stories, Vol. 2",
}
def check_is_valid_id(id: str):
    if not id.startswith("isbn", "imdb-"):
        raise ValueError('Invalid ID format, it must start with "isbn-" or "imdb-"')
    return id

@app.get("/books")
async def read_books(
        id: Annotated[str | None,AfterValidator(check_is_valid_id)] = None,
):
    if id:
        item = data.get(id)
    else:
        id, item = random.choice(list(data.items()))
    return {"id": id, "item": item}

class FilterParams(BaseModel):
    # model_config = {"etra", "forbid"}
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, gt=0)
    order_by: Literal["price", "name"]
    tags: list[str] = []
@app.get("/items4/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query