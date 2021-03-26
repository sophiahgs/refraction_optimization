from dotenv import load_dotenv
import psycopg2
import os
import numpy as np
import pandas as pd


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


def get_table_colmun_index(exam_name, looking_for):
    return [exam_name.index(i) for i in exam_name if looking_for in i][0]


def get_table(connect, table_str: str):
    table = []
    try:
        cursor = connect.cursor()
        postgreSQL_select_Query = "select * from {}".format(table_str)
        cursor.execute(postgreSQL_select_Query)
        table = cursor.fetchall()
        cursor.close()
    except Exception as error:
        print(error)
    return table


def convert_table_in_list(list_input, list_name_column):
    return pd.DataFrame(np.array(list_input), columns=list_name_column)


def close_connexion(connect):
    if connect:
        connect.close()
        print("PostgreSQL connection is closed")
