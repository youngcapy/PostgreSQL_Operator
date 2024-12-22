import tkinter as tk
from tkinter import Entry, END


class PG_Table:
    def __init__(self, parent, values):
        self.values = values
        self.total_rows = len(values)
        self.total_columns = len(values[0]) if values else 0

        # Создаём Frame для таблицы
        self.table_frame = tk.Frame(parent)
        self.table_frame.grid(row=0, column=0, sticky="nsew")

        # Настраиваем сетку в родительском окне
        parent.grid_rowconfigure(0, weight=2)  # Верхняя часть для таблицы
        parent.grid_rowconfigure(1, weight=1)  # Нижняя часть для кнопок
        parent.grid_columnconfigure(0, weight=1)

        # Создаём Canvas и Scrollbars
        self.canvas = tk.Canvas(self.table_frame, bg="lightgrey")
        self.v_scrollbar = tk.Scrollbar(self.table_frame, orient="vertical", command=self.canvas.yview)
        self.h_scrollbar = tk.Scrollbar(self.table_frame, orient="horizontal", command=self.canvas.xview)

        # Привязываем Scrollbars к Canvas
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Размещение Canvas и Scrollbars
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        # Настраиваем сетку для таблицы
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Создаём Frame внутри Canvas для таблицы
        self.inner_table_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_table_frame, anchor="nw")

        # Добавляем ячейки таблицы
        for i in range(self.total_rows):
            for j in range(self.total_columns):
                if(i == 0):
                    self.e = Entry(self.inner_table_frame, width=20, fg='black', font=('Times New Roman', 12, 'bold'))
                else:
                    self.e = Entry(self.inner_table_frame, width=20, fg='black', font=('Times New Roman', 12))
                self.e.grid(row=i, column=j, padx=5, pady=5)
                self.e.insert(END, self.values[i][j])

        # Обновляем область прокрутки
        self.inner_table_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        # Привязываем событие для обновления Canvas при изменении размеров окна
        parent.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        # Обновляем размеры Canvas при изменении размеров окна
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

