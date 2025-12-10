import json
from core.utils import join_paths, path_exist, read_file

class Translation:
    def __init__(self, path_dir:str|list[str], default_lang:str):
        self.path_dir = join_paths(*path_dir) if isinstance(path_dir, list) else path_dir
        self.default_lang = default_lang

    def translate(self, filename:list[str]|str, keys:list[str]|str, lang:str|None = None, ):
        translations = {}
        filename = join_paths(*filename) if isinstance(filename, list) else filename

        if not isinstance(lang, str):
            lang = self.default_lang

        def get_path_file(language):
            return join_paths(self.path_dir, language, filename + '.json')

        path_file = get_path_file(lang)
        
        if not path_exist(path_file):
            path_file = get_path_file(self.default_lang)
        
        if not path_exist(path_file):
            return translations
        
        file = json.loads(read_file(path_file))

        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            try:
                translations[key] = file[key]
            except Exception as e:
                # print(e) implemente log
                translations[key] = ""

        return translations