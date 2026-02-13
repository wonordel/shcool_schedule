import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
SCHEDULES_FILE = os.path.join(BASE_DIR, "schedules.json")
PRESET_DIR = os.path.join(BASE_DIR, "preset")

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
CLASSES = list(range(1, 12))

DEFAULT_MAX_LESSONS = {str(c): 7 for c in CLASSES}
DEFAULT_LESSONS = [
    "Математика", "Русский язык", "Литература", "Физика", "Химия",
    "Биология", "История", "Обществознание", "География", "Английский язык",
    "Физкультура", "ИЗО", "Музыка", "Труд", "ОБЖ", "Информатика"
]