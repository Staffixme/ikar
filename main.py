import datetime
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QLabel
from PySide6.QtUiTools import QUiLoader
import res.qrc.rcc_res
from PySide6.QtCore import QFile

import requests


class MainWindow:
    def __init__(self):
        loader = QUiLoader()
        self.ui = loader.load("main_window.ui", None)  # self передается как родитель
        self.ui.table_list.setCurrentRow(0)
        self.ui.send_message_button.clicked.connect(self.send_message)
        self.table_view = TableManager(self.ui.table_view)
        self.ui.show()


    def send_message(self):
        text = self.ui.message_input.text()
        if text:
            now = datetime.datetime.now()
            self.ui.chat_window.addItem(f"User - {datetime.date(now.year, now.month, now.day)} в "
                                        f"{datetime.time(hour=now.hour, minute=now.minute)}\n\n{text}")


class TableManager:
    def __init__(self, table: QTableWidget):
        self.table = table
        self.set_table()

    def set_table(self):
        try:
            table = requests.get("...").json()
            print(table)
            self.table.setColumnCount(len(table["Table"]["Columns"]))
            self.table.setHorizontalHeaderLabels(table["Table"]["Columns"])
            for i in range(len(table["Table"]["Items"])):
                item = table["Table"]["Items"][i]
                self.table.setRowCount(self.table.rowCount() + 1)
                for j in range(len(table["Table"]["Columns"])):
                    self.table.setCellWidget(i, j, QLabel(str(item[j])))
        except Exception as e:
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
