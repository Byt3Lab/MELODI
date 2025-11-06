def read_file(path_file: str, mode="r") -> str:
    if not path_exist(path_file):
        raise FileNotFoundError(f"The file at {path_file} does not exist.")
    
    if not (mode == "r" or mode == "ra") :
        mode = "r"
        
    with open(path_file, 'r') as file:
        return file.read()
    

def get_file(path_file: str) -> str:
    if not path_exist(path_file):
        raise FileNotFoundError(f"The file at {path_file} does not exist.")
    
    return open(path_file, 'r')
    
def write_file(path_file: str, content: str, mode="w") -> None:
    if not (mode == "w" or mode == "a" or mode == "wb" or mode == "ab") :
        mode = "w"

    with open(path_file, mode=mode) as file:
        file.write(content)

import os

def join_paths(*paths: str) -> str:
    return os.path.join(*paths)

def path_exist(*paths: str):
    return os.path.exists(*paths)

def list_dir(path_dir:str):
    return os.listdir(path=path_dir) 

def create_dir(path_dir, parents=True, exist_ok=True):
    from pathlib import Path
    Path(path_dir).mkdir(parents, exist_ok)

def create_dir_if_not_exist(path_dir, parents=True, exist_ok=True):
    if path_exist(path_dir):
        return
    
    create_dir(path_dir, parents, exist_ok)


from .storage   import  Storage
from .timer_manager import TimerManager   
from .event_listener import EventListener   
from .translation import Translation 