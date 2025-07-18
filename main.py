import hashlib
from typing import  Union, Annotated, Literal, Any
from fastapi import  FastAPI, Query, Path, Body, Cookie, Header,Form, File, UploadFile
from pydantic import BaseModel, AfterValidator, Field, HttpUrl
from enum import Enum
from uuid import UUID
from datetime import datetime, timedelta, time

from pygments.lexers import q
from watchfiles.run import start_process

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

@app.put("/items/more-dts")
async  def more_dts(
        item_id: UUID,
        start_datetime: Annotated[datetime, Body()],
        end_datetime: Annotated[datetime, Body()],
        process_after:Annotated[timedelta, Body()],
        repeat_at:Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        start_datetime: start_datetime,
        end_datetime: end_datetime,
        process_after: process_after,
        repeat_at: repeat_at,
        start_process: start_process,
        duration: duration,
    }

class Cookies(BaseModel):
    model_config = {"extra":"forbid"}
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None
@app.get("/cookies/")
async def read_cookies(cookies: Annotated[Cookies, Cookie()] = None):
    return cookies

class CommonHeaders(BaseModel):
    model_config = {"extra":"forbid"}
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []
@app.get('/headers/')
async def get_headers(user_agent: Annotated[CommonHeaders, Header(convert_underscores=False)] = None):
    return {"User-Agent": user_agent}

class UserIn(BaseModel):
    username: str
    password: str
    email: str
    full_name: str |  None = None

class UserOut(BaseModel):
    username: str
    email: str
    full_name: str | None = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: str
    full_name: str | None = None

def fake_password_hasher(raw_password: str) -> str:
    return "supersecret" + raw_password

def fake_save_user(user_in,UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password= hashed_password)
    print("User saved! ..not really")
    return user_in_db

def create_fake_user(user_in):
    user_saved = fake_save_user(user_in)
    return user_saved

@app.post("/users-io/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user

@app.post("/login/", response_model=UserOut)
async def login(username:Annotated[str, Form()], password:Annotated[str, Form()]):
    return {"username": username}

class FormData(BaseModel):
    username: str
    password: str
    model_config = {"extra":"forbid"}

@app.post("/forms/")
async def create_form(data: Annotated[FormData, Form()]):
    return data

@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}

@app.post("/uploadfile/")
async def create_upload_file(file: Annotated[bytes, File(description="A file read as UploadFile")]):
    return {"file_size": file.filename}


@app.post("/upload-files-1")
async def create_file(
        file: Annotated[bytes, File(description="A file read as UploadFile")],
        fileb: Annotated[bytes, File()] = Body(None),
        token: Annotated[str, Form()] = Body(None),
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }