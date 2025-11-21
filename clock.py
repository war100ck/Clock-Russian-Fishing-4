import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
import os
import sys
import json
import pygame
from tkinter import messagebox

class AlarmWidget:
    def __init__(self, parent, alarm_data, on_drag_start, on_drag_stop, on_drag, on_click, signal_on_icon, signal_off_icon):
        self.parent = parent
        self.alarm_data = alarm_data
        self.on_drag_start = on_drag_start
        self.on_drag_stop = on_drag_stop
        self.on_drag = on_drag
        self.on_click = on_click
        self.signal_on_icon = signal_on_icon
        self.signal_off_icon = signal_off_icon
        
        self.create_widget()
    
    def create_widget(self):
        """Создает отдельный виджет для будильника"""
        self.widget = tk.Toplevel(self.parent)
        self.widget.title(f"Будильник {self.alarm_data['time']}")
        self.widget.geometry("200x40")  # Такая же ширина как у основного окна
        self.widget.resizable(False, False)
        self.widget.configure(bg='#2b2b2b')
        self.widget.overrideredirect(True)
        self.widget.attributes('-topmost', True)
        self.widget.attributes('-alpha', 0.9)
        
        # Основной фрейм виджета
        main_frame = tk.Frame(self.widget, bg='#2b2b2b', padx=10, pady=5)
        main_frame.pack(fill='both', expand=True)
        
        # Иконка сигнала (изначально выключенная)
        self.icon_label = tk.Label(
            main_frame,
            image=self.signal_off_icon,
            bg='#2b2b2b'
        )
        self.icon_label.pack(side='left', padx=(0, 10))
        
        # Метка с информацией о будильнике
        self.alarm_label = tk.Label(
            main_frame,
            text=f"{self.alarm_data['time']} - {self.alarm_data['name']}",
            font=("Arial", 10),
            fg='#ffffff',
            bg='#2b2b2b',
            cursor="hand2"
        )
        self.alarm_label.pack(side='left', fill='both', expand=True)
        
        # Привязываем события перемещения
        self.bind_drag_events()
        
        # Привязываем клик для остановки
        self.alarm_label.bind("<Button-1>", self.on_click)
        self.icon_label.bind("<Button-1>", self.on_click)
    
    def bind_drag_events(self):
        """Привязывает события перемещения к виджету"""
        self.alarm_label.bind("<ButtonPress-1>", self.on_drag_start)
        self.alarm_label.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.alarm_label.bind("<B1-Motion>", self.on_drag)
        
        self.icon_label.bind("<ButtonPress-1>", self.on_drag_start)
        self.icon_label.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.icon_label.bind("<B1-Motion>", self.on_drag)
        
        self.widget.bind("<ButtonPress-1>", self.on_drag_start)
        self.widget.bind("<ButtonRelease-1>", self.on_drag_stop)
        self.widget.bind("<B1-Motion>", self.on_drag)
    
    def update_position(self, x, y):
        """Обновляет позицию виджета"""
        self.widget.geometry(f"+{x}+{y}")
    
    def destroy(self):
        """Уничтожает виджет"""
        self.widget.destroy()
    
    def set_alarm_active(self, active):
        """Устанавливает состояние активного будильника через смену иконок"""
        if active:
            # Включенное состояние - красная иконка
            self.icon_label.config(image=self.signal_on_icon)
        else:
            # Выключенное состояние - белая иконка
            self.icon_label.config(image=self.signal_off_icon)

class GameClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Игровые часы")
        self.root.geometry("200x100")
        self.root.resizable(False, False)
        self.root.configure(bg='#2b2b2b')
        
        # Убираем стандартные рамки окна
        self.root.overrideredirect(True)
        
        # Всегда поверх всех окон
        self.root.attributes('-topmost', True)
        
        # Настройки времени
        self.real_time_ratio = 2.5  # 2.5 реальных минуты = 1 игровой час
        
        # База для синхронизации - начало текущего реального часа
        self.sync_base = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        # Инициализация pygame для звука
        pygame.mixer.init()
        
        # Настройки будильника
        self.alarms = []
        self.alarm_widgets = []
        self.sound_playing = False
        self.active_alarm = None
        self.flash_state = False
        
        # Переменные для перемещения
        self.drag_data = {"x": 0, "y": 0, "widget": None}
        
        # Загружаем настройки
        self.load_settings()
        
        # Загружаем иконки
        self.load_icons()
        
        self.create_widgets()
        self.create_alarm_widgets()
        self.update_time()
        
        # Добавляем возможность перемещения окна
        self.bind_drag_events()
    
    def get_resource_path(self, relative_path):
        """Получает правильный путь к ресурсам как в EXE так и в скрипте"""
        try:
            # PyInstaller создает временную папку и хранит путь в _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def get_data_path(self, filename):
        """Получает путь для файлов данных (в папке с EXE)"""
        if getattr(sys, 'frozen', False):
            # Если запущено как EXE
            base_path = os.path.dirname(sys.executable)
        else:
            # Если запущено как скрипт
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, filename)
    
    def load_icons(self):
        """Загружает иконки дня и ночи"""
        try:
            # Используем правильные пути для ресурсов
            day_path = self.get_resource_path("day.png")
            night_path = self.get_resource_path("night.png")
            settings_path = self.get_resource_path("setting.png")
            setting_black_path = self.get_resource_path("setting_black.png")
            signal_on_path = self.get_resource_path("signal_on.png")
            signal_off_path = self.get_resource_path("signal_off.png")
            
            # Загружаем иконку дня
            day_image = Image.open(day_path)
            day_image = day_image.resize((40, 40), Image.Resampling.LANCZOS)
            self.day_icon = ImageTk.PhotoImage(day_image)
            
            # Загружаем иконку ночи
            night_image = Image.open(night_path)
            night_image = night_image.resize((40, 40), Image.Resampling.LANCZOS)
            self.night_icon = ImageTk.PhotoImage(night_image)
            
            # Загружаем иконку настроек (белую)
            settings_image = Image.open(settings_path)
            settings_image = settings_image.resize((20, 20), Image.Resampling.LANCZOS)
            self.settings_icon = ImageTk.PhotoImage(settings_image)
            
            # Загружаем иконку настроек (черную)
            setting_black_image = Image.open(setting_black_path)
            setting_black_image = setting_black_image.resize((20, 20), Image.Resampling.LANCZOS)
            self.setting_black_icon = ImageTk.PhotoImage(setting_black_image)
            
            # Загружаем иконки сигнала для будильников
            signal_on_image = Image.open(signal_on_path)
            signal_on_image = signal_on_image.resize((20, 20), Image.Resampling.LANCZOS)
            self.signal_on_icon = ImageTk.PhotoImage(signal_on_image)
            
            signal_off_image = Image.open(signal_off_path)
            signal_off_image = signal_off_image.resize((20, 20), Image.Resampling.LANCZOS)
            self.signal_off_icon = ImageTk.PhotoImage(signal_off_image)
            
        except Exception as e:
            print(f"Ошибка загрузки иконок: {e}")
            # Создаем заглушки если иконки не найдены
            self.create_fallback_icons()
    
    def create_fallback_icons(self):
        """Создает простые иконки если файлы не найдены"""
        # Создаем простую иконку дня (желтый круг)
        day_img = Image.new('RGBA', (40, 40), (255, 255, 0, 255))
        self.day_icon = ImageTk.PhotoImage(day_img)
        
        # Создаем простую иконку ночи (синий круг)
        night_img = Image.new('RGBA', (40, 40), (0, 0, 139, 255))
        self.night_icon = ImageTk.PhotoImage(night_img)
        
        # Создаем простую иконку настроек (серый шестеренка)
        settings_img = Image.new('RGBA', (20, 20), (128, 128, 128, 255))
        self.settings_icon = ImageTk.PhotoImage(settings_img)
        
        # Создаем простую иконку настроек черную (темно-серый шестеренка)
        setting_black_img = Image.new('RGBA', (20, 20), (64, 64, 64, 255))
        self.setting_black_icon = ImageTk.PhotoImage(setting_black_img)
        
        # Создаем простые иконки сигнала (красная и белая)
        signal_on_img = Image.new('RGBA', (20, 20), (255, 0, 0, 255))  # Красная
        self.signal_on_icon = ImageTk.PhotoImage(signal_on_img)
        
        signal_off_img = Image.new('RGBA', (20, 20), (255, 255, 255, 255))  # Белая
        self.signal_off_icon = ImageTk.PhotoImage(signal_off_img)
    
    def load_settings(self):
        """Загружает настройки будильника из файла"""
        try:
            settings_path = self.get_data_path("alarms.json")
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alarms = data.get('alarms', [])
                    
                    # Обновляем старые будильники, добавляя поле name
                    for alarm in self.alarms:
                        if 'name' not in alarm:
                            alarm['name'] = "Будильник"  # Добавляем поле по умолчанию
            else:
                # Если файла не существует, создаем пустой
                self.alarms = []
                self.save_settings()
                    
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
            self.alarms = []
            # Пытаемся создать файл с пустыми настройками
            try:
                self.save_settings()
            except:
                pass
    
    def save_settings(self):
        """Сохраняет настройки будильника в файл"""
        try:
            settings_path = self.get_data_path("alarms.json")
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump({'alarms': self.alarms}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def create_alarm_widgets(self):
        """Создает отдельные виджеты для активных будильников"""
        # Удаляем старые виджеты
        for widget in self.alarm_widgets:
            widget.destroy()
        self.alarm_widgets = []
        
        # Создаем виджеты только для активных будильников
        active_alarms = [alarm for alarm in self.alarms if alarm['enabled']]
        
        # Позиционируем виджеты внизу под основным окном с меньшим отступом
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_height = 100
        spacing = 5  # Уменьшенный отступ между виджетами
        
        for i, alarm in enumerate(active_alarms):
            widget = AlarmWidget(
                self.root,
                alarm,
                self.start_widget_drag,
                self.stop_widget_drag,
                self.do_widget_drag,
                lambda e, alarm=alarm: self.stop_alarm(alarm),
                self.signal_on_icon,
                self.signal_off_icon
            )
            
            # Позиционируем виджеты внизу под основным окном
            widget_x = main_x
            widget_y = main_y + main_height + spacing + (i * (40 + spacing))  # 40 - высота виджета
            
            widget.update_position(widget_x, widget_y)
            self.alarm_widgets.append(widget)
    
    def start_widget_drag(self, event):
        """Начало перемещения виджета"""
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        # Получаем Toplevel окно виджета
        widget = event.widget
        while not isinstance(widget, tk.Toplevel) and widget.master:
            widget = widget.master
        self.drag_data["widget"] = widget
    
    def stop_widget_drag(self, event):
        """Конец перемещения виджета"""
        self.drag_data["widget"] = None
    
    def do_widget_drag(self, event):
        """Перемещение виджета"""
        if self.drag_data["widget"]:
            deltax = event.x_root - self.drag_data["x"]
            deltay = event.y_root - self.drag_data["y"]
            
            # Получаем текущую позицию виджета
            widget_x = self.drag_data["widget"].winfo_x()
            widget_y = self.drag_data["widget"].winfo_y()
            
            # Обновляем позицию
            new_x = widget_x + deltax
            new_y = widget_y + deltay
            
            self.drag_data["widget"].geometry(f"+{new_x}+{new_y}")
            
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root
    
    def play_alarm_sound(self):
        """Проигрывает звук будильника"""
        try:
            sound_path = self.get_resource_path("signal.mp3")
            if os.path.exists(sound_path):
                pygame.mixer.music.load(sound_path)
                pygame.mixer.music.play(-1)  # -1 для повторения
                self.sound_playing = True
        except Exception as e:
            print(f"Ошибка воспроизведения звука: {e}")
    
    def stop_alarm_sound(self):
        """Останавливает звук будильника"""
        try:
            pygame.mixer.music.stop()
            self.sound_playing = False
            self.active_alarm = None
            
            # Сбрасываем подсветку всех виджетов
            for widget in self.alarm_widgets:
                widget.set_alarm_active(False)
                
        except Exception as e:
            print(f"Ошибка остановки звука: {e}")
    
    def stop_alarm(self, alarm):
        """Останавливает конкретный будильник"""
        if self.active_alarm and self.active_alarm['time'] == alarm['time'] and self.active_alarm['name'] == alarm['name']:
            self.stop_alarm_sound()
    
    def check_alarms(self, game_hour, game_minute):
        """Проверяет срабатывание будильников"""
        if self.active_alarm:
            return  # Уже есть активный будильник
            
        current_time_str = f"{game_hour:02d}:{game_minute:02d}"
        
        for alarm in self.alarms:
            if alarm['time'] == current_time_str and alarm['enabled']:
                if not self.sound_playing:
                    self.active_alarm = alarm
                    self.play_alarm_sound()
                    self.start_alarm_flash()
                return
    
    def start_alarm_flash(self):
        """Запускает мигание активного будильника через смену иконок"""
        if self.active_alarm and self.sound_playing:
            self.flash_state = not self.flash_state
            
            # Находим виджет активного будильника и мигаем им
            for widget in self.alarm_widgets:
                if (widget.alarm_data['time'] == self.active_alarm['time'] and 
                    widget.alarm_data['name'] == self.active_alarm['name']):
                    widget.set_alarm_active(self.flash_state)
            
            self.root.after(500, self.start_alarm_flash)
    
    def open_settings(self):
        """Открывает окно настроек будильника"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Настройки будильника")
        settings_window.geometry("350x450")
        settings_window.configure(bg='#2b2b2b')
        settings_window.attributes('-topmost', True)
        settings_window.resizable(False, False)
        
        # Устанавливаем иконку для окна настроек (черную версию)
        try:
            settings_window.iconphoto(False, self.setting_black_icon)
        except:
            pass
        
        # Центрируем окно
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Заголовок с иконкой
        title_frame = tk.Frame(settings_window, bg='#2b2b2b')
        title_frame.pack(pady=10, padx=20, fill='x')
        
        # Иконка в заголовке (черная версия)
        title_icon = tk.Label(
            title_frame,
            image=self.setting_black_icon,
            bg='#2b2b2b'
        )
        title_icon.pack(side='left', padx=(0, 10))
        
        # Текст заголовка
        title_label = tk.Label(
            title_frame,
            text="Настройки будильника",
            font=("Arial", 14, "bold"),
            fg='white',
            bg='#2b2b2b'
        )
        title_label.pack(side='left')
        
        # Фрейм для добавления нового будильника
        add_frame = tk.Frame(settings_window, bg='#2b2b2b')
        add_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(add_frame, text="Добавить будильник:", 
                font=("Arial", 10), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        # Поле для названия будильника
        name_frame = tk.Frame(add_frame, bg='#2b2b2b')
        name_frame.pack(fill='x', pady=5)
        
        tk.Label(name_frame, text="Название:", fg='white', bg='#2b2b2b').pack(side='left')
        name_var = tk.StringVar(value="Будильник")
        name_entry = tk.Entry(name_frame, textvariable=name_var, bg='#1a1a1a', fg='white', 
                             insertbackground='white', width=15)
        name_entry.pack(side='left', padx=5)
        
        time_frame = tk.Frame(add_frame, bg='#2b2b2b')
        time_frame.pack(fill='x', pady=5)
        
        # Поля для ввода времени
        tk.Label(time_frame, text="Время:", fg='white', bg='#2b2b2b').pack(side='left')
        hour_var = tk.StringVar(value="06")
        hour_spinbox = tk.Spinbox(time_frame, from_=0, to=23, width=3, 
                                 textvariable=hour_var, format="%02.0f",
                                 bg='#1a1a1a', fg='white', buttonbackground='#1a1a1a')
        hour_spinbox.pack(side='left', padx=5)
        
        tk.Label(time_frame, text=":", fg='white', bg='#2b2b2b').pack(side='left')
        minute_var = tk.StringVar(value="00")
        minute_spinbox = tk.Spinbox(time_frame, from_=0, to=59, width=3, 
                                   textvariable=minute_var, format="%02.0f",
                                   bg='#1a1a1a', fg='white', buttonbackground='#1a1a1a')
        minute_spinbox.pack(side='left', padx=5)
        
        def add_alarm():
            """Добавляет новый будильник"""
            try:
                hour = int(hour_var.get())
                minute = int(minute_var.get())
                name = name_var.get().strip()
                if not name:
                    name = "Будильник"
                    
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    time_str = f"{hour:02d}:{minute:02d}"
                    
                    # Проверяем, нет ли уже такого будильника
                    if not any(alarm['time'] == time_str and alarm['name'] == name for alarm in self.alarms):
                        self.alarms.append({
                            'time': time_str,
                            'name': name,
                            'enabled': True
                        })
                        self.save_settings()
                        update_alarms_list()
                        self.create_alarm_widgets()  # Пересоздаем виджеты
                    else:
                        messagebox.showwarning("Внимание", "Будильник с таким временем и названием уже существует!")
                else:
                    messagebox.showerror("Ошибка", "Некорректное время!")
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числа!")
        
        tk.Button(add_frame, text="Добавить будильник", command=add_alarm,
                 bg='#2196F3', fg='white', font=("Arial", 9)).pack(pady=10)
        
        # Список существующих будильников
        list_frame = tk.Frame(settings_window, bg='#2b2b2b')
        list_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(list_frame, text="Мои будильники:", 
                font=("Arial", 10), fg='white', bg='#2b2b2b').pack(anchor='w')
        
        # Создаем canvas и scrollbar для списка будильников
        canvas = tk.Canvas(list_frame, bg='#1a1a1a', height=150)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1a1a1a')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def update_alarms_list():
            """Обновляет список будильников в настройках"""
            # Очищаем фрейм
            for widget in scrollable_frame.winfo_children():
                widget.destroy()
            
            if not self.alarms:
                tk.Label(scrollable_frame, text="Нет будильников", 
                        fg='#888888', bg='#1a1a1a').pack(pady=10)
                return
            
            for i, alarm in enumerate(self.alarms):
                alarm_frame = tk.Frame(scrollable_frame, bg='#1a1a1a')
                alarm_frame.pack(fill='x', pady=2)
                
                status = "🔔" if alarm['enabled'] else "🔕"
                tk.Label(alarm_frame, text=f"{status} {alarm['time']} - {alarm['name']}", 
                        fg='white', bg='#1a1a1a', font=("Arial", 9)).pack(side='left')
                
                btn_frame = tk.Frame(alarm_frame, bg='#1a1a1a')
                btn_frame.pack(side='right')
                
                tk.Button(btn_frame, text="Вкл/Выкл", command=lambda idx=i: toggle_alarm(idx),
                         bg='#FF9800', fg='white', font=("Arial", 7)).pack(side='left', padx=2)
                
                tk.Button(btn_frame, text="Удалить", command=lambda idx=i: delete_alarm(idx),
                         bg='#f44336', fg='white', font=("Arial", 7)).pack(side='left', padx=2)
        
        def toggle_alarm(index):
            """Включает/выключает будильник"""
            self.alarms[index]['enabled'] = not self.alarms[index]['enabled']
            self.save_settings()
            update_alarms_list()
            self.create_alarm_widgets()  # Пересоздаем виджеты
        
        def delete_alarm(index):
            """Удаляет будильник"""
            self.alarms.pop(index)
            self.save_settings()
            update_alarms_list()
            self.create_alarm_widgets()  # Пересоздаем виджеты
        
        # Кнопка закрытия
        tk.Button(settings_window, text="Закрыть", command=settings_window.destroy,
                 bg='#757575', fg='white', width=15).pack(pady=10)
        
        update_alarms_list()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = tk.Frame(self.root, bg='#2b2b2b', padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        # Фрейм для времени и иконки
        time_frame = tk.Frame(main_frame, bg='#2b2b2b')
        time_frame.pack(expand=True)
        
        # Метка для иконки дня/ночи
        self.icon_label = tk.Label(time_frame, image=self.day_icon, bg='#2b2b2b')
        self.icon_label.pack(side='left', padx=(0, 10))
        
        # Метка для игрового времени
        self.game_time_label = tk.Label(
            time_frame, 
            text="00:00", 
            font=("Arial", 24, "bold"), 
            fg='#ffffff', 
            bg='#2b2b2b'
        )
        self.game_time_label.pack(side='left')
        
        # Кнопка настроек (маленькая иконка справа от времени)
        self.settings_btn = tk.Label(
            time_frame,
            image=self.settings_icon,
            bg='#2b2b2b',
            cursor="hand2"
        )
        self.settings_btn.pack(side='left', padx=(10, 0))
        self.settings_btn.bind("<Button-1>", lambda e: self.open_settings())
        
        # Изменяем курсор при наведении на кнопку настроек
        self.settings_btn.bind("<Enter>", lambda e: self.settings_btn.config(bg='#3b3b3b'))
        self.settings_btn.bind("<Leave>", lambda e: self.settings_btn.config(bg='#2b2b2b'))
        
        # Кнопка закрытия (в углу)
        close_btn = tk.Label(
            self.root, 
            text="×", 
            font=("Arial", 12, "bold"), 
            fg='#cccccc', 
            bg='#2b2b2b',
            cursor="hand2"
        )
        close_btn.place(x=180, y=0, width=20, height=20)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())
        
        # Изменяем цвет при наведении на кнопку закрытия
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg='#ffffff', bg='#ff4444'))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg='#cccccc', bg='#2b2b2b'))
    
    def bind_drag_events(self):
        """Добавляет возможность перемещения окна"""
        def start_move(event):
            self.x = event.x
            self.y = event.y
        
        def stop_move(event):
            self.x = None
            self.y = None
        
        def do_move(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")
            
            # Перемещаем все виджеты будильников вместе с основным окном
            self.update_alarm_widgets_position(x, y)
        
        # Привязываем события ко всему окну кроме кнопки закрытия
        self.root.bind("<ButtonPress-1>", start_move)
        self.root.bind("<ButtonRelease-1>", stop_move)
        self.root.bind("<B1-Motion>", do_move)
        
        # Игровое время тоже можно использовать для перемещения
        self.game_time_label.bind("<ButtonPress-1>", start_move)
        self.game_time_label.bind("<ButtonRelease-1>", stop_move)
        self.game_time_label.bind("<B1-Motion>", do_move)
        
        self.icon_label.bind("<ButtonPress-1>", start_move)
        self.icon_label.bind("<ButtonRelease-1>", stop_move)
        self.icon_label.bind("<B1-Motion>", do_move)
    
    def update_alarm_widgets_position(self, main_x, main_y):
        """Обновляет позиции всех виджетов будильников относительно главного окна"""
        main_height = 100
        spacing = 5  # Уменьшенный отступ
        
        for i, widget in enumerate(self.alarm_widgets):
            widget_x = main_x
            widget_y = main_y + main_height + spacing + (i * (40 + spacing))  # 40 - высота виджета
            widget.update_position(widget_x, widget_y)
    
    def real_time_to_game_time(self, real_time):
        """Конвертирует реальное время в игровое с синхронизацией"""
        # Вычисляем разницу от базового времени синхронизации
        time_diff = real_time - self.sync_base
        total_seconds = time_diff.total_seconds()
        
        # Конвертируем секунды в игровое время
        # 2.5 реальных минуты = 150 секунд = 1 игровой час
        game_hours_passed = (total_seconds / 150) % 24
        game_hour = int(game_hours_passed)
        game_minute = int((game_hours_passed - game_hour) * 60)
        
        return game_hour, game_minute
    
    def update_time(self):
        """Обновляет время на экране"""
        current_time = datetime.now()
        
        # Конвертируем в игровое время
        game_hour, game_minute = self.real_time_to_game_time(current_time)
        
        # Обновляем игровое время
        game_time_str = f"{game_hour:02d}:{game_minute:02d}"
        self.game_time_label.config(text=game_time_str)
        
        # Обновляем иконку (ночь с 00:00 до 06:00, день с 06:00 до 00:00)
        if 0 <= game_hour < 6:
            self.icon_label.config(image=self.night_icon)
        else:
            self.icon_label.config(image=self.day_icon)
        
        # Проверяем будильники
        self.check_alarms(game_hour, game_minute)
        
        # Проверяем, не нужно ли обновить базу синхронизации (на случай смены часа)
        if current_time.minute == 0 and current_time.second == 0:
            self.sync_base = current_time.replace(second=0, microsecond=0)
        
        # Обновляем каждые 100 мс для плавности
        self.root.after(100, self.update_time)

def main():
    root = tk.Tk()
    
    # Устанавливаем прозрачность
    root.attributes('-alpha', 0.95)
    
    # Всегда поверх всех окон
    root.attributes('-topmost', True)
    
    app = GameClock(root)
    root.mainloop()

if __name__ == "__main__":
    main()