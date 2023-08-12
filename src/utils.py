import pickle
import os
import json
import subprocess
import time
from tqdm import tqdm
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def save_json(json_object, file_path):
    with open(file_path, mode='w', encoding='utf-8') as f:
        json.dump(json_object, f, indent=4, ensure_ascii=False)


def open_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as f:
        json_object = json.load(f)
        return json_object


def open_object(object_path):
    with open(object_path, mode='rb') as f:
        obj = pickle.load(f)

    return obj


def save_object(object_path, obj):
    os.makedirs(os.path.dirname(object_path), exist_ok=True)
    with open(object_path, mode='wb') as f:
        pickle.dump(obj, f)


class Config:
    def __init__(self, dict):
        self.dict = dict
        for key, value in dict.items():
            setattr(self, key, value)


def download_s3_directory(s3_dir_path):

    output = subprocess.run(["aws", "s3", "cp", s3_dir_path,
                             "./", '--recursive'], capture_output=True)

    if output.returncode==1:
        raise Exception(output.stderr.decode("utf-8"))
    else:
        logger.info(output.stdout.decode("utf-8"))
        
    
    return os.path.abspath("./")

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        runtime = end_time - start_time
        runtime = round(runtime*1000,2)
        print(f"Runtime of {func.__name__}: {runtime} ms")
        return result
    return wrapper

def recursively_listdir(dir_path, extensions=[''], with_tqdm=False):

    dir_path = os.path.abspath(dir_path)
    if not os.path.isdir(dir_path):
        return [dir_path]

    file_list = []
    file_paths = listdir_with_full_path(dir_path)
    if with_tqdm:
        file_paths = tqdm(file_paths, position=0, leave=True,
                          desc=f"INFO: Scaning files under the folder {dir_path}")
    for file_path in file_paths:
        if os.path.isdir(file_path):
            file_list_under_dir = recursively_listdir(
                file_path, extensions, False)
            file_list.extend(file_list_under_dir)
        else:
            for ext in extensions:
                if file_path.endswith(ext):
                    file_list.append(file_path)
                    break
    return file_list

def listdir_with_full_path(dir_path):
    return [os.path.join(dir_path, path) for path in os.listdir(dir_path)]