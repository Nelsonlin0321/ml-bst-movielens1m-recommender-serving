import torch
import pandas as pd
from torch.utils.data import Dataset


class RatingDataset(Dataset):
    def __init__(self, data: pd.DataFrame):
        self.label = "target_rating"

        self.features_dtype_dict = {
            self.label: torch.float32,
            "sex": torch.float32,
            "target_movie": torch.long,
            "movie_sequence": torch.long,
            "genres_ids_sequence": torch.long,
            "age_group_index": torch.long
        }
        selected_columns = list(self.features_dtype_dict)
        if self.label not in data.columns:
            selected_columns.remove(self.label)
        self.data = data[selected_columns].copy()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):

        item_dict = self.data.iloc[index].to_dict()

        # pylint: disable=no-member

        sample = {}
        for key, value in item_dict.items():
            sample[key] = torch.tensor(
                value, dtype=self.features_dtype_dict[key]).to(self.device)

        return sample
