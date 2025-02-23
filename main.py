from PySide6.QtWidgets import QApplication, QMainWindow, QInputDialog, QDialog, QLineEdit, QPushButton, QLabel,QListWidget
from PySide6.QtCore import QTimer, Qt, QFile
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtWidgets
import sys
import io
import sqlite3

class Cilantromes(QMainWindow):
    def __init__(self):
        self.user_in_mes = False
        super().__init__()
        ui_file = QFile("face.ui")
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        self.users = ''
        self.login_user = ''
        self.data = list()

        # Доступ к элементам интерфейса
        self.login = self.ui.findChild(QLineEdit, "login")
        self.password = self.ui.findChild(QLineEdit, "password")
        self.getlog = self.ui.findChild(QPushButton, "getlog")
        self.getregistr = self.ui.findChild(QPushButton, "getregistr")
        self.add = self.ui.findChild(QPushButton, "add")
        self.delet = self.ui.findChild(QPushButton, "delet")
        self.send = self.ui.findChild(QPushButton, "send")
        self.label = self.ui.findChild(QLabel, "label")
        self.label_2 = self.ui.findChild(QLabel, "label_2")
        self.label_3 = self.ui.findChild(QLabel, "label_3")
        self.error = self.ui.findChild(QLabel, "error")
        self.error1 = self.ui.findChild(QLabel, "error1")
        self.peoplelist = self.ui.findChild(QListWidget, "peoplelist")
        self.messagelist = self.ui.findChild(QListWidget, "messagelist")
        self.message = self.ui.findChild(QLineEdit, "message")

        # Подключение сигналов к слотам
        self.getlog.clicked.connect(self.log)
        self.getregistr.clicked.connect(self.registr)
        self.add.clicked.connect(self.add_user)
        self.delet.clicked.connect(self.del_user)
        self.peoplelist.itemClicked.connect(self.get_username)
        self.send.clicked.connect(self.send_mes)

        # Скрытие лишних виджетов
        self.add.hide()
        self.delet.hide()
        self.messagelist.hide()
        self.peoplelist.hide()
        self.send.hide()
        self.message.hide()
        self.getregistr.hide()

        # Таймер для обновления
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updt)
        self.timer.start(1000)

        self.password.setEchoMode(QLineEdit.Password)

    def log(self):
        flag = True
        login = self.login.text()
        self.login_user = login
        password = self.password.text()

        db = sqlite3.connect('members.db')
        c = db.cursor()
        self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
        db.commit()
        db.close()

        for q in range(len(self.data)):
            if login == self.data[q][1]:
                if password == self.data[q][2]:
                    self.error.hide()
                    self.getlog.hide()
                    self.getregistr.hide()
                    self.label.hide()
                    self.label_2.hide()
                    self.label_3.hide()
                    self.login.hide()
                    self.password.hide()
                    self.add.show()
                    self.delet.show()
                    self.messagelist.show()
                    self.peoplelist.show()
                    self.send.show()
                    self.message.show()
                    flag = False
                    db = sqlite3.connect(f'local_{self.login_user}.db')
                    c = db.cursor()
                    try:
                        c.execute("""CREATE TABLE info (
                                    login text,
                                    message text
                                )""")
                    except:
                        pass
                    self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
                    db.close()
                    if len(self.data) > 0:
                        for j in range(len(self.data)):
                            self.peoplelist.addItem(self.data[j][1])
                    self.user_in_mes = True

                    break
                else:
                    self.error.setText('Неверный пароль')
                    flag = False
                    break
        if flag:
            self.error.setText('Аккаунт отсутствует')
            self.getregistr.show()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            if self.users != '' and self.login_user != '':
                self.send_mes()

    def updt(self):
        flag_user_people = False  # человек в поле пользователей
        if self.login_user != '' and self.user_in_mes:
            db = sqlite3.connect('members.db')
            c = db.cursor()
            newmes = c.execute(f"""SELECT newmessage FROM info WHERE login = '{self.login_user}'""").fetchall()[0][
                0].split('α1')
            db.close()
            newmes.remove('')
            if len(newmes) > 0:
                db = sqlite3.connect(f'local_{self.login_user}.db')
                c = db.cursor()
                logins = c.execute(f'''SELECT login FROM info''').fetchall()
                logins = list(map(lambda x: x[0], logins))
                for i in range(len(newmes)):
                    if newmes[i].split(':')[0] not in logins:
                        print(newmes[i].split(':')[0])
                        c.execute(f"INSERT INTO info VALUES ('{newmes[i].split(':')[0]}',  '')")
                        db.commit()
                    mes = c.execute(f'''SELECT message FROM info
                                    WHERE login = '{newmes[i].split(':')[0]}' ''').fetchall()[0][0]
                    c.execute(f'''UPDATE info
                                SET message = '{mes + newmes[i] + 'α1'}'
                                WHERE login = '{newmes[i].split(':')[0]}' ''')

                    if self.peoplelist.count() == 0:
                        self.peoplelist.addItem(newmes[i].split(':')[0])
                    else:
                        for j in range(self.peoplelist.count()):
                            if newmes[i].split(':')[0] in self.peoplelist.item(j).text():
                                flag_user_people = True
                                break

                        if not flag_user_people:
                            self.peoplelist.addItem(newmes[i].split(':')[0])
                db.commit()
                db.close()

                db = sqlite3.connect('members.db')
                c = db.cursor()
                c.execute(f'''UPDATE info
                            SET newmessage = '' 
                            WHERE login = '{self.login_user}' ''')
                db.commit()
                db.close()
                if self.users != '':
                    for i in range(self.peoplelist.count()):
                        if self.peoplelist.item(i).text() == self.users:
                            self.get_username(self.peoplelist.item(i))
                            break

    def registr(self):
        login = self.login.text()
        password = self.password.text()
        for i in range(len(self.data)):
            if login == self.data[i][1]:
                self.error.setText('Такой аккаунт уже существует')
                break
            elif self.login == '' or password == '':
                self.error.setText('Неверный формат')
            else:
                self.getregistr.hide()
                db = sqlite3.connect('members.db')
                c = db.cursor()
                c.execute(f"INSERT INTO info VALUES ('{login}',  '{password}', '')")
                db.commit()
                db.close()
                self.error.setText('Аккаунт создан')
                break

    def del_user(self):
        flag_not_user = False
        flag_this_user = False
        correct = True
        name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Кого вы хотите удалить?")
        db = sqlite3.connect(f'local_{self.login_user}.db')
        c = db.cursor()
        self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
        db.commit()
        db.close()
        if ok_pressed:
            while correct:
                for i in range(len(self.data)):
                    if self.login_user == name:
                        flag_this_user = True
                        break
                    elif name == self.data[i][1]:
                        flag_not_user = False
                        correct = False
                        break
                    else:
                        flag_not_user = True
                if not correct:
                    break
                if flag_this_user:
                    name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Это вы")
                elif flag_not_user:
                    name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Такого пользователя нет")
                if not ok_pressed:
                    break
                flag_not_user = False
                flag_this_user = False
        if ok_pressed:
            db = sqlite3.connect(f'local_{self.login_user}.db')
            c = db.cursor()
            c.execute(f"DELETE FROM info WHERE login = '{name}'")
            self.data = c.execute("SELECT login FROM info").fetchall()
            db.commit()
            db.close()
            self.peoplelist.clear()
            self.messagelist.clear()
            for i in range(len(self.data)):
                self.peoplelist.addItem(self.data[i][0])

    def add_user(self):
        flag_not_user = False
        flag_this_user = False
        correct = True
        name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Кому вы хотите написать?")
        db = sqlite3.connect('members.db')
        c = db.cursor()
        self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
        db.commit()
        db.close()
        if ok_pressed:
            while correct:
                for i in range(len(self.data)):
                    if self.login_user == name:
                        flag_this_user = True
                        break
                    elif name == self.data[i][1]:
                        flag_not_user = False
                        correct = False
                        break
                    else:
                        flag_not_user = True
                if not correct:
                    break
                if flag_this_user:
                    name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Это вы")
                elif flag_not_user:
                    name, ok_pressed = QInputDialog.getText(self, "Введите имя", "Такого пользователя нет")
                if not ok_pressed:
                    break
                flag_not_user = False
                flag_this_user = False
        if ok_pressed:

            flag_in_db = False
            self.peoplelist.addItem(name)
            db = sqlite3.connect(f'local_{self.login_user}.db')
            c = db.cursor()
            self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
            for i in range(len(self.data)):
                if name == self.data[i][1]:
                    flag_in_db = True
                    break
            if not flag_in_db:
                c.execute(f"INSERT INTO info VALUES ('{name}', '')")
                db.commit()
            db.close()

    def get_username(self, item):
        self.users = item.text()
        data_user = ''
        db = sqlite3.connect(f'local_{self.login_user}.db')
        c = db.cursor()
        self.data = c.execute("SELECT rowid,  * FROM info").fetchall()
        db.close()
        for i in range(len(self.data)):
            if item.text() == self.data[i][1]:
                data_user = self.data[i][2].split('α1')
                break
        data_user.remove('')
        self.messagelist.clear()
        if len(data_user) > 0:
            self.messagelist.addItems(data_user)

    def send_mes(self):
        self.error1.clear()
        text = self.message.text()
        if self.users == '':
            self.error1.setText('Никто не выбран')
        else:
            if text == '':
                self.error1.setText('Пустое сообщение')
            else:
                self.message.clear()
                db = sqlite3.connect('members.db')
                c = db.cursor()
                mes = c.execute(f'''SELECT newmessage FROM info
                                WHERE login = '{self.users}' ''').fetchall()[0][0]
                mes += f'{self.login_user}:{text}α1'
                c.execute(f'''UPDATE info
                        SET newmessage = '{mes}'
                        WHERE login = '{self.users}'
                ''')
                db.commit()
                db.close()

                db = sqlite3.connect(f'local_{self.login_user}.db')
                c = db.cursor()
                mes = c.execute(f'''SELECT message FROM info
                WHERE login = '{self.users}' ''').fetchall()[0][0]
                mes += f"{self.login_user}:{text}α1"
                c.execute(f'''UPDATE info
                        SET message = '{mes}'
                        WHERE login = '{self.users}' ''')
                db.commit()
                db.close()
                self.messagelist.addItem(f'{self.login_user}:{text}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Cilantromes()
    ex.setFixedSize(718, 519)
    ex.show()
    sys.exit(app.exec())