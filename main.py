
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
import router

app = FastAPI()
app.include_router(router.router, prefix="",)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    # Use this line for auto reload after editing
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run("main:app", host="0.0.0.0", port=8000)