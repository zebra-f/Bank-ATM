from database import dbi
from customers import CreditUser, DebitUser
import hashlib
import time
import os


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def sha_password(x):
    byte_pass = str.encode(x, "utf-8")
    crypt = hashlib.sha256()
    crypt.update(byte_pass)
    return crypt.hexdigest().strip()


def wrong_input(s):
    print(s)
    time.sleep(1)


def amount_check():
    while True:
        try:
            x = int(input('How much: '))
        except ValueError:
            print('Wrong input, try again')
            time.sleep(1)
            continue
        else:
            return x


def sign_in():
    """
    True- sing in
    False- sing up
    :return: Information need to create an user instance
    """
    while True:
        while True:
            x = input("Sign in or register [s/r]: ").lower().strip()
            if x != 's' and x != 'r':
                wrong_input('Something went wrong! Try again.')
                continue
            else:
                break

        if x == 's':
            while True:
                nm = input("Login: ").lower().strip()
                if nm not in dbi.return_nick_names():
                    wrong_input('Something went wrong! Try again.')
                    continue
                else:
                    break
            while True:
                x = input('Password: ')
                pw = sha_password(x)
                if pw != dbi.return_customer_pass(nm):
                    wrong_input('Wrong password! Try again.')
                    continue
                else:
                    break

            return True, nm, pw

        elif x == 'r':
            print('Fill up the information needed to register')

            def fn_nm_check(n): return n.isalpha() and len(n) > 1
            while True:
                fn = input("First name: ").title().strip()
                if not fn_nm_check(fn):
                    wrong_input('Something went wrong! Try again.')
                    continue
                else:
                    break
            while True:
                ln = input("Last name: ").title().strip()
                if not fn_nm_check(ln):
                    wrong_input('Something went wrong! Try again.')
                    continue
                else:
                    break
            while True:
                nm = input(
                    "Nickname (at least 5 characters and no longer than 10) \n"
                    "first 3 must be a-z: "
                ).lower().strip()
                if nm[:3].isalpha() and 11 > len(nm) > 4 and nm not in dbi.return_nick_names():
                    nm_check = None  # gets rid of warning
                    for x in nm[3:]:
                        if x.isalpha() or x.isnumeric():
                            nm_check = True
                        else:
                            nm_check = False
                            break

                    if nm_check:
                        break
                else:
                    wrong_input('Something went wrong! Try again.')
                    continue
            while True:
                x = input('Password: ')
                pw = None  # gets rid of warning
                if len(x) < 5:
                    wrong_input('Password must be at least 5 character long! Try again.')
                    continue
                else:
                    pw = sha_password(x)
                    break
            while True:
                ct = input("Would you like a credit card or a debit card [c/d]: ").lower().strip()
                if ct != 'c' and ct != 'd':
                    wrong_input('Something went wrong! Try again.')
                    continue
                else:
                    break

            if ct == 'c':
                ct = 'credit'
            else:
                ct = 'debit'

            return False, fn, ln, nm, pw, ct

        else:
            wrong_input('Something went wrong! Try again.')
            continue


def user_instance():
    # True- sign up, else- sign in
    x = sign_in()
    if not x[0]:  # x = (False, fn, ln, nm, pw, ct)
        fn = x[1]
        ln = x[2]
        nm = x[3]
        pw = x[4]
        ct = x[5]

        dbi.insert_customer(fn, ln, nm, pw, ct)

        if x[5] == 'credit':
            return CreditUser(fn, ln, nm, pw, ct)
        else:
            return DebitUser(fn, ln, nm, pw, ct)

    else:  # x = (True, nm, pw)
        nm = x[1]
        fn = dbi.return_customer_info(nm)[1]
        ln = dbi.return_customer_info(nm)[2]
        pw = dbi.return_customer_info(nm)[4]

        if dbi.return_customer_info(nm)[5] == 'credit':

            return CreditUser(fn, ln, nm, pw, 'credit')
        else:
            return DebitUser(fn, ln, nm, pw, 'debit')


def main():
    ui = user_instance()
    clear_terminal()
    ui.bank_greeting()
    while True:
        ui.print_info()
        x = input(
            '1 deposit,\n'
            '2 withdraw,\n'
            '3 transfer,\n'
            '4 history, \n'
            '9 delete account, \n'
            '0 exit bank app: '
        ).strip()
        if x == '1':
            y = amount_check()
            ui.deposit(y)
            clear_terminal()
            continue
        elif x == '2':
            y = amount_check()
            ui.withdraw(y)
            clear_terminal()
            continue
        elif x == '3':
            t_sum = amount_check()
            while True:
                nm = input("Send to: ").strip()
                if nm == ui.nick_name:
                    print("Can't do that operation")
                    time.sleep(0.5)
                    clear_terminal()
                    continue
                elif nm not in dbi.return_nick_names():
                    wrong_input('Wrong nickname')
                    y = input("Try again [y] or return to main menu [press Enter]: ").strip()
                    if y == 'y':
                        continue
                    else:
                        clear_terminal()
                        break
                else:
                    ui.transfer(t_sum, nm)
                    clear_terminal()
                    break
        elif x == '4':
            clear_terminal()
            ui.print_history()
            input(' \nPress enter to continue. ')
            clear_terminal()
        elif x == '9':
            ui.delete_customer()
            print('Goodbye')
            time.sleep(1)
            clear_terminal()
            exit()
        elif x == '0':
            print('Goodbye!')
            time.sleep(1)
            clear_terminal()
            dbi.close_connection()
            exit()
        else:
            wrong_input('Something went wrong! Try again.')
            clear_terminal()
            ui.print_info()
            continue


main()
