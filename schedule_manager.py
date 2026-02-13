import json
import os
from config import SCHEDULES_FILE, DAYS

class ScheduleManager:
    def __init__(self):
        self.schedules = {}
        self.load()

    def load(self):
        if os.path.exists(SCHEDULES_FILE):
            try:
                with open(SCHEDULES_FILE, 'r', encoding='utf-8') as f:
                    self.schedules = json.load(f)
            except Exception:
                self.schedules = {}

    def save(self):
        with open(SCHEDULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=4)

    def get_schedule(self, class_num):
        key = str(class_num)
        if key not in self.schedules:
            self.schedules[key] = {day: [] for day in DAYS}
        return self.schedules[key]

    def set_schedule(self, class_num, schedule_data):
        self.schedules[str(class_num)] = schedule_data
        self.save()

    def load_preset_into_class(self, class_num, preset_data):
        self.set_schedule(class_num, preset_data)