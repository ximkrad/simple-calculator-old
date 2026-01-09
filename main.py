from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from datetime import datetime
import calendar
import json
import os
from kivy.utils import get_color_from_hex
from kivy.config import Config
from kivy.metrics import dp

if os.environ.get('KIVY_BUILD', '') == 'android':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '700')
    Config.set('graphics', 'resizable', '0')
    Config.set('kivy', 'exit_on_escape', '0')

class DayButton(Button):
    """Кнопка дня"""
    def __init__(self, date_str, day_num, is_current_month=True, **kwargs):
        super().__init__(**kwargs)
        self.date_str = date_str
        self.day_num = day_num
        self.is_current_month = is_current_month
        self.background_normal = ''
        self.font_size = dp(18)  # Используем dp для масштабирования
        self.size_hint_y = None
        self.height = dp(60)  # Используем dp вместо фиксированных пикселей
        self.halign = 'center'
        self.valign = 'middle'
        
        # Настройка внешнего вида
        if not self.is_current_month:
            self.color = (0.6, 0.6, 0.6, 1)
            self.background_color = (0.95, 0.95, 0.95, 1)
        else:
            self.color = (0, 0, 0, 1)
            self.background_color = (1, 1, 1, 1)

class CalendarApp(App):
    def build(self):
        # Создаем TabbedPanel для вкладок
        self.tabs = TabbedPanel(
            do_default_tab=False,
            tab_width=dp(200)  # Используем dp
        )
        
        # Вкладка 1: Календарь
        self.calendar_tab = TabbedPanelItem(text='📅 Календарь')
        self.create_calendar_tab()
        self.tabs.add_widget(self.calendar_tab)
        
        # Вкладка 2: Все заметки
        self.notes_tab = TabbedPanelItem(text='📝 Все заметки')
        self.create_notes_tab()
        self.tabs.add_widget(self.notes_tab)
        
        # Загрузка данных
        self.load_data()
        
        # Обновление календаря
        self.update_calendar()
        
        return self.tabs
    
    def create_calendar_tab(self):
        """Создает вкладку календаря"""
        # Основной layout
        calendar_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Панель управления
        control_panel = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        
        self.current_date = datetime.now()
        self.month_label = Label(
            text=self.get_month_text(),
            font_size=dp(22),
            bold=True,
            size_hint_x=0.6
        )
        
        prev_btn = Button(text="<", size_hint_x=0.2, font_size=dp(20))
        prev_btn.bind(on_press=self.prev_month)
        
        next_btn = Button(text=">", size_hint_x=0.2, font_size=dp(20))
        next_btn.bind(on_press=self.next_month)
        
        control_panel.add_widget(prev_btn)
        control_panel.add_widget(self.month_label)
        control_panel.add_widget(next_btn)
        
        calendar_layout.add_widget(control_panel)
        
        # Дни недели
        days_layout = GridLayout(cols=7, size_hint_y=0.08, spacing=dp(2))
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for day in days:
            lbl = Label(text=day, bold=True, font_size=dp(16))
            days_layout.add_widget(lbl)
        
        calendar_layout.add_widget(days_layout)
        
        # Календарь
        self.calendar_grid = GridLayout(
            cols=7, 
            spacing=dp(2), 
            size_hint_y=None,
            row_default_height=dp(70)  # Фиксированная высота строки
        )
        self.calendar_grid.bind(minimum_height=self.calendar_grid.setter('height'))
        
        scroll = ScrollView(size_hint_y=0.75)
        scroll.add_widget(self.calendar_grid)
        calendar_layout.add_widget(scroll)
        
        # Статус
        self.status_label = Label(
            text='Выберите день для редактирования',
            size_hint_y=0.06,
            font_size=dp(14)
        )
        calendar_layout.add_widget(self.status_label)
        
        # Кнопка сегодня
        today_btn = Button(
            text='Сегодня', 
            size_hint_y=0.08,
            font_size=dp(16)
        )
        today_btn.bind(on_press=self.go_to_today)
        calendar_layout.add_widget(today_btn)
        
        self.calendar_tab.content = calendar_layout
    
    def create_notes_tab(self):
        """Создает вкладку со всеми заметками"""
        # Основной layout
        notes_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        # Заголовок
        self.notes_title = Label(
            text='Все заметки',
            font_size=dp(22),
            bold=True,
            size_hint_y=0.1
        )
        notes_layout.add_widget(self.notes_title)
        
        # Кнопки управления заметками
        notes_control = BoxLayout(size_hint_y=0.08, spacing=dp(10))
        
        refresh_btn = Button(text='Обновить', font_size=dp(16))
        refresh_btn.bind(on_press=self.refresh_notes)
        
        clear_all_btn = Button(
            text='Очистить все', 
            background_color=(0.9, 0.3, 0.3, 1),
            font_size=dp(16)
        )
        clear_all_btn.bind(on_press=self.clear_all_notes)
        
        notes_control.add_widget(refresh_btn)
        notes_control.add_widget(clear_all_btn)
        
        notes_layout.add_widget(notes_control)
        
        # Список заметок
        self.notes_scroll = ScrollView(size_hint_y=0.8)
        self.notes_container = BoxLayout(
            orientation='vertical',
            spacing=dp(5),
            size_hint_y=None,
            padding=[dp(5), dp(5), dp(5), dp(5)]
        )
        self.notes_container.bind(minimum_height=self.notes_container.setter('height'))
        
        self.notes_scroll.add_widget(self.notes_container)
        notes_layout.add_widget(self.notes_scroll)
        
        # Статус заметок
        self.notes_status = Label(
            text='Загрузка заметок...',
            size_hint_y=0.05,
            font_size=dp(14)
        )
        notes_layout.add_widget(self.notes_status)
        
        self.notes_tab.content = notes_layout
    
    def load_data(self):
        """Загружает сохраненные данные"""
        self.saved_data = {}
        try:
            if os.path.exists('calendar_data.json'):
                with open('calendar_data.json', 'r', encoding='utf-8') as f:
                    self.saved_data = json.load(f)
        except:
            self.saved_data = {}
    
    def save_data(self):
        """Сохраняет данные"""
        try:
            with open('calendar_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.saved_data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_month_text(self):
        """Возвращает название месяца"""
        months = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        return f"{months[self.current_date.month-1]} {self.current_date.year}"
    
    def update_calendar(self):
        """Обновляет отображение календаря"""
        self.calendar_grid.clear_widgets()
        
        year = self.current_date.year
        month = self.current_date.month
        
        cal = calendar.monthcalendar(year, month)
        
        for week in cal:
            for day in week:
                if day == 0:
                    # Пустая ячейка
                    self.calendar_grid.add_widget(Label(text='', size_hint_y=None, height=dp(70)))
                else:
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    
                    # Создаем кнопку
                    btn = DayButton(
                        date_str=date_str,
                        day_num=day,
                        is_current_month=True,
                        text=str(day),
                        size_hint_y=None,
                        height=dp(70)  # Фиксированная высота
                    )
                    
                    # Проверяем есть ли заметка для этого дня
                    has_note = False
                    if date_str in self.saved_data:
                        day_data = self.saved_data[date_str]
                        
                        # Устанавливаем цвет
                        if 'color' in day_data:
                            color = day_data['color']
                            if isinstance(color, str) and color.startswith('#'):
                                btn.background_color = get_color_from_hex(color)
                            elif isinstance(color, list):
                                btn.background_color = color
                        
                        # Проверяем есть ли заметка
                        if 'note' in day_data and day_data['note'].strip():
                            has_note = True
                            btn.text = f"{day} 📝"
                    
                    # Подсветка сегодняшнего дня
                    today = datetime.now()
                    if year == today.year and month == today.month and day == today.day:
                        # Если день не имеет цвета, подсвечиваем его
                        if date_str not in self.saved_data or 'color' not in self.saved_data[date_str]:
                            btn.background_color = (0.8, 0.9, 1, 1)
                        btn.bold = True
                        btn.color = (0, 0.3, 0.8, 1)
                    
                    # Для темных цветов делаем текст белым
                    if isinstance(btn.background_color, (list, tuple)) and len(btn.background_color) >= 3:
                        r, g, b = btn.background_color[0], btn.background_color[1], btn.background_color[2]
                        brightness = 0.299 * r + 0.587 * g + 0.114 * b
                        if brightness < 0.5:
                            btn.color = (1, 1, 1, 1)
                    
                    btn.bind(on_press=self.on_day_click)
                    self.calendar_grid.add_widget(btn)
    
    def on_day_click(self, instance):
        """Обработка клика по дню"""
        if not instance.is_current_month:
            return
        
        self.selected_day = instance.date_str
        self.show_day_editor()
    
    def show_day_editor(self):
        """Показывает редактор дня"""
        # Получаем данные дня
        day_data = self.saved_data.get(self.selected_day, {})
        current_color = day_data.get('color', [1, 1, 1, 1])
        current_note = day_data.get('note', '')
        
        # Конвертируем цвет в HEX
        hex_color = self.color_to_hex(current_color)
        
        # Создаем контент попапа
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # Заголовок
        day_str = f"{self.selected_day[8:10]}.{self.selected_day[5:7]}.{self.selected_day[:4]}"
        title = Label(text=f"День: {day_str}", font_size=dp(20), bold=True)
        content.add_widget(title)
        
        # Цвета
        color_label = Label(text="Выберите цвет:", font_size=dp(16))
        content.add_widget(color_label)
        
        # Сетка цветов
        colors_grid = GridLayout(cols=5, spacing=dp(5), size_hint_y=None, height=dp(180))
        
        colors = [
            ('#FF6B6B', 'Красный'),
            ('#FFD166', 'Желтый'),
            ('#06D6A0', 'Зеленый'),
            ('#118AB2', 'Синий'),
            ('#9B59B6', 'Фиолетовый'),
            ('#FF9A76', 'Оранжевый'),
            ('#A7E9AF', 'Салатовый'),
            ('#78C1D5', 'Голубой'),
            ('#D4A5A5', 'Бежевый'),
            ('#FFFFFF', 'Белый'),
            ('#E74C3C', 'Темно-красный'),
            ('#2ECC71', 'Ярко-зеленый'),
            ('#3498DB', 'Небесно-синий'),
            ('#F1C40F', 'Золотой'),
            ('#1ABC9C', 'Бирюзовый'),
            ('#34495E', 'Темно-серый'),
            ('#ECF0F1', 'Светло-серый'),
            ('#BDC3C7', 'Серый'),
            ('#7F8C8D', 'Стальной'),
            ('#2C3E50', 'Чернильный')
        ]
        
        self.selected_color_btn = None
        
        for hex_color_value, color_name in colors:
            color_btn = Button(
                background_normal='',
                background_color=get_color_from_hex(hex_color_value),
                size_hint_y=None,
                height=dp(40)
            )
            color_btn.hex_color = hex_color_value
            color_btn.color_name = color_name
            
            # Выделяем текущий цвет
            if hex_color_value == hex_color:
                self.selected_color_btn = color_btn
                color_btn.border = (dp(2), dp(2), dp(2), dp(2))
            
            color_btn.bind(on_press=self.on_color_select)
            colors_grid.add_widget(color_btn)
        
        content.add_widget(colors_grid)
        
        # Заметка
        note_label = Label(text="Заметка:", font_size=dp(16))
        content.add_widget(note_label)
        
        self.note_input = TextInput(
            text=current_note,
            multiline=True,
            size_hint_y=None,
            height=dp(120),
            hint_text='Введите заметку...',
            font_size=dp(16)
        )
        content.add_widget(self.note_input)
        
        # Кнопки
        buttons_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        save_btn = Button(
            text='Сохранить', 
            background_color=(0.2, 0.7, 0.3, 1),
            font_size=dp(16)
        )
        save_btn.bind(on_press=self.save_day_data)
        
        cancel_btn = Button(text='Отмена', font_size=dp(16))
        cancel_btn.bind(on_press=lambda x: self.day_editor_popup.dismiss())
        
        delete_btn = Button(
            text='Удалить', 
            background_color=(0.8, 0.2, 0.2, 1),
            font_size=dp(16)
        )
        delete_btn.bind(on_press=self.delete_day_data)
        
        buttons_layout.add_widget(save_btn)
        buttons_layout.add_widget(cancel_btn)
        buttons_layout.add_widget(delete_btn)
        
        content.add_widget(buttons_layout)
        
        # Создаем попап
        self.day_editor_popup = Popup(
            title='Редактирование дня',
            content=content,
            size_hint=(0.9, 0.85),
            auto_dismiss=False
        )
        
        # Сохраняем выбранный цвет
        self.selected_color = hex_color
        
        self.day_editor_popup.open()
    
    def on_color_select(self, instance):
        """Обработка выбора цвета"""
        if hasattr(self, 'selected_color_btn') and self.selected_color_btn:
            self.selected_color_btn.border = (0, 0, 0, 0)
        
        instance.border = (dp(2), dp(2), dp(2), dp(2))
        self.selected_color_btn = instance
        self.selected_color = instance.hex_color
    
    def save_day_data(self, instance):
        """Сохраняет данные дня"""
        # Получаем цвет
        color = get_color_from_hex(self.selected_color)
        
        # Получаем заметку
        note = self.note_input.text.strip()
        
        # Сохраняем данные
        self.saved_data[self.selected_day] = {
            'color': self.color_to_hex(color),
            'note': note,
            'last_modified': datetime.now().isoformat()
        }
        
        # Сохраняем в файл
        self.save_data()
        
        # Обновляем календарь
        self.update_calendar()
        
        # Обновляем список заметок
        self.update_notes_list()
        
        # Закрываем попап
        self.day_editor_popup.dismiss()
        
        # Показываем статус
        day_str = f"{self.selected_day[8:10]}.{self.selected_day[5:7]}.{self.selected_day[:4]}"
        if note:
            self.status_label.text = f"День {day_str} сохранен с заметкой"
        else:
            self.status_label.text = f"День {day_str} сохранен"
    
    def delete_day_data(self, instance):
        """Удаляет данные дня"""
        if self.selected_day in self.saved_data:
            del self.saved_data[self.selected_day]
            self.save_data()
            self.update_calendar()
            self.update_notes_list()
        
        self.day_editor_popup.dismiss()
        
        day_str = f"{self.selected_day[8:10]}.{self.selected_day[5:7]}.{self.selected_day[:4]}"
        self.status_label.text = f"Данные дня {day_str} удалены"
    
    def color_to_hex(self, color):
        """Конвертирует цвет в HEX"""
        if isinstance(color, str) and color.startswith('#'):
            return color
        elif isinstance(color, (list, tuple)) and len(color) >= 3:
            r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            return f'#{r:02x}{g:02x}{b:02x}'
        return '#FFFFFF'
    
    def prev_month(self, instance):
        """Предыдущий месяц"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        
        self.month_label.text = self.get_month_text()
        self.update_calendar()
    
    def next_month(self, instance):
        """Следующий месяц"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        
        self.month_label.text = self.get_month_text()
        self.update_calendar()
    
    def go_to_today(self, instance):
        """Переход к сегодня"""
        self.current_date = datetime.now()
        self.month_label.text = self.get_month_text()
        self.update_calendar()
        self.status_label.text = "Текущий месяц"
    
    def refresh_notes(self, instance):
        """Обновляет список заметок"""
        self.update_notes_list()
        self.notes_status.text = "Список заметок обновлен"
    
    def clear_all_notes(self, instance):
        """Очищает все заметки (только текст заметок, цвета остаются)"""
        confirm_popup = Popup(
            title='Подтверждение',
            size_hint=(0.7, 0.4)
        )
        
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        msg = Label(
            text="Удалить текст всех заметок?\nЦвета дней останутся.",
            font_size=dp(16)
        )
        content.add_widget(msg)
        
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        
        yes_btn = Button(
            text='Да', 
            background_color=(0.9, 0.3, 0.3, 1),
            font_size=dp(16)
        )
        no_btn = Button(text='Нет', font_size=dp(16))
        
        def clear_notes(btn):
            for date_str in self.saved_data:
                if 'note' in self.saved_data[date_str]:
                    self.saved_data[date_str]['note'] = ''
            self.save_data()
            self.update_calendar()
            self.update_notes_list()
            confirm_popup.dismiss()
            self.notes_status.text = "Все заметки очищены"
        
        yes_btn.bind(on_press=clear_notes)
        no_btn.bind(on_press=confirm_popup.dismiss)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        confirm_popup.content = content
        confirm_popup.open()
    
    def update_notes_list(self):
        """Обновляет список всех заметок во вкладке"""
        # Очищаем контейнер
        self.notes_container.clear_widgets()
        
        # Собираем заметки
        notes_with_dates = []
        for date_str, day_data in self.saved_data.items():
            if 'note' in day_data and day_data['note'].strip():
                note_text = day_data['note'].strip()
                day_formatted = f"{date_str[8:10]}.{date_str[5:7]}.{date_str[:4]}"
                
                # Получаем цвет дня
                color_hex = day_data.get('color', '#FFFFFF')
                notes_with_dates.append((day_formatted, note_text, color_hex))
        
        # Сортируем по дате
        notes_with_dates.sort(key=lambda x: x[0], reverse=True)
        
        if not notes_with_dates:
            # Нет заметок
            no_notes_label = Label(
                text="Нет сохраненных заметок\n\nСоздайте заметки во вкладке 'Календарь'",
                font_size=dp(18),
                halign='center',
                valign='middle',
                size_hint_y=None,
                height=dp(200)
            )
            no_notes_label.bind(size=no_notes_label.setter('text_size'))
            self.notes_container.add_widget(no_notes_label)
        else:
            # Добавляем заметки
            for day_formatted, note_text, color_hex in notes_with_dates:
                # Создаем карточку заметки
                note_card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=dp(120),
                    padding=[dp(10), dp(5), dp(10), dp(5)],
                    spacing=dp(5)
                )
                
                # Верхняя часть с датой и цветом
                top_part = BoxLayout(size_hint_y=0.4)
                
                date_btn = Button(
                    text=day_formatted,
                    background_normal='',
                    background_color=get_color_from_hex(color_hex),
                    size_hint_x=0.3,
                    font_size=dp(16),
                    bold=True
                )
                
                # Кнопка перехода к дню
                date_btn.date_str = f"{day_formatted[6:]}-{day_formatted[3:5]}-{day_formatted[:2]}"
                date_btn.bind(on_press=self.go_to_date)
                
                note_preview = Label(
                    text=note_text[:50] + ("..." if len(note_text) > 50 else ""),
                    size_hint_x=0.7,
                    halign='left',
                    font_size=dp(16)
                )
                note_preview.bind(size=note_preview.setter('text_size'))
                
                top_part.add_widget(date_btn)
                top_part.add_widget(note_preview)
                
                # Нижняя часть с полным текстом
                bottom_part = BoxLayout(size_hint_y=0.6)
                
                full_note = Label(
                    text=note_text,
                    halign='left',
                    valign='top',
                    font_size=dp(14)
                )
                full_note.bind(size=full_note.setter('text_size'))
                
                # Кнопка редактирования
                edit_btn = Button(
                    text='✎',
                    size_hint_x=0.1,
                    font_size=dp(18)
                )
                edit_btn.date_str = f"{day_formatted[6:]}-{day_formatted[3:5]}-{day_formatted[:2]}"
                edit_btn.note_text = note_text
                edit_btn.bind(on_press=self.edit_note_from_list)
                
                bottom_part.add_widget(full_note)
                bottom_part.add_widget(edit_btn)
                
                note_card.add_widget(top_part)
                note_card.add_widget(bottom_part)
                
                # Разделитель
                separator = BoxLayout(size_hint_y=None, height=dp(1))
                separator.canvas.before.clear()
                with separator.canvas.before:
                    from kivy.graphics import Color, Rectangle
                    Color(0.9, 0.9, 0.9, 1)
                    Rectangle(pos=separator.pos, size=separator.size)
                
                self.notes_container.add_widget(note_card)
                self.notes_container.add_widget(separator)
        
        # Обновляем заголовок
        self.notes_title.text = f'Все заметки ({len(notes_with_dates)})'
        self.notes_status.text = f"Найдено {len(notes_with_dates)} заметок"
    
    def go_to_date(self, instance):
        """Переходит к указанной дате в календаре"""
        try:
            # Преобразуем дату
            date_str = instance.date_str  # Формат: "YYYY-MM-DD"
            year, month, day = map(int, date_str.split('-'))
            
            # Устанавливаем дату
            self.current_date = datetime(year, month, day)
            self.month_label.text = self.get_month_text()
            self.update_calendar()
            
            # Переключаемся на вкладку календаря
            self.tabs.switch_to(self.calendar_tab)
            
            self.status_label.text = f"Перешли к {day:02d}.{month:02d}.{year}"
        except:
            self.status_label.text = "Ошибка перехода к дате"
    
    def edit_note_from_list(self, instance):
        """Редактирует заметку из списка"""
        self.selected_day = instance.date_str
        self.show_day_editor()
        
        # Переключаемся на вкладку календаря
        self.tabs.switch_to(self.calendar_tab)

if __name__ == '__main__':
    # Создаем файл данных если его нет
    if not os.path.exists('calendar_data.json'):
        with open('calendar_data.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)
    
    CalendarApp().run()
