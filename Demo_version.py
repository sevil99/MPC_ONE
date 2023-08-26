
import sys
import threading
from time import time, sleep
import random 
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets, uic 
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import QCoreApplication, QBasicTimer, QDateTime, Qt, QSize, QTimer
import Interface

from DialWind import Ui_Dialog
from ExitWindow import Ui_DialogExit


class RegulWindow(QDialog, Ui_Dialog):
    def __init__(self, root):
        QDialog.__init__(self, root)
        self.setupUi(self)
        self.MainWindow = root
        self.pushButton_13.clicked.connect(self.acept_data)
        self.pushButton_14.clicked.connect(self.reject_data)
        
        self.pushButton_1.clicked.connect(lambda: self.add_text("1"))
        self.pushButton_2.clicked.connect(lambda: self.add_text("2"))
        self.pushButton_3.clicked.connect(lambda: self.add_text("3"))
        self.pushButton_4.clicked.connect(lambda: self.add_text("4"))
        self.pushButton_5.clicked.connect(lambda: self.add_text("5"))
        self.pushButton_6.clicked.connect(lambda: self.add_text("6"))
        self.pushButton_7.clicked.connect(lambda: self.add_text("7"))
        self.pushButton_8.clicked.connect(lambda: self.add_text("8"))
        self.pushButton_9.clicked.connect(lambda: self.add_text("9"))
        self.pushButton_10.clicked.connect(lambda: self.add_text("0"))
        self.pushButton_11.clicked.connect(lambda: self.add_text("."))
        self.pushButton_12.clicked.connect(self.clear_text)

    def add_text(self, text):
        current_text = self.label_value_flow_Ar.text()
        self.label_value_flow_Ar.setText(current_text + text)
        
    def clear_text(self):
        self.label_value_flow_Ar.setText("")

    def acept_data(self):
        self.MainWindow.fakeLineEditO.setText(self.label_value_flow_Ar.text())
        self.close()

    def reject_data(self):
        print('команда сработала')
        self.close()

class RegulWindow2(QDialog, Ui_Dialog):
    def __init__(self, root):
        QDialog.__init__(self, root)
        self.setupUi(self)
        self.MainWindow = root
        self.pushButton_13.clicked.connect(self.acept_data)
        self.pushButton_14.clicked.connect(self.reject_data)
        
        self.pushButton_1.clicked.connect(lambda: self.add_text("1"))
        self.pushButton_2.clicked.connect(lambda: self.add_text("2"))
        self.pushButton_3.clicked.connect(lambda: self.add_text("3"))
        self.pushButton_4.clicked.connect(lambda: self.add_text("4"))
        self.pushButton_5.clicked.connect(lambda: self.add_text("5"))
        self.pushButton_6.clicked.connect(lambda: self.add_text("6"))
        self.pushButton_7.clicked.connect(lambda: self.add_text("7"))
        self.pushButton_8.clicked.connect(lambda: self.add_text("8"))
        self.pushButton_9.clicked.connect(lambda: self.add_text("9"))
        self.pushButton_10.clicked.connect(lambda: self.add_text("0"))
        self.pushButton_11.clicked.connect(lambda: self.add_text("."))
        self.pushButton_12.clicked.connect(self.clear_text)

    def add_text(self, text):
        current_text = self.label_value_flow_Ar.text()
        self.label_value_flow_Ar.setText(current_text + text)
        
    def clear_text(self):
        self.label_value_flow_Ar.setText("")

    def acept_data(self):
        self.MainWindow.fakeLineEditO_2.setText(self.label_value_flow_Ar.text())
        self.close()

    def reject_data(self):
        self.close()

class ExitWindow(QDialog, Ui_DialogExit):
    def __init__(self, root):
        QDialog.__init__(self, root)
        self.setupUi(self)
        self.MainWindow = root

