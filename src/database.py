from dotenv import load_dotenv
import psycopg2
import os


print("Here")


def get_database():
    load_dotenv()
    server = os.environ.get("server")
    database = os.environ.get("database")
    username = os.environ.get("username")
    password = os.environ.get("password")
    port = os.environ.get("port")
    driver = "Devart ODBC Driver for PostgreSQL"
    connect = psycopg2.connect(
        host=server,
        database=database,
        user=username,
        password=password,
        port="5432",
        sslmode="require",
    )
    return connect


def get_table_column_names(connect, table_str: str):
    col_names = []
    try:
        cursor = connect.cursor()
        cursor.execute("select * from " + table_str + " LIMIT 0")
        for desc in cursor.description:
            col_names.append(desc[0])
        cursor.close()
    except Exception as error:
        print(error)
    return col_names