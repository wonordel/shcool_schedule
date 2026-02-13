import os
import json
from config import PRESET_DIR

class PresetManager:
    def __init__(self):
        if not os.path.exists(PRESET_DIR):
            os.makedirs(PRESET_DIR)

    def list_presets(self):
        files = os.listdir(PRESET_DIR)
        return [os.path.splitext(f)[0] for f in files if f.endswith('.json')]

    def load_preset(self, name):
        path = os.path.join(PRESET_DIR, name + '.json')
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_preset(self, name, data):
        if not os.path.exists(PRESET_DIR):
            os.makedirs(PRESET_DIR)
        path = os.path.join(PRESET_DIR, name + '.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)