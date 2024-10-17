import logging
import os
import sys
from datetime import datetime

import dotenv
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# from src import utils
from src.payload import RecommendPayLoad, ScoringPayLoad
from src.recommender import RecommenderEngine

logger = logging.getLogger()
logger.setLevel(logging.INFO)

IS_LOADED = dotenv.load_dotenv(".env")
if not IS_LOADED:
    logger.info("The env file is not loaded!")
else:
    logger.info("The env file is loaded!")

# artifact_url = os.getenv(
#     "ARTIFACTS_URL", "s3://s3-mlflow-artifacts-storage/mlflow/15/7008c7131367497a8dd99e2b2d506f96")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "256"))

# if artifact_url is not None:
#     logger.info("ARTIFACTS_URL Env is %s!", artifact_url)
#     artifact_root_dir = utils.download_s3_directory(artifact_url, "/tmp")
#     logger.info("artifact_root_dir is %s!", artifact_root_dir)
#     artifact_dir = os.path.join(artifact_root_dir, 'artifacts')
# else:
#     raise ValueError("ARTIFACTS_URL Env is not set!")

recommender_engine = RecommenderEngine(
    artifact_dir="./artifacts", batch_size=BATCH_SIZE, rating_threshold=4)

app = FastAPI()


@app.post("/recommend")
async def recommend(pay_load: RecommendPayLoad):
    # pylint: disable=unexpected-keyword-arg
    try:
        results = recommender_engine.recommend(
            movie_ids=pay_load.movie_ids, user_age=pay_load.user_age,
            sex=pay_load.sex, topk=pay_load.topk, rating_threshold=pay_load.rating_threshold)
    # # pylint: disable=broad-exception-caught,unused-variable,
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        error_message = f"An error occurred on line {line_number}: {str(e)}"
        logging.error(error_message)
        return HTTPException(status_code=500, detail=error_message)
    return results


@app.post("/get_scores")
async def get_scores(pay_load: ScoringPayLoad):
    # pylint: disable=unexpected-keyword-arg
    try:
        results = recommender_engine.get_scores(
            viewed_movie_ids=pay_load.viewed_movie_ids,
            suggested_movie_ids=pay_load.suggested_movie_ids,
            sex=pay_load.sex, user_age=pay_load.user_age)
    # # pylint: disable=broad-exception-caught,unused-variable,
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        line_number = exc_tb.tb_lineno
        error_message = f"An error occurred on line {line_number}: {str(e)}"
        return HTTPException(status_code=500, detail=error_message)
    return results


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
start_time = datetime.utcnow()
start_time = start_time.strftime(DATE_FORMAT)


@app.get("/healthcheck")
async def healthcheck():
    response = f'The server is up since {start_time}'
    return {"message": response, 'start_uct_time': start_time}

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
