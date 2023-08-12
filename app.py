import os
import json
import dotenv
import logging
from src import utils
from src.recommender import RecommenderEngine

logger = logging.getLogger()

is_loaded = dotenv.load_dotenv(".env")
if not is_loaded:
    logging.warn("token crendential is not loaded")


artifact_url = os.getenv("ARTIFACTS_URL")
if artifact_url is not None:
    utils.download_s3_directory(artifact_url)
recommender_engine = RecommenderEngine(aritifact_dir='./artifacts')


def lambda_handler(event, context):

    try:
        results = recommender_engine.recommend(
                    movie_ids=event['movie_ids'], user_age=event.get('user_age'),
                    sex=event.get('sex'), topk=event.get('topk',10))
        
    except Exception as e:
        
        logging.error(e)

        return {
            "status_code": 500,
            "message": str(e)
        }
    
    return {
            "status_code": 200,
            "prediction": results
        }
