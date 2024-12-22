from tkinter import *
from tkinter import ttk
import psycopg
from pg_back import PG_Back
import pg_table
from pg_table import PG_Table


class PG_Gui:
    def __init__(self, back_link):
        self.back_ops = back_link
        self.pg_tables = []
        self.get_table_names()
        self.root = None
        self.table = None
        self.clicked = None  # Инициализация после создания root
        self.sort_order = None  # Для хранения выбранного порядка сортировки
        self.sort_column = None  # Для хранения выбранного столбца сортировки
        self.column_menu = None  # Ссылка на меню столбцов
        self.form_builder()
        self.gui_cascades()
        self.gui_start()

    def form_builder(self):
        self.root = Tk()  # Создаем корневое окно
        self.root.title('Оператор PostgreSQL')
        self.root.geometry('500x500')

        self.clicked = StringVar()
        self.sort_order = StringVar()
        self.sort_column = StringVar()

        self.get_table(self.pg_tables[0])

        # Frame для вывода таблицы
        table_frame = Frame(self.root)
        table_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Надпись "Таблица"
        table_label = Label(self.root, text="Таблица")
        table_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Dropdown для выбора таблицы
        self.clicked.set(self.pg_tables[0] if self.pg_tables else "No tables available")
        drop = OptionMenu(self.root, self.clicked, *self.pg_tables)
        drop.grid(row=2, column=0, padx=10, pady=10, sticky="w")  # Размещение под таблицей

        # Привязываем функцию к изменению значения в clicked
        self.clicked.trace("w", self.on_table_selected)

        # Надпись "Отсортировать"
        #sort_label = Label(self.root, text="Отсортировать")
        #sort_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        # Dropdown для выбора порядка сортировки
        self.sort_order.set("По возрастанию")  # Значение по умолчанию
        sort_menu = OptionMenu(self.root, self.sort_order, "По возрастанию", "По убыванию",
                               command=self.on_sort_order_selected)
        #sort_menu.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        # Надпись "Относительно"
        #relative_label = Label(self.root, text="Относительно")
        #relative_label.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Dropdown для выбора столбца сортировки
        self.sort_column.set("Выберите столбец")  # Значение по умолчанию
        self.column_menu = OptionMenu(self.root, self.sort_column, "Выберите столбец")
        #self.column_menu.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    def get_table_names(self):
        self.pg_tables = self.back_ops.get_tables_names()

    def get_column_names(self, table_name):
        if table_name:
            return self.back_ops.get_column_names()
        return []

    def sort_menu(self):
        self.open_sort_window()

    def delete_menu(self):
        self.open_delete_window()

    def add_menu(self):
        self.open_add_window()

    def redact_menu(self):
        self.open_redact_window()

    def search_menu(self):
        self.open_search_window()

    def open_add_window(self):
        modal_window = Toplevel(self.root)
        modal_window.title("Добавление")
        modal_window.geometry("400x400")
        modal_window.grab_set()

        columns = self.get_column_names(self.clicked.get())

        entry_widgets = []
        for idx, column in enumerate(columns):
            label = Label(modal_window, text=column)
            label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")
            entry = Entry(modal_window)
            entry.grid(row=idx, column=1, padx=10, pady=5)
            entry_widgets.append(entry)

        def on_add():
            values = [entry.get() for entry in entry_widgets]
            print("Добавляемые данные:", values)  # Вывод данных в консоль
            self.back_ops.on_add_row(values)
            self.get_table(self.back_ops.current_table)
            modal_window.destroy()

        add_button = Button(modal_window, text="Добавить", command=on_add)
        add_button.grid(row=len(columns), column=0, columnspan=2, pady=10)

    def open_delete_window(self):
        modal_window = Toplevel(self.root)
        modal_window.title("Удаление")
        modal_window.geometry("300x200")
        modal_window.grab_set()

        label = Label(modal_window, text="Идентификатор строки")
        label.pack(padx=10, pady=5)

        id_entry = Entry(modal_window)
        id_entry.pack(padx=10, pady=5)

        def on_delete():
            row_id = id_entry.get()
            print("Удаляемая строка:", row_id)  # Вывод данных в консоль
            self.back_ops.on_delete_row(int(row_id))
            self.get_table(self.back_ops.current_table)
            modal_window.destroy()

        delete_button = Button(modal_window, text="Удалить", command=on_delete)
        delete_button.pack(pady=10)

    def open_redact_window(self):
        modal_window = Toplevel(self.root)
        modal_window.title("Редактирование")
        modal_window.geometry("400x400")
        modal_window.grab_set()

        # Добавляем текстбокс для ID
        label_id = Label(modal_window, text="ID")
        label_id.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        id_entry = Entry(modal_window)
        id_entry.grid(row=0, column=1, padx=10, pady=5)

        # Получаем названия столбцов
        columns = self.get_column_names(self.clicked.get())

        # Создаем текстбоксы для каждого столбца
        entry_widgets = {}
        for idx, column in enumerate(columns):
            label = Label(modal_window, text=column)
            label.grid(row=idx + 1, column=0, padx=10, pady=5, sticky="w")
            entry = Entry(modal_window)
            entry.grid(row=idx + 1, column=1, padx=10, pady=5)
            entry_widgets[column] = entry

        def on_redact():
            row_id = id_entry.get()  # Получаем ID
            values = [row_id] + [entry.get() for column, entry in entry_widgets.items()]  # Массив с ID и значениями
            print("Редактируемая строка ID:", row_id)
            print("Новые значения:", values)
            self.back_ops.on_edit_row(values)
            self.get_table(self.back_ops.current_table)
            modal_window.destroy()

        # Кнопка для подтверждения изменений
        redact_button = Button(modal_window, text="Изменить", command=on_redact)
        redact_button.grid(row=len(columns) + 1, column=0, columnspan=2, pady=10)


    def open_sort_window(self):
        modal_window = Toplevel(self.root)
        modal_window.title("Сортировка")
        modal_window.geometry("300x200")
        modal_window.grab_set()

        sort_column_menu = OptionMenu(modal_window, self.sort_column, *self.get_column_names(self.clicked.get()))
        sort_column_menu.pack(padx=10, pady=10)

        sort_order_menu = OptionMenu(modal_window, self.sort_order, "По возрастанию", "По убыванию")
        sort_order_menu.pack(padx=10, pady=10)

        def on_sort():
            selected_column = self.sort_column.get()
            selected_order = self.sort_order.get()
            self.on_sort_order_selected(selected_order)

        sort_button = Button(modal_window, text="Сортировать", command=on_sort)
        sort_button.pack(pady=10)

    def open_search_window(self):
        modal_window = Toplevel(self.root)
        modal_window.title("Поиск")
        modal_window.geometry("300x200")
        modal_window.grab_set()

        # Получаем имена столбцов текущей таблицы
        columns = self.get_column_names(self.clicked.get())

        # Метка для выпадающего списка
        label_field = Label(modal_window, text="Поле")
        label_field.pack(padx=10, pady=5)

        # Переменная для хранения выбранного столбца
        selected_column = StringVar(modal_window)
        selected_column.set(columns[0])  # Устанавливаем первый столбец как значение по умолчанию

        # Выпадающий список для выбора столбца
        field_dropdown = OptionMenu(modal_window, selected_column, *columns)
        field_dropdown.pack(padx=10, pady=5)

        # Метка и текстовое поле для значения
        label_value = Label(modal_window, text="Значение")
        label_value.pack(padx=10, pady=5)

        value_entry = Entry(modal_window)
        value_entry.pack(padx=10, pady=5)

        def on_search():
            field = selected_column.get()  # Получаем выбранное поле
            value = value_entry.get()  # Получаем введенное значение
            values = [field, value]
            print("Поиск по:", values)  # Вывод данных в консоль
            self.table = PG_Table(self.root, self.back_ops.on_search_row(values))
            modal_window.destroy()

        # Кнопка для выполнения поиска
        search_button = Button(modal_window, text="Искать", command=on_search)
        search_button.pack(pady=10)

    def gui_cascades(self):
        menu_bar = Menu(self.root)
        # Добавление элементов в меню
        menu_bar.add_cascade(label="Добавление", command=self.add_menu)
        menu_bar.add_cascade(label="Удаление", command=self.delete_menu)
        menu_bar.add_cascade(label="Редактирование", command=self.redact_menu)
        menu_bar.add_cascade(label="Сортировка", command=self.sort_menu)
        menu_bar.add_cascade(label="Поиск", command=self.search_menu)

        # Конфигурируем меню
        self.root.config(menu=menu_bar)

    def gui_start(self):
        self.root.mainloop()

    def get_table(self, table_name):
        table = self.back_ops.get_table(table_name)
        self.table = PG_Table(self.root, table)

    def on_table_selected(self, *args):
        selected_table = self.clicked.get()
        print(f"Selected table: {selected_table}")
        self.get_table(selected_table)
        self.update_column_menu(selected_table)

    def update_column_menu(self, table_name):
        # Получаем список столбцов для выбранной таблицы
        columns = self.get_column_names(table_name)

        # Очистка текущего меню
        self.column_menu['menu'].delete(0, 'end')

        # Добавление новых столбцов в меню
        for column in columns:
            self.column_menu['menu'].add_command(label=column, command=lambda value=column: self.sort_column.set(value))

        # Сброс значения по умолчанию
        self.sort_column.set("Выберите столбец")

    def on_sort_order_selected(self, order):
        print(f"Selected sort order: {order}")
        selected_table = self.clicked.get()
        selected_column = self.sort_column.get()
        if selected_table and selected_column and selected_column != "Выберите столбец":
            self.get_sorted_table(selected_table, selected_column, order)

    def get_sorted_table(self, table_name, column, order):
        # Преобразуем порядок сортировки в SQL-совместимый вид
        sql_order = "ASC" if order == "По возрастанию" else "DESC"
        table = self.back_ops.table_sort_by(column, sql_order)
        self.table = PG_Table(self.root, table)  # Обновляем таблицу в интерфейсе