class MainWindow(QMainWindow, Interface.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.flow_value = 1
        
        self.btn_openO.clicked.connect(self.click_openO) #функции нажатия на кнопки
        self.btn_openAr.clicked.connect(self.click_openAr)
        self.btn_closeO.clicked.connect(self.click_closeO)
        self.btn_closeAr.clicked.connect(self.click_closeAr)
        self.btn_regulateO.clicked.connect(self.click_regulateO)
        self.btn_regulateAr.clicked.connect(self.click_regulateAr)
        self.btn_installO.clicked.connect(self.click_installO)
        self.btn_installAr.clicked.connect(self.click_installAr)
        self.fakeButtonO.clicked.connect(self.show_keyboard_dialogO)
        self.fakeButtonO_2.clicked.connect(self.show_keyboard_dialogAr)
        self.pushButton.clicked.connect(self.Exit_)                   # клик на кнопку ВЫХОД


        self.setWindowFlags(Qt.FramelessWindowHint)             # убирает шапку приложения
        
    def Exit_(self):                                         # при выходе из программы
        print('Активирован выход')
        self.ExitWindow = ExitWindow(self)
        self.ExitWindow.show()
        global current_command
        current_command = 'Exit'

    def show_keyboard_dialogO(self):
        dialog = RegulWindow(self)
        dialog.show()
        dialog.exec()

    def show_keyboard_dialogAr(self):
        dialog = RegulWindow2(self)
        dialog.show()
        dialog.exec()

    def showEvent(self, event): #запускает программу при при её открытии 
        global current_command 
        print('Продукт Vasiliev Embedded Software Technology. Все права защищены')
        current_command = '010300040002'
        self.start_readout()

    def start_readout(self):
        global current_command 
        a = '010300040002'
        if current_command == 'Exit':
            sleep(2)
            print('Идет выключение')
            self.fn_sendcmd('010F000200020102')
            self.fn_sendcmd('020F000200020102')
            self.ExitWindow.close()
            self.close()
        else:
            if current_command != a and current_command != 'Exit':
                print('модуль получил глобальную команду')
                self.thread1 = threading.Thread(target = self.fn_sendcmd, args=(current_command,) )
                self.thread1.start()
                self.thread1.join()
                current_command = '010300040002'
            else:
                print('modul 1 made/ ')
                self.thread1 = threading.Thread(target = self.fn_sendcmd, args=(a,) )
                self.thread1.start()
                self.thread1.join()
                self.updatelabeltextO(self.flow_value)
            self.timer = threading.Timer(0.5, self.second_part, args=(str,))
            self.timer.start()
 
    def second_part(self, str):
        a = '020300040002'
        print('modul 2 made /')
        self.thread1 = threading.Thread(target = self.fn_sendcmd, args=(a,) )
        self.thread1.start()
        self.thread1.join()
        self.updatelabeltextAr(self.flow_value)
        self.start_readout()

    def updatelabeltextAr(self, number):
        number = str(round(number/1.45, 2))
        self.label_realflowAr.setText(number)

    def updatelabeltextO(self, number):
        number = str(round(number, 2))
        self.label_realflowO.setText(number)

    def fn_sendcmd(self, number):                                       # Данная функция является иммитацией функции в Work_version, которая требует инициализации портов
        print("def fn_sendcmd получило значение - ", number)                         # данные
        self.ed_id= number[0:2]                           # адрес устройства ID
        self.ed_cmd=number[2:4]                           # номер команды
        self.ed_adr=number[4:8]                           # адрес регистра
        self.ed_count=number[8:17]                          # данные
        self.flow_value = random.randint(0,100)
        sleep(1)

    def click_openO(self):
        global current_command  
        current_command = "010F000200020101"
        print("def click_openO выполнено")

    def click_openAr(self):
        global current_command  
        current_command = "020F000200020101"
        print("def click_openAr выполнено")
        
    def click_closeO(self):
        global current_command  
        current_command = "010F000200020102"
        print("def click_closeO выполнено")

    def click_closeAr(self):
        global current_command  
        current_command = "020F000200020102"
        print("def click_closeAr выполнено")
        
    def click_regulateO(self):
        global current_command  
        current_command = "010F000200020100"
        print("def click_regulateO выполнено")
        
    def click_regulateAr(self):
        global current_command  
        current_command = "020F000200020100"
        print("def click_regulateAr выполнено")
        
    def click_installO(self):
        value_flow_1 = self.fakeLineEditO.text() #значение из TextEdit в строку
        try:
            value_flow_1 = float(value_flow_1)
            procent = int((value_flow_1/90)*10000)
            procent1 = hex(procent)
            if value_flow_1 > 90:
                self.show_error("Значение должно быть не больше 90 л/с")
            else:
                procent1=str(procent1)
                if len(procent1) < 6:
                    procent2 = "0" + procent1[2:6]
                else:
                    procent2 = procent1[2:6]
                type_command = "02060004" + procent2
                global current_command  
                current_command = type_command
        except: 
            self.show_error('Введено некорректное значение потока')

    def click_installAr(self):
        print('click installAr')
        value_flow_1 = self.fakeLineEditO_2.text() #значение из TextEdit в строку
        try:
            print('try dona')
            value_flow_1 = float(value_flow_1)
            procent = int((value_flow_1/90)*10000*1.45)
            procent1 = hex(procent)
            if value_flow_1 > 90:
                self.show_error("Значение должно быть не больше 90 л/с")
            else:
                print('else done')
                procent1=str(procent1)
                if len(procent1) < 6:
                    procent2 = "0" + procent1[2:6]
                else:
                    procent2 = procent1[2:6]
                type_command = "01060004" + procent2
                print('type_command', type_command)
                global current_command  
                current_command = type_command
        except: 
            self.show_error('Введено некорректное значение потока')

    def show_error(self, str): #вывод ошибки 
        error = QMessageBox()
        error.setWindowTitle("Ошибка")
        error.setText(str)
        error.setIcon(QMessageBox.Warning)
        error.setStandardButtons(QMessageBox.Ok)
        error.exec()

def main():                                                     # открытие главного окна
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__": main()
