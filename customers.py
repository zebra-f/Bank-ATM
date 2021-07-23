import math
from database import dbi
import time


# can not be imported from bank.py due to circular import
def wrong_input(s):
    print(s)
    time.sleep(1)


def interest_rate(x):
    return 3 * math.log(x, 10)


class BankCustomer:

    def __init__(self, first_name, last_name, nick_name, password, customer_type):

        self.first_name = first_name
        self.last_name = last_name
        self.nick_name = nick_name
        self.password = password
        self.customer_type = customer_type

        self.balance = dbi.return_balance(self.nick_name)

        self.cti = dbi.return_customer_id(self.nick_name)  # same as customer_id (cid)

    def bank_greeting(self):
        print(f'Hello {self.first_name} {self.last_name} in this banking app, \n'
              f'choose what would you like to do and follow pop-up instructions ')

    def transfer(self, t_sum, nm):
        """
        :param t_sum: amount
        :param nm: nickname of a customer we would like to send money to
        :return:
        """
        while True:
            if self.balance < t_sum:
                print('Insufficient funds!')
                input('Press enter to continue!')
                break
            else:
                # from
                self.balance -= t_sum
                dbi.update_balance(self.balance, self.nick_name)
                dbi.insert_history(f'SENT TO {nm.upper()}', t_sum, self.cti)

                # to
                cti = dbi.return_customer_id(nm)

                bl = dbi.return_balance(nm)
                db = dbi.return_debt(nm)

                if db > 0:
                    if db > t_sum:
                        db -= t_sum
                        dbi.update_debt(db, nm)
                        dbi.insert_history(f'RECEIVED FROM {self.nick_name.upper()}', t_sum, cti)
                        break

                    else:
                        x = t_sum - db
                        bl += x
                        dbi.update_debt(0, nm)
                        dbi.update_balance(bl, nm)
                        dbi.insert_history(f'RECEIVED FROM {self.nick_name.upper()}', t_sum, cti)
                        break

                else:
                    bl += t_sum
                    dbi.update_balance(bl, nm)
                    dbi.insert_history(f'RECEIVED FROM {self.nick_name.upper()}', t_sum, cti)
                    break

    def print_history(self):
        print('Your last 5 operations:')
        y = 0
        for x in dbi.print_customer_history(self.cti)[::-1]:
            print(x[1], x[2], x[3])
            y += 1
            if y == 5:
                break

    def delete_customer(self):
        dbi.delete_customer(self.nick_name)


class CreditUser(BankCustomer):

    def __init__(self, first_name, last_name, nick_name, password, customer_type):
        super().__init__(first_name, last_name, nick_name, password, customer_type)
        self.debt = dbi.return_debt(self.nick_name)

    def print_info(self):
        print(f'balance: {round(self.balance, 2)} debt: {round(self.debt, 2)}')

    def withdraw(self, w_sum):
        if w_sum > self.balance:
            x = w_sum - self.balance  # credit without interest
            y = x * (interest_rate(x) / 100)  # interest
            y = round(y, 2)
            z = w_sum + y  # amount with interest

            while True:
                i = input(
                    f'You will be charged an extra {y}$, would you like to continue [y/n]: '
                ).lower().strip()
                if i != 'y' and i != 'n':
                    wrong_input('Something went wrong! Try again.')
                    continue

                elif i == 'y':
                    self.debt += x + y
                    dbi.update_debt(self.debt, self.nick_name)
                    dbi.insert_history('CREDIT WITHDRAW', z, self.cti)

                    dbi.update_balance(0, self.nick_name)
                    self.balance = 0
                    break

                else:
                    print('Have a nice day!')
                    break

        else:
            self.balance -= w_sum
            dbi.update_balance(self.balance, self.nick_name)
            dbi.insert_history('WITHDRAW', w_sum, self.cti)

    def deposit(self, d_sum):
        if self.debt > d_sum:
            self.debt -= d_sum
            dbi.update_debt(self.debt, self.nick_name)
            dbi.insert_history('DEPOSIT', d_sum, self.cti)

        else:
            x = d_sum - self.debt
            self.balance += x
            self.debt = 0
            dbi.update_debt(0, self.nick_name)
            dbi.update_balance(self.balance, self.nick_name)
            dbi.insert_history('DEPOSIT', d_sum, self.cti)


class DebitUser(BankCustomer):

    def print_info(self):
        print(f'balance: {round(self.balance, 2)}')

    def withdraw(self, w_sum):

        if w_sum > self.balance:
            print(f'Insufficient funds! ${self.balance} left on your account.')
            user_input = input("Would you like to withdraw everything? [y/n]: ").strip().lower()
            while True:
                if user_input != 'y' and user_input != 'n':
                    wrong_input('Something went wrong! Try again.')
                    continue

                elif user_input == 'y':
                    x = self.balance
                    self.balance = 0

                    dbi.update_balance(0, self.nick_name)
                    dbi.insert_history('WITHDRAW', x, self.cti)
                    break

                else:
                    print('Have a nice day')
                    break

        else:
            self.balance -= w_sum

            dbi.update_balance(self.balance, self.nick_name)
            dbi.insert_history('WITHDRAW', w_sum, self.cti)

    def deposit(self, d_sum):
        self.balance += d_sum

        dbi.update_balance(self.balance, self.nick_name)
        dbi.insert_history('DEPOSIT', d_sum, self.cti)
