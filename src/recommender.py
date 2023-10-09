from typing import Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
import torch
from sklearn.utils import shuffle
from torch.utils.data import DataLoader

# pylint: disable=no-name-in-module,relative-beyond-top-level
from . import utils
from .dataset import RatingDataset
from .model import BSTRecommenderModel


class RecommenderEngine():
    def __init__(self, artifact_dir='./artifacts', batch_size=None, rating_threshold=4.5) -> None:
        self.artifact_dir = artifact_dir
        self.rating_threshold = rating_threshold
        self.config_dict = utils.open_json(
            f"{artifact_dir}/artifacts/config.json")

        self.config = utils.Config(dictionary=self.config_dict)

        if batch_size is not None:
            self.config.batch_size = int(batch_size)

        self.model = BSTRecommenderModel(config=self.config)
        self.sequence_length = self.config_dict['sequence_length']

        self.model.load_state_dict(
            torch.load(f"{artifact_dir}/model/pytorch_model.pt"))

        self.movie_id_map_dict = utils.open_object(
            f"{artifact_dir}/artifacts/movie_id_map_dict.pkl")
        self.movies_to_genres_dict = utils.open_object(
            f"{artifact_dir}/artifacts/movies_to_genres_dict.pkl")
        self.genres_map_dict = utils.open_object(
            f"{artifact_dir}/artifacts/genres_map_dict.pkl")
        self.age_group_id_map_dict = utils.open_object(
            f"{artifact_dir}/artifacts/age_group_id_map_dict.pkl")

        self.sex_id_map_dict = {"Male": 0.0, "Female": 1.0, "UNK": 0.5}
        self.rating_min_max_scaler = utils.open_object(
            f"{artifact_dir}/artifacts/rating_min_max_scaler.pkl")

        self.sorted_age_group_id_tuple = [(id_, limit) for id_, limit in sorted(
            self.age_group_id_map_dict.items(), key=lambda x: x[1]) if id_ != 'UNK']

        self.reverse_movie_id_map_dict = {remap_id: id_ for id_,
                                          remap_id in self.movie_id_map_dict.items()}

        self.movie_info = pd.read_parquet(
            f"{artifact_dir}/artifacts/movie_info.parquet")

        self.movie_info['genres'] = self.movie_info['genres'].apply(
            lambda x: x.tolist())

        self.movie_id_genre_dict = self.movie_info[['movie_id', 'genres']].set_index(
            "movie_id")['genres'].to_dict()

    @utils.timer
    def preprocess(self, movie_ids: List[int], user_age: int, sex: str) -> pd.DataFrame:

        df_input = pd.DataFrame()
        df_input["movie_id"] = df_input["target_movie"].map(
            self.reverse_movie_id_map_dict)

        # loop for each movie
        target_movies = list(self.movie_id_map_dict.values())
        target_movies.remove(self.movie_id_map_dict["UNK"])
        df_input["target_movie"] = target_movies

        # encode movie id
        df_input['movie_ids'] = [movie_ids.copy()
                                 for _ in range(len(df_input))]

        movie_sequence_ids = [self.movie_id_map_dict[id_] for id_ in movie_ids]

        df_input['movie_sequence'] = [movie_sequence_ids.copy()
                                      for _ in range(len(df_input))]

        # add target movie the last position of sequence
        _ = df_input.apply(lambda x: x['movie_sequence'].append(
            x['target_movie']), axis=1)

        # padding
        df_input["movie_sequence"] = df_input["movie_sequence"].apply(
            lambda x: x + self.sequence_length * [self.movie_id_map_dict["UNK"]])

        df_input["movie_sequence"] = df_input["movie_sequence"].apply(
            lambda x: x[:self.sequence_length]
        )

        # movie genres encoding
        self.movies_to_genres_dict[self.movie_id_map_dict['UNK']] = [
            self.genres_map_dict['UNK']]*len(self.movies_to_genres_dict[1])
        df_input['genres_ids_sequence'] = df_input['movie_sequence'].apply(
            lambda x: [self.movies_to_genres_dict[id_] for id_ in x])

        df_input['sex'] = self.sex_id_map_dict.get(
            sex, self.sex_id_map_dict['UNK'])

        age_group = self.age_to_age_group(user_age)
        age_group_index = self.age_group_id_map_dict[age_group]
        df_input['age_group_index'] = age_group_index

        return df_input

    def age_to_age_group(self, user_age: int):

        if user_age is None or (not isinstance(user_age, float) and not isinstance(user_age, int)):
            return "UNK"

        lower_limit = None
        for idx in range(0, len(self.sorted_age_group_id_tuple)-1):
            lower = self.sorted_age_group_id_tuple[idx][0]
            uppper = self.sorted_age_group_id_tuple[idx+1][0]
            # print(lower, uppper)
            if lower <= user_age < uppper:
                lower_limit = lower
                break

        if lower_limit is None:
            upper = self.sorted_age_group_id_tuple[-1][0]
            lower = self.sorted_age_group_id_tuple[0][0]
            if user_age >= upper:
                lower_limit = upper
            else:
                lower_limit = lower

        return lower_limit

    @utils.timer
    def inference(self, df_input, input_genres: Set, topk=5, rating_threshold: Optional[float] = None) -> pd.DataFrame:

        # Improve randomness
        df_output = shuffle(df_input.copy())
        inference_dataset = RatingDataset(data=df_output)
        inference_loader = DataLoader(
            inference_dataset, batch_size=self.config.batch_size, shuffle=False)
        cur_count = 0
        ratings_list = []
        with torch.no_grad():
            for inputs in inference_loader:
                probs = self.model(inputs)
                probs = probs.cpu().numpy()
                ratings = self.rating_min_max_scaler.inverse_transform(probs)[
                    :, 0]

                df_tmp = pd.DataFrame(ratings, columns=['predicted_rating'])
                df_tmp['movie_id'] = inputs["movie_id"].cpu().numpy()
                
                df_tmp['genres'] = df_tmp['movie_id'].map(
                    self.movie_id_genre_dict)

                rating_threshold = rating_threshold if rating_threshold else self.rating_threshold
                df_tmp = df_tmp[df_tmp["predicted_rating" >= rating_threshold]]
                df_tmp = df_tmp[]
                count = len(ratings[ratings >= rating_threshold])
                cur_count += count
                if cur_count >= topk:
                    # if number of movie with predicted rating >= rating threshold,
                    # is larger then topk,
                    # we stop recommending.
                    break

        predicted_ratings = np.concatenate(ratings_list)
        df_output = df_output.head(len(predicted_ratings)).copy()
        df_output['predicted_rating'] = predicted_ratings

        return df_output

    @utils.timer
    def postprocess(self, df_input, topk=5):

        df_input["movie_id"] = df_input["target_movie"].map(
            self.reverse_movie_id_map_dict)

        df_output = df_input.merge(self.movie_info, on=['movie_id'])

        # rating = df_output[['predicted_rating']].values
        # df_output['predicted_rating'] = self.rating_min_max_scaler.inverse_transform(rating)[
        #     :, 0]

        df_output = df_output.sort_values(
            by=['predicted_rating', 'release_year'], ascending=False)

        df_output = df_output[df_output.apply(
            lambda x:x['movie_id'] not in x['movie_ids'], axis=1)]

        selected_cols = list(self.movie_info.columns)+['predicted_rating']

        df_output = df_output[selected_cols]

        results = df_output.head(topk).to_dict(orient='records')

        return results

    def recommend(self, movie_ids: List[int], user_age: int, sex: str,
                  rating_threshold: float = 4.8, topk=5) -> List[Dict]:

        input_genres = set(self.movie_info[self.movie_info.movie_id.isin(
            movie_ids)]['genres'].explode())

        df_input = self.preprocess(
            movie_ids=movie_ids, user_age=user_age, sex=sex)

        df_inference = self.inference(
            df_input=df_input, topk=topk,
            rating_threshold=rating_threshold,
            input_genres=input_genres)

        outputs = self.postprocess(df_input=df_inference, topk=topk)

        return outputs
