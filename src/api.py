from fastapi import FastAPI

app = FastAPI()


@app.post("/")
async def test():
    return {
        "status_code": 200,
        "message": "",
        "data": ""
    }
