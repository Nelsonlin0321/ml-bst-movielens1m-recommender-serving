from typing import List
from pydantic import BaseModel


class payLoad(BaseModel):
    movie_ids: List[int] = [1, 2, 3, 4, 5]
    user_age: int = 20
    sex: str = 'M'
    topk: int = 3
