import os
import sys

import dotenv

dotenv.load_dotenv("./.env")

curr_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(curr_dir)
sys.path.append(root_dir)

# pylint: disable=import-outside-toplevel


def test_download_artifact():

    from src.utils import download_s3_directory

    artifact_url = os.getenv("ARTIFACTS_URL")
    download_s3_directory(artifact_url)


def test_recommendation_endpoint():

    from src.recommender import RecommenderEngine

    recommender_engine = RecommenderEngine(artifact_dir='./artifacts')

    movie_ids = [1, 2, 3, 4]
    user_age = 23
    sex = "M"
    topk = 10
    rating_threshold = 4.8

    # pylint: disable=unexpected-keyword-arg
    results = recommender_engine.recommend(
        movie_ids=movie_ids, user_age=user_age,
        sex=sex, topk=topk, rating_threshold=rating_threshold)

    assert len(results) == topk


def test_get_scores_endpoint():

    from src.recommender import RecommenderEngine

    recommender_engine = RecommenderEngine(artifact_dir='./artifacts')

    viewed_movie_ids = [1, 2, 3, 4, 5]
    suggested_movie_ids = [5, 6, 7, 8, 9, 10]
    user_age = 23
    sex = "M"

    # pylint: disable=unexpected-keyword-arg
    results = recommender_engine.get_scores(
        viewed_movie_ids=viewed_movie_ids,
        user_age=user_age,
        sex=sex,
        suggested_movie_ids=suggested_movie_ids)

    assert len(results) == len(suggested_movie_ids)
