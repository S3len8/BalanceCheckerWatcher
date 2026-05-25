from fastapi import FastAPI
import uvicorn


app = FastAPI()


@app.get("/")
async def get_data():
    return {"message": "Hello World!"}


@app.get("/items/")
async def get_items():
    return {"items": [1, 2, 3]} 


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)