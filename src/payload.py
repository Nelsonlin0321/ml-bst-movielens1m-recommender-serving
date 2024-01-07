from typing import List

from pydantic import BaseModel


class RecommendPayLoad(BaseModel):
    movie_ids: List[int] = [1, 2, 3, 4, 5]
    user_age: int = 20
    sex: str = 'M'
    topk: int = 3
    rating_threshold: float = 4.5


class ScoringPayLoad(BaseModel):
    viewed_movie_ids: List[int] = [1, 2, 3, 4, 5]
    suggested_movie_ids: List[int] = [6, 7, 8, 9, 10]
    user_age: int = 20
    sex: str = 'M'
