import json
import os
from config import SETTINGS_FILE, DEFAULT_LESSONS, DEFAULT_MAX_LESSONS

class SettingsManager:
    def __init__(self):
        self.lessons = DEFAULT_LESSONS[:]
        self.max_lessons = DEFAULT_MAX_LESSONS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.lessons = data.get("lessons", DEFAULT_LESSONS[:])
                self.max_lessons = data.get("max_lessons_per_class", DEFAULT_MAX_LESSONS.copy())
                print("Настройки успешно загружены из", SETTINGS_FILE)  # временно для отладки
            except Exception as e:
                print(f"Ошибка загрузки {SETTINGS_FILE}: {e}")  # теперь вы увидите ошибку
                # остаются значения по умолчанию

    def save(self):
        data = {
            "lessons": self.lessons,
            "max_lessons_per_class": self.max_lessons
        }
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_lesson(self, lesson):
        if lesson and lesson not in self.lessons:
            self.lessons.append(lesson)
            self.save()
            return True
        return False

    def remove_lesson(self, lesson):
        if lesson in self.lessons:
            self.lessons.remove(lesson)
            self.save()
            return True
        return False

    def rename_lesson(self, old, new):
        if old in self.lessons and new and new not in self.lessons:
            idx = self.lessons.index(old)
            self.lessons[idx] = new
            self.save()
            return True
        return False

    def update_max_lessons(self, class_num, value):
        self.max_lessons[str(class_num)] = value
        self.save()