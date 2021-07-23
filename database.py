import sqlite3
import itertools
from datetime import datetime


def current_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


class DataBase:

    # instance_example = DataBase('banking_data.db')'
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            nick_name TEXT,
            password TEXT,
            customer_type TEXT,
            balance REAL DEFAULT 0,
            debt REAL DEFAULT 0
            )""")
        self.c.execute("""CREATE TABLE IF NOT EXISTS history (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_datetime TEXT,
            transaction_type TEXT,
            transaction_amount REAL,
            customer_transaction_id INTEGER,
            FOREIGN KEY (customer_transaction_id) REFERENCES customers (customer_id)
            )""")
        self.conn.commit()

    # 1st table insert
    def insert_customer(self, fn, ln, nm, pw, ct):
        """

        :param fn: first_name str
        :param ln: last_name str
        :param nm: nick_name str
        :param pw: password str
        :param ct: customer_type (example: 1) int
        :return:
        """
        self.c.execute("""INSERT INTO customers 
            (first_name, last_name, nick_name, password, customer_type) 
            VALUES (?, ?, ?, ?, ?)""", (fn, ln, nm, pw, ct))
        self.conn.commit()

    # balance
    def update_balance(self, bl, nm):
        self.c.execute("""UPDATE customers SET 
                       balance = ?
                       WHERE nick_name = ?""", (bl, nm))
        self.conn.commit()

    def return_balance(self, nm):
        self.c.execute("""SELECT DISTINCT balance FROM customers WHERE nick_name = ?""", (nm,))
        return self.c.fetchone()[0]

    # debt
    def update_debt(self, db, nm):
        self.c.execute("""UPDATE customers SET 
                       debt = ?
                       WHERE nick_name = ?""", (db, nm))
        self.conn.commit()

    def return_debt(self, nm):
        self.c.execute("SELECT DISTINCT debt FROM customers WHERE nick_name = ?", (nm,))
        return self.c.fetchone()[0]

    # return customer/customers info from the 1st table
    def return_nick_names(self):
        """
        :return: list of nick names
        """
        self.c.execute("SELECT nick_name FROM customers")
        nm_list = list(itertools.chain(*self.c.fetchall()))
        # or nm_list = [i for x in self.c.fetchall() for i in x]
        return nm_list

    def return_customer_info(self, nm):
        self.c.execute("SELECT * FROM customers WHERE nick_name = ?", (nm,))
        return self.c.fetchall()[0]  # [0]- id, [1]- first_name, [2]- last_name...

    def return_customer_pass(self, nm):
        self.c.execute("SELECT DISTINCT password FROM customers WHERE nick_name = ?", (nm,))
        return self.c.fetchone()[0]

    def return_customer_id(self, nm):
        """
        :param nm: nick_name
        :return: cdi/cti
        """
        self.c.execute("SELECT DISTINCT customer_id FROM customers WHERE nick_name = ?", (nm,))
        return self.c.fetchone()[0]

    # delete
    def delete_customer(self, nm):
        # self.c.execute("DELETE FROM composers WHERE composer_id = (?)", (cid))
        self.c.execute("DELETE FROM customers WHERE nick_name = ?", (nm,))
        self.conn.commit()

    # 2nd table
    def insert_history(self, t_type, t_amount, cti):
        """

        :param t_type: transaction_type (example: withdraw), str
        :param t_amount: transaction_amount (example: 321.2), int/float
        :param cti: customer_transaction_id- same as customer_id in customers table, int
        :return:
        """
        t_date = current_datetime()
        self.c.execute("""INSERT INTO history 
            (transaction_datetime, transaction_type, transaction_amount, customer_transaction_id) 
            VALUES (?, ?, ?, ?)""", (t_date, t_type, t_amount, cti))
        self.conn.commit()

    def print_customer_history(self, cti):
        """
        for i in dbi.print_history(cti)[::-1]:  # replace cti param with a customer_id
            print(i[0], i[1], i[2])
        :param cti:
        :return: list of tuples
        (example: [('2021-06-24 00:22:17', 'deposit', 300),
                   ('2021-06-24 00:22:59', 'deposit', 100)])
        """
        self.c.execute("SELECT * FROM history WHERE customer_transaction_id = ?", (cti,))
        return self.c.fetchall()

    # closing connection
    def close_connection(self):
        # or
        # def __del__(self):
        #   self.conn.close()
        self.conn.close()


dbi = DataBase("banking_data.db")
