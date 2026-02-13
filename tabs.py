import tkinter as tk
from tkinter import ttk, messagebox
from config import DAYS

class LessonsTab(ttk.Frame):
    def __init__(self, parent, settings, app):
        super().__init__(parent)
        self.settings = settings
        self.app = app
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        list_frame = ttk.Frame(self)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(btn_frame, text="Название урока:").pack(pady=2)
        self.entry = ttk.Entry(btn_frame, width=20)
        self.entry.pack(pady=2)

        ttk.Button(btn_frame, text="Добавить", command=self.add).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Удалить", command=self.remove).pack(pady=2, fill=tk.X)
        ttk.Button(btn_frame, text="Редактировать", command=self.edit).pack(pady=2, fill=tk.X)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for lesson in self.settings.lessons:
            self.listbox.insert(tk.END, lesson)

    def add(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите название")
            return
        if self.settings.add_lesson(name):
            self.refresh_list()
            self.entry.delete(0, tk.END)
            self.app.refresh_schedule_comboboxes()
        else:
            messagebox.showerror("Ошибка", "Урок уже существует")

    def remove(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        lesson = self.listbox.get(sel[0])
        if messagebox.askyesno("Подтверждение", f"Удалить '{lesson}'?"):
            if self.settings.remove_lesson(lesson):
                self.refresh_list()
                self.app.refresh_schedule_comboboxes()

    def edit(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        old = self.listbox.get(sel[0])
        new = self.entry.get().strip()
        if not new:
            messagebox.showerror("Ошибка", "Введите новое название")
            return
        if self.settings.rename_lesson(old, new):
            self.refresh_list()
            self.entry.delete(0, tk.END)
            self.app.refresh_schedule_comboboxes()
        else:
            messagebox.showerror("Ошибка", "Не удалось переименовать (возможно, имя уже занято)")

class ClassesTab(ttk.Frame):
    def __init__(self, parent, settings, app):
        super().__init__(parent)
        self.settings = settings
        self.app = app
        self.vars = {}
        self.create_widgets()
        self.load_values()

    def create_widgets(self):
        ttk.Label(self, text="Максимальное количество уроков в день:").pack(pady=5)
        main = ttk.Frame(self)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        row = col = 0
        for c in range(1, 12):
            f = ttk.Frame(main)
            f.grid(row=row, column=col, padx=5, pady=2, sticky='w')
            ttk.Label(f, text=f"Класс {c}:").pack(side=tk.LEFT)
            var = tk.IntVar()
            spin = ttk.Spinbox(f, from_=1, to=10, textvariable=var, width=5)
            spin.pack(side=tk.LEFT, padx=5)
            self.vars[c] = var
            col += 1
            if col > 3:
                col = 0
                row += 1

        ttk.Button(self, text="Сохранить", command=self.save).pack(pady=10)

    def load_values(self):
        for c, var in self.vars.items():
            var.set(self.settings.max_lessons.get(str(c), 7))

    def save(self):
        for c, var in self.vars.items():
            self.settings.update_max_lessons(c, var.get())
        messagebox.showinfo("Сохранение", "Настройки сохранены")
        # 👇 Обновляем таблицу расписания сразу после изменения лимитов
        self.app.refresh_schedule_display()

class ScheduleTab(ttk.Frame):
    def __init__(self, parent, settings, schedule_mgr, app):
        super().__init__(parent)
        self.settings = settings
        self.schedule_mgr = schedule_mgr
        self.app = app
        self.current_class = tk.StringVar(value="1")
        self.comboboxes = []   # список строк, каждая строка - список комбобоксов
        self.create_widgets()

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(top, text="Класс:").pack(side=tk.LEFT)
        cb = ttk.Combobox(top, textvariable=self.current_class,
                          values=list(range(1,12)), state='readonly', width=5)
        cb.pack(side=tk.LEFT, padx=5)
        cb.bind('<<ComboboxSelected>>', self.on_class_change)

        ttk.Button(top, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Загрузить", command=self.load).pack(side=tk.LEFT, padx=5)
        ttk.Button(top, text="Очистить", command=self.clear).pack(side=tk.LEFT, padx=5)

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_grid()

    def on_class_change(self, event=None):
        self.update_grid()

    def clear(self):
        if messagebox.askyesno("Очистка", "Очистить всё расписание?"):
            for row in self.comboboxes:
                for cb in row:
                    cb.set('')
    
    def update_grid(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.comboboxes = []

        class_num = int(self.current_class.get())
        max_less = self.settings.max_lessons.get(str(class_num), 7)
        schedule = self.schedule_mgr.get_schedule(class_num)

        # заголовки
        ttk.Label(self.grid_frame, text="№", font=('Arial',10,'bold')).grid(row=0, column=0)
        for col, day in enumerate(DAYS):
            ttk.Label(self.grid_frame, text=day, font=('Arial',10,'bold')).grid(row=0, column=col+1)

        for row in range(1, max_less+1):
            ttk.Label(self.grid_frame, text=str(row)).grid(row=row, column=0)
            row_combos = []
            for col, day in enumerate(DAYS):
                var = tk.StringVar()
                day_lessons = schedule.get(day, [])
                if row-1 < len(day_lessons):
                    var.set(day_lessons[row-1])
                combo = ttk.Combobox(self.grid_frame, textvariable=var,
                                     values=self.settings.lessons, state='readonly', width=15)
                combo.grid(row=row, column=col+1, padx=2, pady=2)
                row_combos.append(combo)
            self.comboboxes.append(row_combos)
        print(f"Загружено расписание для класса {class_num}: {schedule}")

    def update_combobox_values(self):
        for row in self.comboboxes:
            for cb in row:
                cb['values'] = self.settings.lessons

    def save(self):
        class_num = int(self.current_class.get())
        schedule = {}
        for col, day in enumerate(DAYS):
            day_less = []
            for row in range(len(self.comboboxes)):
                day_less.append(self.comboboxes[row][col].get())
            schedule[day] = day_less
        self.schedule_mgr.set_schedule(class_num, schedule)
        messagebox.showinfo("Сохранение", f"Расписание для {class_num} класса сохранено")

    def load(self):
        import os
        import json
        from config import SCHEDULES_FILE
        if os.path.exists(SCHEDULES_FILE):
            try:
                with open(SCHEDULES_FILE, 'r', encoding='utf-8') as f:
                    self.schedules = json.load(f)
                self.schedule_mgr.load()          # загружаем данные из файла в менеджер
                self.update_grid()                 # обновляем таблицу для текущего класса
                print(f"✅ Расписание успешно загружено из {SCHEDULES_FILE}")
            except Exception as e:
                print(f"❌ ОШИБКА загрузки расписания: {e}")
                self.schedules = {}
        else:
            print(f"ℹ️ Файл {SCHEDULES_FILE} не найден, будет создан при сохранении")
            self.schedules = {}

class PresetsTab(ttk.Frame):
    def __init__(self, parent, preset_mgr, schedule_mgr, settings, app):
        super().__init__(parent)
        self.preset_mgr = preset_mgr
        self.schedule_mgr = schedule_mgr
        self.settings = settings
        self.app = app
        self.target_class = tk.IntVar(value=1)
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        list_frame = ttk.Frame(self)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scroll.set)

        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)

        ttk.Button(ctrl, text="Обновить список", command=self.refresh_list).pack(pady=5, fill=tk.X)

        ttk.Label(ctrl, text="Загрузить в класс:").pack(pady=2)
        ttk.Spinbox(ctrl, from_=1, to=11, textvariable=self.target_class, width=5).pack(pady=2)

        ttk.Button(ctrl, text="Загрузить пресет", command=self.load_preset).pack(pady=5, fill=tk.X)

        ttk.Separator(ctrl, orient='horizontal').pack(fill=tk.X, pady=5)

        ttk.Label(ctrl, text="Сохранить как пресет:").pack(pady=2)
        self.name_entry = ttk.Entry(ctrl, width=20)
        self.name_entry.pack(pady=2)
        ttk.Button(ctrl, text="Сохранить текущее", command=self.save_preset).pack(pady=5, fill=tk.X)

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for p in self.preset_mgr.list_presets():
            self.listbox.insert(tk.END, p)

    def load_preset(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showerror("Ошибка", "Выберите пресет")
            return
        name = self.listbox.get(sel[0])
        data = self.preset_mgr.load_preset(name)
        if data is None:
            messagebox.showerror("Ошибка", "Не удалось загрузить пресет")
            return
        target = self.target_class.get()
        self.schedule_mgr.load_preset_into_class(target, data)
        messagebox.showinfo("Успех", f"Пресет '{name}' загружен в {target} класс")
        self.app.refresh_schedule_display()  # обновим вкладку расписания

    def save_preset(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Ошибка", "Введите имя пресета")
            return

        # диалог выбора класса
        dlg = tk.Toplevel(self)
        dlg.title("Выберите класс")
        dlg.geometry("200x120")
        dlg.transient(self)
        dlg.grab_set()
        ttk.Label(dlg, text="Класс для сохранения:").pack(pady=5)
        var = tk.IntVar(value=1)
        ttk.Spinbox(dlg, from_=1, to=11, textvariable=var, width=5).pack(pady=5)

        def ok():
            cls = var.get()
            sched = self.schedule_mgr.get_schedule(cls)
            self.preset_mgr.save_preset(name, sched)
            self.refresh_list()
            dlg.destroy()
            messagebox.showinfo("Сохранение", f"Пресет '{name}' сохранён")

        ttk.Button(dlg, text="OK", command=ok).pack(pady=5)