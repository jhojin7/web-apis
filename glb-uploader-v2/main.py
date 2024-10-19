# fastapi dev main.py
from pymongo import MongoClient
from fastapi import FastAPI, UploadFile, File, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException


def get_models_db():
    (db_name, collection_name) = "data", "model"
    try:
        client = MongoClient("mongodb://localhost:27017/")
        models_db = client.get_database(db_name)
        models_coll = models_db.get_collection(collection_name)
        return models_coll
    except Exception as e:
        raise e


app = FastAPI()


@app.get("/")
def main():
    html_str = open("./index.html", "r", encoding="utf-8").read()
    return HTMLResponse(html_str)


@app.get("/models", dependencies=[Depends(get_models_db)])
def get_all_models():
    db = get_models_db()
    db_res = list(db.find({}))
    return [x["name"] for x in db_res]


@app.post("/models/upload", dependencies=[Depends(get_models_db)])
def upload_one_model(
    glb_file: UploadFile = File(...),
    file_name: str = Form(...),
    thumbnail_file: UploadFile = File(...),
):
    request_data = [file_name, glb_file, thumbnail_file]
    print(request_data)
    db = get_models_db()

    db_result = list(db.find({"name": file_name}))
    if len(list(db_result)) > 0:
        print(db_result)
        # print(*db_result, sep="\n") # ffffffuuuu....
        raise HTTPException(
            400, "duplicate file name exists"
        )  # ValueError: [TypeError("'ObjectId' object is not iterable"), TypeError('vars() argument must have __dict__ attribute')]
    db_model = {
        "name": file_name,
        "glb_file": glb_file.filename,
        "thumbnail_file": thumbnail_file.filename,
        "type": "PROPERTY",
    }
    db.insert_one(db_model)
    print(db_model)
    return file_name
