import os
import dotenv
import sys
dotenv.load_dotenv("./.env")

curr_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(curr_dir)
sys.path.append(root_dir)


def test_download_artifact():

    from src.utils import download_s3_directory

    artifact_url = os.getenv("ARTIFACTS_URL")
    download_s3_directory(artifact_url)


def test_model_serving():

    from src.recommender import RecommenderEngine

    recommender_engine = RecommenderEngine(artifact_dir='./artifacts')

    movie_ids = [1, 2, 3, 4]
    user_age = 23
    sex = "M"
    topk = 10

    results = recommender_engine.recommend(
        movie_ids=movie_ids, user_age=user_age,
        sex=sex, topk=topk)

    assert len(results) == topk
