import pg_ops
from pg_ops import PG_Ops

if __name__ == "__main__":
    database = 'postgres'
    username = 'postgres'
    password = 'admin'
    host = 'localhost'

    main_pg = PG_Ops(database, username, password, host)
