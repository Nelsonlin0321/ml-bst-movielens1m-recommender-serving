import torch
from .model import BSTRecommenderModel
from . import utils
from typing import List, Dict
import pandas as pd
from .dataset import RatingDataset
from torch.utils.data import DataLoader
import numpy as np


class RecommenderEngine():
    def __init__(self, artifact_dir='./artifacts', batch_size=None) -> None:
        self.artifact_dir = artifact_dir

        self.config_dict = utils.open_json(
            f"{artifact_dir}/artifacts/config.json")

        self.config = utils.Config(dict=self.config_dict)

        if batch_size is not None:
            self.config.batch_size = batch_size

        self.recommende_model = BSTRecommenderModel(config=self.config)
        self.sequence_length = self.config_dict['sequence_length']

        self.recommende_model.load_state_dict(
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

    @utils.timer
    def preprocess(self, movie_ids: List[int], user_age: int, sex: str) -> pd.DataFrame:

        df_input = pd.DataFrame()

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
    def inference(self, df_input) -> pd.DataFrame:

        inference_dataset = RatingDataset(data=df_input)
        inference_loader = DataLoader(
            inference_dataset, batch_size=self.config.batch_size, shuffle=False)

        probs_list = []
        for inputs in inference_loader:
            with torch.no_grad():
                probs = self.recommende_model(inputs)
                probs_list.append(probs.cpu().numpy())

        df_input['rating'] = np.concatenate(probs_list)[:, 0]

        return df_input

    @utils.timer
    def postprocess(self, df_input, topk=5):

        df_input["movie_id"] = df_input["target_movie"].map(
            self.reverse_movie_id_map_dict)

        df_output = df_input.merge(self.movie_info, on=['movie_id'])

        rating = df_output[['rating']].values
        df_output['rating'] = self.rating_min_max_scaler.inverse_transform(rating)[
            :, 0]

        df_output = df_output.sort_values(
            by=['rating', 'release_year'], ascending=False)

        df_output = df_output[df_output.apply(
            lambda x:x['movie_id'] not in x['movie_ids'], axis=1)]

        selected_cols = list(self.movie_info.columns)+['rating']

        df_output = df_output[selected_cols]

        results = df_output.head(topk).to_dict(orient='records')

        return results

    def recommend(self, movie_ids: List[int], user_age: int, sex: str, topk=5) -> List[Dict]:
        df_input = self.preprocess(
            movie_ids=movie_ids, user_age=user_age, sex=sex)

        df_inference = self.inference(df_input=df_input)

        outputs = self.postprocess(df_input=df_inference, topk=topk)

        return outputs
