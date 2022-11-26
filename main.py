import sqlite3
import smtplib
import sys
import asyncio
import re
from typing import List
from datetime import datetime as d

sql_db_ = "users_db"
conn = sqlite3.connect(sql_db_)

try:
    conn.execute('CREATE TABLE "users"(id INTEGER PRIMARY KEY AUTOINCREMENT, NAME TEXT NOT NULL,'
                 ' SURNAME TEXT NOT NULL, PATRONYM TEXT NULL,'
                 ' BIRTHDAY TEXT NOT NULL, MAIL TEXT NOT NULL)')
    conn.commit()
except Exception:
    pass


async def insert_intoDB(tup):
    conn.execute(f"""INSERT INTO users(NAME, SURNAME, PATRONYM, BIRTHDAY, MAIL)
                     VALUES{tup}
""")
    conn.commit()


all_users = list()


class Exception:

    @staticmethod
    def alpha_(arg):
        arg1 = input(f"Please, enter a user's {arg}: ")
        if [char.isalpha() or char == " " for char in arg1]:
            return arg1
        else:
            Exception.failure_info()
            return Exception.alpha_(arg)

    @staticmethod
    def digit():
        date_of_birth = input("Enter a user's birthday in the format 'dd.mm.yyyy': ")
        if [char.isdigit() for char in date_of_birth.split(".")] and len(date_of_birth) == 10:
            return date_of_birth
        else:
            Exception.failure_info()
            return Exception.digit()

    @staticmethod
    def failure_info():
        print("You must have made a failure when typed")

    @staticmethod
    def email():
        mail = input(f"Please, enter a user's email: ")
        if re.search(r"\w+@+\w+\S+\w", mail):
            return mail
        else:
            Exception.failure_info()
            return Exception.email()


class User:
    def __init__(self, name, surname, birthday, email, patronym=None):
        self.name = name
        self.surname = surname
        self.patronym = patronym
        self.birthday = birthday
        self.age: int = d.today().year - int(birthday[6:])
        self.email = email

    def __repr__(self):
        return f"{self.get_full_name()},  {self.birthday}"

    def get_full_name(self):
        if self.patronym is None:
            return f"{self.name} {self.surname}"
        return f"{self.name} {self.surname} {self.patronym}"

    def get_short_name(self):
        if self.patronym is None:
            return f"{self.surname} {self.name[0]}."
        return f"{self.surname} {self.name[0]}. {self.patronym[0]}."


def create_user() -> User:  # creates an User instance
    patronym = None
    name = Exception.alpha_("name")
    surname = Exception.alpha_("surname")
    question = input("Type 'y' if you have patrnym, else type any other symbol: ")
    match question:
        case "y":
            patronym = Exception.alpha_("patronym")
    birthday = Exception.digit()
    mail = Exception.email()
    if question == "y":
        new_user = User(name, surname, birthday, mail, patronym)
        all_users.append(new_user)
        loop = asyncio.get_event_loop()
        task = [
            loop.create_task(send_mail(name, mail)),
            loop.create_task(insert_intoDB((name, surname, patronym, birthday, mail)))
        ]
        tasks = asyncio.wait(task)
        loop.run_until_complete(tasks)
        loop.close()
        return new_user
    else:
        new_user = User(name, surname, birthday, mail)
        all_users.append(new_user)
        loop = asyncio.get_event_loop()
        task = [
            loop.create_task(send_mail(name, mail)),
            loop.create_task(insert_intoDB((name, surname, "NULL", birthday, mail)))
        ]
        tasks = asyncio.wait(task)
        loop.run_until_complete(tasks)
        loop.close()
        return new_user


async def send_mail(name, mail):
    msg = f"""
    Dear {name}!

    We are happy to inform you that you became our client. 

    Best regards,
    Company
    """
    sender_mail = "test@gmail.com"  # email is not real.
    password = "trrcznkwfrttrttrt"  # email and password should be yours
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    try:
        server.login(sender_mail, password)
        print("Login success")
        server.sendmail(sender_mail, mail, msg)
        await asyncio.sleep(0.1)
        print(f"Email has been sent to {mail}")
    except BaseException:
        print("Error! We failed to send email! Check configurations")


def find_by_name() -> List:
    found_users: List[tuple] = list()
    name = input("Enter the name of the user to find: ")
    for user in conn.execute(f"""SELECT * FROM users WHERE {name=}""").fetchall():
        found_users.append(user)
    return found_users


def find_by_mail() -> List:
    found_users: List[tuple] = list()
    mail = input("Enter the mail of the user to find: ")
    for user in conn.execute(f"""SELECT * FROM users WHERE {mail=}""").fetchall():
        found_users.append(user)
    return found_users


def find_by_surname() -> List:
    found_users: List[tuple] = list()
    surname = input("Enter the surname of the user to find: ")
    for user in conn.execute(f"""SELECT * FROM users WHERE {surname=}""").fetchall():
        found_users.append(user)
    return found_users


try:
    for i in range(int(input("How many users do you want to create: "))):
        create_user()
except ValueError:
    sys.exit("ValueError. Try again and type a number")
else:
    for user in all_users:
        print(user)

    print(find_by_name())
    print(find_by_surname())
    print(find_by_mail())
