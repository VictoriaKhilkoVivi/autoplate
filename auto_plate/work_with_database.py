import sqlite3


def create_table_in_database():
    with sqlite3.connect('drivers.db') as conn:
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS drivers(
           id INT PRIMARY KEY,
           fio TEXT,
           phone TEXT,
           email TEXT,
           plate_number TEXT);
        """)
        conn.commit()


def insert_in_database(data):
    with sqlite3.connect('drivers.db') as conn:
        cur = conn.cursor()
        cur.execute("""INSERT INTO drivers(id, fio, phone, email, plate_number) 
           VALUES(?, ?, ?, ?, ?);""", data)
        conn.commit()


def find_by_plate_number(plate_number):
    with sqlite3.connect('drivers.db') as conn:
        cur = conn.cursor()
        cur.execute("""SELECT * FROM drivers WHERE plate_number=?;""", (plate_number,))
        driver = cur.fetchone()
        return driver


if __name__ == '__main__':
    create_table_in_database()
    plate_number = 'B081KE123'
    # data = ('1', 'Alex Al Al', '+79999999999', 'mail.mail@mail.ru', plate_number)
    data = ('2', 'Khilko Victoria', '+79999999888', 'example@mail.ru', plate_number)
    insert_in_database(data)
    # data_about_driver = find_by_plate_number(plate_number)
    # print(data_about_driver)
