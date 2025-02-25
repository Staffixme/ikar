import datetime
import sys
import time

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QLabel, QTableWidgetItem, QListWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, Slot, QThread, Signal, QObject
import res.qrc.rcc_res
from PySide6.QtCore import QFile

import requests


class MainWindow:
    def __init__(self):
        loader = QUiLoader()
        self.ui = loader.load("main_window.ui", None)  # self передается как родитель
        self.ui.send_message_button.clicked.connect(self.send_message)
        self.table_view = TableManager(self.ui.table_view)
        self.chat_window = ChatsManager(self.ui.chat_window)
        self.setup_lists()
        self.update_tasks()
        self.update_notifications()
        self.ui.table_list.currentTextChanged.connect(self.table_view.set_table)
        self.ui.chats_list.currentTextChanged.connect(self.chat_window.set_chat)
        self.ui.table_list.setCurrentRow(0)
        self.ui.chats_list.setCurrentRow(0)

        self.time_updater = TimeUpdater()
        self.time_updater.time_update.connect(self.update_time)
        self.time_updater.start()
        self.ui.show()

    def setup_lists(self):
        for i in BD_TABLES:
            self.ui.table_list.addItem(i["Table"]["Title"])
        for i in CHATS:
            self.ui.chats_list.addItem(i["Chat"]["Title"])

    def update_time(self, time):
        self.ui.time.setText(time[0])
        self.ui.date.setText(time[1])

    def update_tasks(self):
        self.ui.tasks_list.clear()
        for i in TASKS["Tasks"]:
            self.ui.tasks_list.addItem(f"- {i[0]}\n\n{"✅ Выполнено" if i[1] == 1 else "Не выполнено"}")

    def update_notifications(self):
        self.ui.notifications_list.clear()
        for i in NOTIFICATIONS["Notifications"]:
            self.ui.notifications_list.addItem(i)

    def send_message(self):
        text = self.ui.message_input.text()
        if text:
            now = datetime.datetime.now()
            self.ui.chat_window.addItem(f"User - {datetime.date(now.year, now.month, now.day)} в "
                                        f"{datetime.time(hour=now.hour, minute=now.minute)}\n\n{text}")


class TimeUpdater(QThread):
    time_update = Signal(tuple)

    def run(self, /):
        now = datetime.datetime.now()
        cur_time = f"{now.hour}:{now.minute}"
        cur_date = f"{now.day} {now.strftime("%B")}, {now.year}"
        self.time_update.emit((cur_time, cur_date))
        time.sleep(1)
        self.run()


class TableManager:
    def __init__(self, table: QTableWidget):
        self.table = table

    def set_table(self, item):
        try:
            for i in BD_TABLES:
                if i["Table"]["Title"] == item:
                    table = i
                    break
            self.table.clear()
            self.table.setRowCount(0)
            self.table.parent().parent().parent().parent().findChild(QLabel, "table_name").setText(item)
            self.table.setColumnCount(len(table["Table"]["Columns"]))
            self.table.setHorizontalHeaderLabels(table["Table"]["Columns"])
            for i in range(len(table["Table"]["Items"])):
                item = table["Table"]["Items"][i]
                self.table.setRowCount(self.table.rowCount() + 1)
                for j in range(len(table["Table"]["Columns"])):
                    try:
                        cell = QTableWidgetItem(str(item[j]))
                        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.table.setItem(i, j, cell)
                    except IndexError:
                        cell = QTableWidgetItem("--Null--")
                        cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.table.setItem(i, j, cell)
        except Exception as e:
            print(e)


class ChatsManager:
    def __init__(self, chat: QListWidget):
        self.chat = chat

    def set_chat(self, item):
        try:
            for i in CHATS:
                if i["Chat"]["Title"] == item:
                    chat = i
                    break
            self.chat.clear()
            self.chat.parent().parent().parent().findChild(QLabel, "chat_name").setText(item)
            for i in chat["Chat"]["Messages"]:
                self.chat.addItem(i)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    BD_TABLES = [{"Table":
                      {"Columns": ["id", "Название", "Цена", "Количество"],
                       "Items": [[1, "Вода"], [2, "Хлеб", 31, 10]],
                       "Title": "Товары"}},
                 {"Table":
                      {"Columns": ["id", "Имя", "Должность"],
                       "Items": [[1, "Александр", "Сотрудник"], [2, "Иван", "Сотрудник"], [3, "Анна", "Сотрудник"]],
                       "Title": "Сотрудники"}},
                 {"Table":
                      {"Columns": ["id", "Номинал"],
                       "Items": [[1, 250], [2, 500], [3, 1000], [4, 2500], [5, 5000]],
                       "Title": "Подарочные карты"}},
                 ]

    CHATS = [{"Chat": {"Title": "Иван",
                       "Messages": ["Иван - 2025-02-20 в 16:12:52\n\nПривет!",
                                    "Иван - 2025-02-20 в 16:13:23\n\nДо конца дня нужно закончить проект."]
                       }},
             {"Chat": {"Title": "Анна",
                       "Messages": ["User - 2025-02-16 в 14:32:28\n\nВсе, список задач обновил.",
                                    "Анна - 2025-02-16 в 14:35:02\n\nХорошо, спасибо."]
                       }}
             ]

    TASKS = {"Tasks": [("Доделать проект", 0), ("Распечатать документы", 0), ("Обновить список дел", 1)]}

    NOTIFICATIONS = {"Notifications": ["Вы вошли в учетную запись.", "Список дел был обновлен."]}

    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
