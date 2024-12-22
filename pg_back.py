from posixpath import curdir

import psycopg
from psycopg import sql

class PG_Back:
    conn = "connection"
    cursor = "cursor"
    current_table = "current_table"
    table_contents = []

    def __init__(self, dbname, username, password, host):
        self.conn = psycopg.connect(dbname = dbname, user = username, password = password, host = host)
        self.cursor = self.conn.cursor()

    def add_header(self, table):
        col_names = [desc[0] for desc in self.cursor.description]
        table.insert(0, col_names)

    def add_ids(self, table):
        if not table:
            return []

        # Преобразуем заголовки в список и добавляем "id"
        headers = list(table[0])
        headers.insert(0, "id")

        # Преобразуем строки данных в списки и добавляем нумерацию
        rows = [list(row) for row in table[1:]]
        for idx, row in enumerate(rows, start=1):
            row.insert(0, idx)

        # Возвращаем таблицу с заголовками и строками
        rows_headers = [headers] + rows
        return [headers] + rows

    def get_column_names(self):
        column_names = [desc[0] for desc in self.cursor.description]
        return column_names

    def get_table(self, table_name):
        self.current_table = table_name
        query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
        self.cursor.execute(query)
        ready_table = self.cursor.fetchall()
        self.table_contents = ready_table
        self.add_header(ready_table)
        ready_table = self.add_ids(ready_table)
        return ready_table

    def get_tables_names(self):
        self.cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        names = []
        for table in self.cursor.fetchall():
            names.append(table[0])
        return names

    def table_sort_by(self, column_to_sort, order):
        query = sql.SQL("SELECT * FROM {} ORDER BY {} {}").format(
            sql.Identifier(self.current_table),
            sql.Identifier(column_to_sort),
            sql.SQL(order)
        )
        self.cursor.execute(query)
        ready_table = self.cursor.fetchall()
        self.table_contents = ready_table
        self.add_header(ready_table)
        ready_table = self.add_ids(ready_table)


        return ready_table

    def on_delete_row(self, row_id):
        row = self.table_contents[row_id]

        # Получаем имена столбцов текущей таблицы
        column_names = self.get_column_names()

        # Формируем условия для удаления строки
        conditions = [
            sql.SQL("{} = {}").format(sql.Identifier(column), sql.Literal(value))
            for column, value in zip(column_names, row)
        ]

        # Объединяем условия через AND
        where_clause = sql.SQL(" AND ").join(conditions)

        # Формируем запрос на удаление
        query = sql.SQL("DELETE FROM {} WHERE {}").format(
            sql.Identifier(self.current_table),
            where_clause
        )

        # Выполняем запрос
        try:
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Row deleted: {row}")
        except Exception as e:
            print(f"Error deleting row: {e}")
            self.conn.rollback()

    def on_add_row(self, values):
        try:
            # Получаем имена столбцов текущей таблицы
            column_names = self.get_column_names()

            # Формируем запрос на добавление строки
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(self.current_table),
                sql.SQL(", ").join(map(sql.Identifier, column_names)),
                sql.SQL(", ").join(sql.Placeholder() for _ in values)
            )

            # Выполняем запрос с переданными значениями
            self.cursor.execute(query, values)
            self.conn.commit()
            print(f"Row added: {values}")
        except Exception as e:
            print(f"Error adding row: {e}")
            self.conn.rollback()


    def on_search_row(self, args):
        if len(args) != 2:
            print("Ошибка: Ожидаются два аргумента - столбец и значение.")
            return

        column, value = args

        try:
            query = sql.SQL("SELECT * FROM {} WHERE {} = {}").format(
                sql.Identifier(self.current_table),  # Имя текущей таблицы
                sql.Identifier(column),  # Столбец для поиска
                sql.Literal(value)  # Значение для поиска
            )

            self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.add_header(result)
            result = self.add_ids(result)


            # Возвращаем результат
            print("Найденные строки:")
            for row in result:
                print(row)

            return result
        except Exception as e:
            print(f"Ошибка при выполнении поиска: {e}")
            return []

    def on_edit_row(self, args):
        if len(args) < 2:
            print("Ошибка: Ожидается массив с минимум двумя элементами - индекс строки и новые значения.")
            return

        row_index = int(args[0])
        new_values = args[1:]

        try:
            # Проверяем, что индекс строки корректен
            if row_index < 0 or row_index >= len(self.table_contents):
                print("Ошибка: Некорректный индекс строки.")
                return

            # Получаем текущую строку и имена столбцов
            current_row = self.table_contents[row_index]
            column_names = self.get_column_names()

            # Формируем пары "столбец = новое значение" для обновления
            updates = []
            for column, new_value, current_value in zip(column_names, new_values, current_row):
                if new_value:  # Если значение не пустое, добавляем его для обновления
                    updates.append(
                        sql.SQL("{} = {}").format(sql.Identifier(column), sql.Literal(new_value))
                    )

            # Если нет значений для обновления, завершаем
            if not updates:
                print("Нет значений для обновления.")
                return

            # Формируем WHERE условие для поиска строки
            conditions = [
                sql.SQL("{} = {}").format(sql.Identifier(column), sql.Literal(value))
                for column, value in zip(column_names, current_row)
            ]
            where_clause = sql.SQL(" AND ").join(conditions)

            # Формируем запрос на обновление строки
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(self.current_table),
                sql.SQL(", ").join(updates),
                where_clause
            )

            # Выполняем запрос
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Row updated: {row_index}, New values: {new_values}")

        except Exception as e:
            print(f"Ошибка при обновлении строки: {e}")
            self.conn.rollback()