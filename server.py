import os
import dotenv
import logging
import uvicorn
from datetime import datetime
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from src import utils
from src.payload import payLoad
from src.recommender import RecommenderEngine

logger = logging.getLogger()
logger.setLevel(logging.INFO)

is_loaded = dotenv.load_dotenv(".env")
if not is_loaded:
    logger.info("The env file is not loaded!")

artifact_url = os.getenv("ARTIFACTS_URL")
if artifact_url is not None:
    logger.info(f"ARTIFACTS_URL Env is {artifact_url}!")
    artitfact_root_dir = utils.download_s3_directory(artifact_url)
    logger.info(f"artitfact_root_dir is {artitfact_root_dir}!")
    aritifact_dir = os.path.join(artitfact_root_dir,'artifacts')
    logger.info(f"The downloaded aritifact dir is {aritifact_dir}")
else:
    raise Exception("ARTIFACTS_URL Env is not set!")

recommender_engine = RecommenderEngine(aritifact_dir=aritifact_dir)

app = FastAPI()


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

handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)