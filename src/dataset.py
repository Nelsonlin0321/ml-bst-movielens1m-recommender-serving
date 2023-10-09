import torch
from torch.utils.data import Dataset


class RatingDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.features_dtype_dict = {
            'target_rating': torch.float32,
            "sex": torch.float32,
            "target_movie": torch.long,
            "movie_sequence": torch.long,
            "genres_ids_sequence": torch.long,
            "age_group_index": torch.long
        }

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):

        item_dict = self.data.iloc[index].to_dict()

        # pylint: disable=no-member
        # dtype_dict = {}
        # for k, _ in item_dict.items():
        #     dtype_dict[k] = torch.long
        # dtype_dict["target_rating"] = torch.float32
        # dtype_dict["sex"] = torch.float32

        sample = {}
        for key, value in item_dict.items():
            if key in self.features_dtype_dict:
                sample[key] = torch.tensor(
                    value, dtype=self.features_dtype_dict[key]).to(self.device)
            else:
                sample[key] = value

        return sample
