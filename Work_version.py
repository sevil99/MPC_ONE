# -*- coding: utf-8 -*-

import time
import sys
import serial
import PyQt5
import os
import board
import busio
import binascii
import minimalmodbus
from RPi import GPIO
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMessageBox, QApplication, QPushButton, QWidget
from PyQt5 import QtCore, QtGui, QtWidgets, uic 
from time import time, sleep
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
import Interface
from DialWind import Ui_Dialog
from ExitWindow import Ui_DialogExit
# DU_Pin_Rpi_Master=18       # Пин, который определяет RPi - Master или Slave при использовании MAX485

s=serial.Serial(                                                # подключение и инициализация порта
	port='/dev/serial/by-id/usb-Silicon_Labs_CP2104_USB_to_UART_Bridge_Controller_0333EFC1-if00-port0', #'/dev/serial0'     /dev/ttyUSB0 #/dev/serial/by-id/usb-Silicon_Labs_CP2104_USB_to_UART_Bridge_Controller_0333EFC1-if00-port0
	baudrate=19200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1)                                        # 1 c ожидание данных

                                                        # Для вычисления СRС16 табличным способом
CRC_High=[
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
    0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
    0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
    0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
    0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
    0x40]
CRC_Low=[
    0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
    0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
    0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
    0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
    0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xE7,
    0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
    0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
    0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
    0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
    0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
    0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
    0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
    0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
    0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
    0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
    0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
    0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
    0x40]

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

        

        #self.Exit.clicked.connect(self.Exit_)                   # клик на кнопку ВЫХОД
        #GPIO.setmode(GPIO.BCM)                                  # Инициализация пина RPi - Master (используется при MAX485)
        #GPIO.setup(DU_Pin_Rpi_Master, GPIO.OUT)
        #GPIO.output(DU_Pin_Rpi_Master, True)
        self.setGeometry(70, 0, 1024, 600)                        # расположение главновго окна
        self.setWindowFlags(Qt.FramelessWindowHint)             # убирает шапку приложения
        #icon_switch_off = QtGui.QIcon()                         # картинка на кнопке ВЫХОД
        #icon_switch_off.addPixmap(QtGui.QPixmap("/home/pi/Desktop/Modbus/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        #self.Exit.setIcon(icon_switch_off)                      # добавляет иконку
        #self.Exit.setIconSize(QtCore.QSize(57, 57))

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
        current_command = '020300040002'
        self.start_readout()

    def start_readout(self):
        global current_command 
        a = '020300040002'
        if current_command == 'Exit':
            sleep(2)
            print('Идет выключение')
            self.fn_sendcmd('010F000200020102')
            self.fn_sendcmd('020F000200020102')
            self.ExitWindow.close()
            self.close()
        else:
            if current_command != a:
                thread1 = threading.Thread(target = self.fn_sendcmd, args=(current_command,) )
                thread1.start()
                thread1.join()
                current_command = '020300040002'
            else:
                thread1 = threading.Thread(target = self.fn_sendcmd, args=(a,) )
                thread1.start()
                thread1.join()
                self.updatelabeltextO(self.flow_value)
            timer = threading.Timer(2.0, self.second_part, args=(str,))
            timer.start()
 
    def second_part(self, str):
        a = '010300040002'
        thread1 = threading.Thread(target = self.fn_sendcmd, args=(a,) )
        thread1.start()
        thread1.join()
        self.updatelabeltextAr(self.flow_value)
        self.start_readout()

    def updatelabeltextAr(self, number):
        number = str(round(number/1.45, 2))
        self.label_realflowAr.setText(number)

    def updatelabeltextO(self, number):
        number = str(round(number, 2))
        self.label_realflowO.setText(number)

    def fn_sendcmd(self, number):                          # передаем в эту функцию команду, которую она дальше разбивает на части         
        self.ed_id= number[0:2]                           # адрес устройства ID
        self.ed_cmd=number[2:4]                           # номер команды
        self.ed_adr=number[4:8]                           # адрес регистра
        self.ed_count=number[8:17]                          # данные
        global send_arr
        self.send_arr=[]                                        # разбивка на байты отправляемого массива (по смыслу)
        self.id_=self.get_bt(self.ed_id)
        self.cmd=self.get_bt(self.ed_cmd)
        self.adrh, self.adrl=self.get_highlow(self.ed_adr)
        self.send_arr.append(hex(self.id_))
        self.send_arr.append(hex(self.cmd))
        self.send_arr.append(hex(self.adrh))
        self.send_arr.append(hex(self.adrl))
        cmd_num=int(self.ed_cmd,16)                             # обработка разных по типу кадров (в зависимости от команды)
        if cmd_num==3:                                          # чтение
            self.counth, self.countl=self.get_highlow(self.ed_count)
            self.send_arr.append(hex(self.counth))
            self.send_arr.append(hex(self.countl))
        elif cmd_num==6:                                        # запись одного регистра
            self.counth, self.countl=self.get_highlow(self.ed_count)
            self.send_arr.append(hex(self.counth))
            self.send_arr.append(hex(self.countl))
        elif cmd_num==15:                                       # групповая запись
            self.count_1=self.ed_count[:4]                      # вычленяем количество флагов
            self.count_2=self.ed_count[4:]                      # ввычленяем количество байт и данные
            if (len(self.count_2)<4):
                print("Ошибка в количестве данных")
                cmd_num=0
            else:
                self.counth, self.countl=self.get_highlow(self.count_1)
                self.send_arr.append(hex(self.counth))              # присоединяем 2 байта (1 и 2 половина количества флагов)
                self.send_arr.append(hex(self.countl))
                self.bytes=int(self.count_2[:2],16)                 # вычленяем количество байт и переводим в 10 сс
                self.count_2=self.count_2[2:]                       # вычленяем данные
                self.send_arr.append(hex(self.bytes))               # присоединяем 1 байт (количество байтов)
                i=0
                while i<self.bytes:                                 # вычленяем данные по 1 байту и записываем
                    self.data=int(self.count_2[:2],16)
                    self.count_2=self.count_2[2:]
                    i=i+1
                    self.send_arr.append(hex(self.data))
        else:
            print("Такой команды нет")

        if (cmd_num==3 or cmd_num==6 or cmd_num==15):               # Если команда существует
            self.addcrc(self.send_arr)                              # расчитаем CRC
            low,high=self.addcrc(self.send_arr)
            self.send_arr.append(low)                               # добавляем CRC
            self.send_arr.append(high)
            self.result=bytes([int(x,16) for x in self.send_arr])   # переводим массив строк hex в байты (представляет некоторые байты символом ASCII это норма)
            s.write(self.result)                                    # отправлем собранный пакет
            self.ls_in=s.read(256)                                  # читаем собранный пакет
            self.ls_in=str("".join("\\x{:02x}".format(c) for c in self.ls_in)) # преобразование в нормальный формат
            result_hex_list=[]
            if len(self.ls_in)<1:                                    # проверка есть ли ответ
                print("РРГ не отвечает")
            else:
                address=self.ls_in[2:4]                             # узнаём адрес устройства
                result_hex_list.append(address)
                command=self.ls_in[6:8]                             # узнаём номер команды
                result_hex_list.append(command)
                if command=="03":                                   # в зависимости от номера команды вычленяем остальные данные
                    # чтение из нескольких регистров
                    kol_bytes=self.ls_in[10:12]
                    result_hex_list.append(kol_bytes)
                    for i in range(int(kol_bytes, 16)):
                        data=self.ls_in[14+4*i:16+4*i]
                        result_hex_list.append(data)
                    crc1=self.ls_in[18+4*i:20+4*i]
                    crc2=self.ls_in[22+4*i:24+4*i]
                    result_hex_list.append(crc1)
                    result_hex_list.append(crc2)
                else:
                    if command=="06":
                        # запись значения в один регистр
                        adress_reg1=self.ls_in[10:12]
                        result_hex_list.append(adress_reg1)
                        adress_reg2=self.ls_in[14:16]
                        result_hex_list.append(adress_reg2)
                        data1=self.ls_in[18:20]
                        result_hex_list.append(data1)
                        data2=self.ls_in[22:24]
                        result_hex_list.append(data2)
                        crc1=self.ls_in[26:28]
                        result_hex_list.append(crc1)
                        crc2=self.ls_in[30:32]
                        result_hex_list.append(crc2)
                    else:
                        if command=="0f":
                            # запись значений в несколько регистров флагов
                            adress_reg1=self.ls_in[10:12]
                            result_hex_list.append(adress_reg1)
                            adress_reg2=self.ls_in[14:16]
                            result_hex_list.append(adress_reg2)
                            kol_f1=self.ls_in[18:20]
                            result_hex_list.append(kol_f1)
                            kol_f2=self.ls_in[22:24]
                            result_hex_list.append(kol_f2)
                            crc1=self.ls_in[26:28]
                            result_hex_list.append(crc1)
                            crc2=self.ls_in[30:32]
                            result_hex_list.append(crc2)
                        else:
                            # ошибка
                            error_num=self.ls_in[10:12]
                            result_hex_list.append(error_num)
                            crc1=self.ls_in[14:16]
                            result_hex_list.append(crc1)
                            crc2=self.ls_in[18:20]
                            result_hex_list.append(crc2)
                result_hex_list_str=self.print_list2(result_hex_list)
                result_hex_list_str='0x' + result_hex_list_str[20:22] + result_hex_list_str[24:26]
                result_hex_list_int = float.fromhex(result_hex_list_str)/100*90/100
                if result_hex_list_int > 190:
                    self.flow_value = 0
                else:
                    self.flow_value = result_hex_list_int
                #self.TE_1.append(result_hex_list_str)               # выводим полученный пакет на экран
                crc2_=result_hex_list.pop(len(result_hex_list)-1)   # удаляем и запоминаем старое CRC
                crc1_=result_hex_list.pop(len(result_hex_list)-1)
                crc1_new,crc2_new=self.addcrc(result_hex_list)      # считаем новое CRC для полученного сообщения
                if (int(crc1,16)==int(crc1_new,16))&(int(crc2,16)==int(crc2_new,16)): # сравниваем CRC
                    #self.TE_1.append("Правильная контрольная сумма")
                    nsb = 1
                else:
                    #self.TE_1.append("Ошибочная контрольная сумма")
                    print("Ошибочная контрольная сумма")

    def Exit_(self):                                         # при выходе из программы
        print('Активирован выход')
        self.ExitWindow = ExitWindow(self)
        self.ExitWindow.show()
        #self.ExitWindow.exec()
        global current_command
        current_command = 'Exit'                                       

    def get_bt(self, tmps):                                     # извлекаем число из поля txt
        bt=int(tmps[-2:],16)
        return bt

    def get_highlow(self,tmps):                                 # разбиваем строку на 2 байта
        tmpl=int(tmps[-2:],16)
        tmph=int(tmps[-4:-2],16)
        return tmph, tmpl

    def print_list(self, ls):
        str_result=""                                           # формируем строчку для вывода на экран (запрос)
        for ch in ls:
            if len(ch[2:])==1:
                str_result=str_result+"0"+ch[2:]+"  "
            else:
                str_result=str_result+ch[2:]+"  "
        return (str_result)

    def print_list2(self, ls):
        str_result=""                                           # формируем строчку для вывода на экран (ответ)
        for ch in ls:
            str_result=str_result+"  "+ch
        return (str_result[2:])

    def crc16bt(self, data):
        i_CRC_High=hex(0xFF)
        i_CRC_Low=hex(0xFF)
        index=hex(0x0000)
        for bt in data:
            index=(int(i_CRC_Low,16) ^ int(bt,16))              # index - в 10 сс
            i_CRC_Low=hex(int(i_CRC_High,16) ^ int(hex(CRC_High[index]),16))
            i_CRC_High=hex(int(hex(CRC_Low[index]),16))
        return (hex((int(i_CRC_High,16)<<8) | int(i_CRC_Low,16)))

    def addcrc(self, ls):                                       # вычисляет байты CRC и добавляет в конец list
        self.crc=self.crc16bt(ls)
        self.crc_low=hex(int(self.crc,16) & int(hex(0xFF),16))
        self.crc_high=hex((int(self.crc,16)>>8) & int(hex(0xFF),16))
        return self.crc_low, self.crc_high
    
    def click_openO(self):
        global current_command  
        current_command = "020F000200020101"

    def click_openAr(self):
        global current_command  
        current_command = "010F000200020101"
        
    def click_closeO(self):
        global current_command  
        current_command = "020F000200020102"

    def click_closeAr(self):
        global current_command  
        current_command = "010F000200020102"
        
    def click_regulateO(self):
        global current_command  
        current_command = "020F000200020100"
        
    def click_regulateAr(self):
        global current_command  
        current_command = "010F000200020100"
        
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
        value_flow_1 = self.fakeLineEditO_2.text() #значение из TextEdit в строку
        try:
            value_flow_1 = float(value_flow_1)
            procent = int((value_flow_1/90)*10000*1.45)
            procent1 = hex(procent)
            if value_flow_1 > 90:
                self.show_error("Значение должно быть не больше 90 л/с")
            else:
                procent1=str(procent1)
                if len(procent1) < 6:
                    procent2 = "0" + procent1[2:6]
                else:
                    procent2 = procent1[2:6]
                type_command = "01060004" + procent2
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