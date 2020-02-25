import pymysql.cursors
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup
import os
import hashlib
import GUI
import cryptography

results = []
recommend_cpu = []
recommend_gpu = []


class Database():

    def __init__(self):
        self.connection = pymysql.connect(host='localhost',
                                          user='root',
                                          password='password',
                                          db='Hardware',
                                          charset='utf8mb4',
                                          cursorclass= pymysql.cursors.DictCursor)

    def openFile(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            file = open(fileName)
            data = file.read()
            soup = BeautifulSoup(data, "lxml")
            for item in soup.find_all('strong'):
                results.append(float(item.text))
        print('Score =', results[1])
        print('Fps =', results[0])

    def registration(self, user1, password):
        salt = os.urandom(32)
        pass_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        key_string = str(pass_key)
        salt_str = str(salt)

        try:
            with self.connection.cursor() as cursor:
                last_row = cursor.execute("SELECT `UserID` FROM Hardware.Login")
                new_row = last_row+1

                update_sql1 = "UPDATE Hardware.Login SET `Username` = %s WHERE `UserID` = %s"
                data1 = (user1, new_row)

                update_sql2 = "UPDATE Hardware.Login SET `PasswordHash` = %s WHERE `UserID` = %s"
                data2 = (key_string, new_row)

                salt_push = "UPDATE Hardware.Login SET `PasswordSalt` = %s WHERE `UserID` = %s"
                data3 = (salt_str, new_row)

                for i in range(1, last_row):
                    cursor.execute("SELECT `Username` FROM Hardware.Login WHERE `UserID` = %s", i)
                    rows = cursor.fetchone()
                    if rows["Username"] == user1:
                        print('username taken')
                        return self.reject_user()
                    else:
                        print('not taken')

                cursor.execute("INSERT INTO Hardware.Login(UserID) VALUES(%s)", new_row)
                cursor.execute(update_sql1, data1)
                cursor.execute(update_sql2, data2)
                cursor.execute(salt_push, data3)

                self.connection.commit()

        except pymysql.err.IntegrityError:
            print('Wrong')

        gui = GUI.Window()
        next_win = gui.mainWindow()
        return next_win

    def login(self, user2, password):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT `PasswordSalt` FROM Hardware.Login WHERE `Username` = %s", user2)
                rows1 = cursor.fetchone()
                new_sec = rows1["PasswordSalt"]
                remove_b = new_sec[1:-1]
                part1 = "b'"; part2 = "'"
                finalpart = part1+remove_b+part2
                pass_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), finalpart, 100000)

                cursor.execute("SELECT `PasswordHash` FROM Hardware.Login WHERE `Username` = %s", user2)
                rows2 = cursor.fetchone()
                if pass_key == rows2['PasswordHash']:
                    print('correct password')
                else:
                    print('wrong password')
                    return self.reject_user()

                self.connection.commit()

        except pymysql.err.IntegrityError:
            print('Wrong')

    def salt_hash(self, plain_word):
        salt = os.urandom(32)
        pass_key = hashlib.pbkdf2_hmac('sha256', plain_word.encode('utf-8'), salt, 100000)
        print(pass_key)
        return pass_key

    def reject_user(self):
        gui = GUI.Window()
        gui.reject_reg()
        return gui.loginWindow()

    def pop_name(self):
        text, okPressed = QInputDialog.getText(self, "Component Name", "name:", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
        elif okPressed and text == '':
            self.pop_name()

    def getCpuDetails(self):
        temp = []
        temp2 = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT `GPU` FROM Hardware.Parts WHERE CPU = 6700")
                rows = cursor.fetchall()
                for i in range(0, len(rows)):
                    found = rows[i]['GPU']
                    temp.append(found)
                for n in range(len(temp)):
                    val = temp[n]
                    new_val = val[0:-1]
                    temp2.append(new_val)

            self.connection.commit()

        except pymysql.err.IntegrityError:
            print('Wrong')

        recommend_cpu = list(dict.fromkeys(temp2))
        print(recommend_cpu)
        return recommend_cpu

    def getGpuDetails(self):
        temp = []
        temp2 = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT `CPU` FROM Hardware.Parts WHERE GPU = 1080")
                rows = cursor.fetchall()
                for i in range(0, len(rows)):
                    found = rows[i]['CPU']
                    temp.append(found)
                for n in range(len(temp)):
                    val = temp[n]
                    new_val = val[0:-1]
                    temp2.append(new_val)

            self.connection.commit()

        except pymysql.err.IntegrityError:
            print('Wrong')

        recommend_gpu = list(dict.fromkeys(temp2))
        print(recommend_gpu)
        return recommend_gpu

    def cpu_URL(self):
        part1 = 'https://www.amazon.co.uk/s?k='
        part2 = '&ref=nb_sb_noss_2'
        for i in range(0, len(recommend_cpu)):
            try:
                split1 = recommend_cpu[i].split(' ')
                joined = split1[0] + split1[1]
                url = part1 + joined + part2
            except:
                url = part1 + recommend_cpu[i] + part2
            print(url)

    def gpu_URL(self):
        part1 = 'https://www.amazon.co.uk/s?k='
        part2 = '&ref=nb_sb_noss_2'
        for i in range(0, len(recommend_gpu)):
            split1 = recommend_gpu[i].split(' ')
            joined = split1[0] + split1[1]
            url = part1 + joined + part2
            print(url)
