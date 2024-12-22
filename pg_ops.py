from asyncio import all_tasks

import pg_back
import pg_gui
from pg_back import PG_Back
from pg_gui import PG_Gui


class PG_Ops:
    back_ops = PG_Back
    gui_ops = PG_Gui
    all_tables = []

    def __init__(self, dbname, username, password, host):
        self.back_ops = PG_Back(dbname, username, password, host)
        self.gui_ops = PG_Gui(self.back_ops)
        self.gui_ops.gui_start()

    def get_tables_list(self):
        return self.back_ops.get_tables_names()

