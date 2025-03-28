import azure.functions as func
import logging
from app import app as fastapi_app  # Import the FastAPI app from app.py 
from dotenv import load_dotenv

load_dotenv()

async def main(req: func.HttpRequest, res:func.Out[func.HttpResponse]) -> None:
    logging.info('Python HTTP trigger function processed a request.')
    response = await func.AsgiMiddleware(fastapi_app).handle_async(req)
    res.set(response)