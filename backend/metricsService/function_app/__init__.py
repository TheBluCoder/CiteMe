import azure.functions as func
import logging
from main import app as fastapi_app  # Import the FastAPI app from app.py 
from dotenv import load_dotenv

load_dotenv()

async def main(req: func.HttpRequest, res:func.Out[func.HttpResponse]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = await func.AsgiMiddleware(app=fastapi_app).handle_async(req)
    res.set(response)