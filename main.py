import tkinter as tk
from tkinter import ttk
from config import *
from settings_manager import SettingsManager
from schedule_manager import ScheduleManager
from preset_manager import PresetManager
from tabs import LessonsTab, ClassesTab, ScheduleTab, PresetsTab

class SchoolSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Школьное расписание")
        self.root.geometry("1000x650")

        style = ttk.Style()
        style.theme_use('clam')  # более современный вид

        # менеджеры
        self.settings_mgr = SettingsManager()
        self.schedule_mgr = ScheduleManager()
        self.preset_mgr = PresetManager()

        # notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # вкладки
        self.lessons_tab = LessonsTab(self.notebook, self.settings_mgr, self)
        self.classes_tab = ClassesTab(self.notebook, self.settings_mgr, self)
        self.schedule_tab = ScheduleTab(self.notebook, self.settings_mgr, self.schedule_mgr, self)
        self.presets_tab = PresetsTab(self.notebook, self.preset_mgr, self.schedule_mgr, self.settings_mgr, self)

        self.notebook.add(self.lessons_tab, text="Уроки")
        self.notebook.add(self.classes_tab, text="Классы")
        self.notebook.add(self.schedule_tab, text="Расписание")
        self.notebook.add(self.presets_tab, text="Пресеты")

        # привязка события смены вкладки
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # При переключении на вкладку расписания обновляем и список уроков, и количество строк
        if self.notebook.select() == str(self.schedule_tab):
            self.schedule_tab.update_combobox_values()   # обновить выпадающие списки уроков
            self.schedule_tab.update_grid()              # перестроить таблицу с актуальными лимитами

    def refresh_schedule_comboboxes(self):
        self.schedule_tab.update_combobox_values()

    def refresh_schedule_display(self):
        self.schedule_tab.update_grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolSchedulerApp(root)
    root.mainloop()