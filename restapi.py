from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="api")

class PostData(BaseModel):
    message: str

@app.post("/post")
async def create_post(data: PostData):
    """
    {
        "message": "test"
    }
    """
    return {
        "status": "success",
        "received_data": data
    }

#8468327124:AAF2N8PKXtAaAZuBSpMYGcEsdfeecrrkTaw