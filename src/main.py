from database import get_database
from database import get_table_column_names

connect = get_database()
exam = get_table_column_names(connect, "exams")
print(exam)
