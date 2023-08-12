import os
import dotenv
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from src import utils
from src.payload import payLoad
from src.recommender import RecommenderEngine

logger = logging.getLogger()


is_loaded = dotenv.load_dotenv(".env")
if not is_loaded:
    logging.warn("token crendential is not loaded")


artifact_url = os.getenv("ARTIFACTS_URL")
if artifact_url is not None:
    utils.download_s3_directory(artifact_url)
recommender_engine = RecommenderEngine(aritifact_dir='./artifacts')

app = FastAPI()
handler = Mangum(app)

@app.post("/recommend")
async def recommend(pay_load: payLoad):
    try:
        results = recommender_engine.recommend(
            movie_ids=pay_load.movie_ids, user_age=pay_load.user_age,
            sex=pay_load.sex, topk=pay_load.topk)
    except Exception as e:
        logging.error(e)
        return HTTPException(status_code=404, detail=str(e))
    return results


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = datetime.utcnow()
start_time = start_time.strftime(DATE_FORMAT)


@app.get("/healthcheck")
async def healthcheck():
    response = f'The server is up since {start_time}'
    return {"message": response, 'start_uct_time': start_time}
