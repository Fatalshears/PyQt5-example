# UDN1HC
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QTabWidget, QHBoxLayout, QGridLayout, QGroupBox, QVBoxLayout, QWidget, QLabel, QLineEdit, QDialogButtonBox, QMessageBox, QPushButton, QFileDialog, QTextEdit, QListWidget, QAbstractItemView, QComboBox
import sys
import os
import socket
from PyQt5 import QtCore
from PyQt5.QtCore import QThread
import CEF
import FlaS
import DTC
import fm
import configparser
from pythonping import ping
import re
import subprocess
import CLARA_ConfigCANape


global_string_1 = ''
global_string_2 = ''
global_string_3 = ''


def set_global_str(p_string, id):
    global global_string_1
    global global_string_2
    global global_string_3
    if id == 1:
        global_string_1 = p_string
    elif id == 2:
        global_string_2 = p_string
    elif id ==3:
        global_string_3 = p_string


def ret_global_str():
    return global_string_1, global_string_2, global_string_3


class FileEdit(QLineEdit):
    def __init__(self):
        super(FileEdit, self).__init__()
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            filepath = str(urls[0].path())[1:]
            # any file type here
            if filepath:
                self.setText(filepath)
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle("Error: Invalid File")
                dialog.setText("Cannot execute Drag and Drop")
                dialog.setIcon(QMessageBox.Warning)
                dialog.exec_()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "CLARA Tool"
        self.top = 300
        self.left = 100
        self.width = 1024
        self.height = 800

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QtGui.QIcon(r'icon\settings-1.png'))

        self.tab_widget = QTabWidget()

        self.tab_widget.setFont(QtGui.QFont('Calibri', 12))
        self.tab_widget.addTab(FlashSoftware(), 'Flash Software')
        self.tab_widget.addTab(TabPower(), 'Power')
        self.tab_widget.addTab(TabCompilerError(), 'Simulation Fix')
        self.tab_widget.addTab(TabDTC(), 'FM Preparation')



        self.setCentralWidget(self.tab_widget)

        self.tab_widget.currentChanged.connect(self.update_dtc_path)

        self.show()

    def update_dtc_path(self):
        # print (self.tab_widget.currentIndex())
        if self.tab_widget.currentIndex() == 3:
            # self.tab_widget.currentWidget().text_box.setText(ret_global_str())
            self.tab_widget.currentWidget().update_text_box_str(ret_global_str())


class TabPower(QWidget):
    def __init__(self):
        super().__init__()

        self.group_box_ip = QGroupBox('IP address')
        self.group_box_ip.setFont(QtGui.QFont('Calibri', 12))
        self.text_box_ip = QLineEdit()
        self.text_box_ip.setText('192.168.3.2')

        gb_ip_layout = QVBoxLayout()
        gb_ip_layout.addWidget(self.text_box_ip)

        self.group_box_ip.setLayout(gb_ip_layout)

        self.group_box_port = QGroupBox('Port')
        self.group_box_port.setFont(QtGui.QFont('Calibri', 12))
        self.text_box_port = QLineEdit()
        self.text_box_port.setText('5025')

        gb_port_layout = QVBoxLayout()
        gb_port_layout.addWidget(self.text_box_port)

        self.group_box_port.setLayout(gb_port_layout)

        self.group_box_vol = QGroupBox('Voltage')
        self.group_box_vol.setFont(QtGui.QFont('Calibri', 12))
        self.text_box_vol = QLineEdit()
        self.text_box_vol.setText('13')

        gb_vol_layout = QVBoxLayout()
        gb_vol_layout.addWidget(self.text_box_vol)

        self.group_box_vol.setLayout(gb_vol_layout)

        self.group_box_current = QGroupBox('Current')
        self.group_box_current.setFont(QtGui.QFont('Calibri', 12))
        self.text_box_current = QLineEdit()
        self.text_box_current.setText('1')

        gb_current_layout = QVBoxLayout()
        gb_current_layout.addWidget(self.text_box_current)

        self.group_box_current.setLayout(gb_current_layout)

        self.group_box = QGroupBox('')
        self.group_box.setFont(QtGui.QFont('Calibri', 12))

        self.set_btn = QPushButton('SET')
        self.set_btn.clicked.connect(self.set_vol_cur)

        self.get_btn = QPushButton('GET')
        self.get_btn.clicked.connect(self.get_vol_cur)

        self.on_btn = QPushButton('ON')
        self.on_btn.clicked.connect(self.on_vol_cur)

        self.off_btn = QPushButton('OFF')
        self.off_btn.clicked.connect(self.off_vol_cur)
        self.power_log = QTextEdit()

        gb_m_layout = QGridLayout()
        gb_m_layout.addWidget(self.set_btn, 0, 0)
        gb_m_layout.addWidget(self.get_btn, 0, 1)
        gb_m_layout.addWidget(self.on_btn, 1, 0)
        gb_m_layout.addWidget(self.off_btn, 1, 1)
        gb_m_layout.addWidget(self.power_log, 2, 0, 2, 2)

        self.group_box.setLayout(gb_m_layout)

        gb_main_layout = QGridLayout()
        gb_main_layout.addWidget(self.group_box_ip, 0,0)
        gb_main_layout.addWidget(self.group_box_port, 0, 1)
        gb_main_layout.addWidget(self.group_box_vol, 1, 0)
        gb_main_layout.addWidget(self.group_box_current, 1, 1)
        gb_main_layout.addWidget(self.group_box, 2, 0, 2, 2)

        self.setLayout(gb_main_layout)

    def set_vol_cur(self):
        self.set_btn.setEnabled(False)
        self.get_btn.setEnabled(False)
        self.on_btn.setEnabled(False)
        self.off_btn.setEnabled(False)

        log = ''
        server_address = (self.text_box_ip.text(), int(self.text_box_port.text()))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(server_address)
            log = f'connecting to {server_address[0]} port {str(server_address[1])}\n'
            message = "VOLTage " + self.text_box_vol.text() + "\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'

            message = "CURRent " + self.text_box_current.text() + "\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'

            message = "VOLTage?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Voltage is set to " + data.strip() + "\n"
            self.text_box_vol.setText(data.strip())

            message = "CURRent?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Current is set to " + data.strip() + "\n"
            self.text_box_current.setText(data.strip())

            sock.close()
            log = log + "Connection closed" + "\n"

        except Exception as e:
            log = log + "==========ERROR==========" + "\n"
            log = log + str(e) + "\n"
            self.text_box_vol.setText("error")
            self.text_box_current.setText("error")

        self.power_log.setText(log)
        self.set_btn.setEnabled(True)
        self.get_btn.setEnabled(True)
        self.on_btn.setEnabled(True)
        self.off_btn.setEnabled(True)

    def get_vol_cur(self):
        self.set_btn.setEnabled(False)
        self.get_btn.setEnabled(False)
        self.on_btn.setEnabled(False)
        self.off_btn.setEnabled(False)

        log = ''
        server_address = (self.text_box_ip.text(), int(self.text_box_port.text()))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(server_address)
            log = f'connecting to {server_address[0]} port {str(server_address[1])}\n'

            message = "VOLTage?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Voltage is set to " + data.strip() + "\n"
            self.text_box_vol.setText(data.strip())

            message = "CURRent?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Current is set to " + data.strip() + "\n"
            self.text_box_current.setText(data.strip())

            sock.close()
            log = log + "Connection closed" + "\n"

        except Exception as e:
            log = log + "==========ERROR==========" + "\n"
            log = log + str(e) + "\n"
            self.text_box_vol.setText("error")
            self.text_box_current.setText("error")

        self.power_log.setText(log)
        self.set_btn.setEnabled(True)
        self.get_btn.setEnabled(True)
        self.on_btn.setEnabled(True)
        self.off_btn.setEnabled(True)

    def on_vol_cur(self):
        self.set_btn.setEnabled(False)
        self.get_btn.setEnabled(False)
        self.on_btn.setEnabled(False)
        self.off_btn.setEnabled(False)

        log = ''
        server_address = (self.text_box_ip.text(), int(self.text_box_port.text()))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(server_address)
            log = f'connecting to {server_address[0]} port {str(server_address[1])}\n'
            message = "OUTPut ON\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'

            message = "VOLTage?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Voltage is set to " + data.strip() + "\n"
            self.text_box_vol.setText(data.strip())

            message = "CURRent?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Current is set to " + data.strip() + "\n"
            self.text_box_current.setText(data.strip())

            sock.close()
            log = log + "Connection closed" + "\n"

        except Exception as e:
            log = log + "==========ERROR==========" + "\n"
            log = log + str(e) + "\n"
            self.text_box_vol.setText("error")
            self.text_box_current.setText("error")

        self.power_log.setText(log)
        self.set_btn.setEnabled(True)
        self.get_btn.setEnabled(True)
        self.on_btn.setEnabled(True)
        self.off_btn.setEnabled(True)

    def off_vol_cur(self):
        self.set_btn.setEnabled(False)
        self.get_btn.setEnabled(False)
        self.on_btn.setEnabled(False)
        self.off_btn.setEnabled(False)

        log = ''
        server_address = (self.text_box_ip.text(), int(self.text_box_port.text()))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(server_address)
            log = f'connecting to {server_address[0]} port {str(server_address[1])}\n'
            message = "OUTPut OFF\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'

            message = "VOLTage?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Voltage is set to " + data.strip() + "\n"
            self.text_box_vol.setText(data.strip())

            message = "CURRent?\n"
            b_message = message.encode('ascii')
            sock.sendall(b_message)
            log = log + f'sending {message}'
            data = sock.recv(16)
            data = bytes.decode(data)
            log = log + "Current is set to " + data.strip() + "\n"
            self.text_box_current.setText(data.strip())

            sock.close()
            log = log + "Connection closed" + "\n"

        except Exception as e:
            log = log + "==========ERROR==========" + "\n"
            log = log + str(e) + "\n"
            self.text_box_vol.setText("error")
            self.text_box_current.setText("error")

        self.power_log.setText(log)
        self.set_btn.setEnabled(True)
        self.get_btn.setEnabled(True)
        self.on_btn.setEnabled(True)
        self.off_btn.setEnabled(True)


class TabDTCThread(QThread):

    def __init__(self, system_degradation_path, sheet_name, FCO_first_cell, fault_cell, csv_path, requirement_path, dbc_path, dtc_path, eventID_PF28, video_keyword):
        QThread.__init__(self)
        self.system_degradation_path = system_degradation_path
        self.sheet_name = sheet_name
        self.FCO_first_cell = FCO_first_cell
        self.fault_cell = fault_cell
        self.csv_path = csv_path
        self.template_path = 'data/Template.py'
        self.requirement_path = requirement_path
        self.dbc_path = dbc_path
        self.dtc_path = dtc_path
        self.eventID_PF28 = eventID_PF28
        self.video_keyword = video_keyword

    def __del__(self):
        self.wait()

    def run(self):
        fm.TestCaseFM.Main(fm.TestCaseFM, self.csv_path, self.system_degradation_path, self.template_path, self.requirement_path, self.FCO_first_cell,
                            self.fault_cell, self.dbc_path, self.sheet_name, self.dtc_path, self.eventID_PF28, self.video_keyword)
        return


class TabDTC(QWidget):
    def __init__(self):
        super().__init__()

        self.group_box = QGroupBox('')
        self.group_box.setFont(QtGui.QFont('Calibri', 12))

        self.text_box = FileEdit()
        self.text_box.setPlaceholderText('Drop 03_EventId_DTC_Mapping_Dem_Cfg_DtcId.h file here')

        self.brow_button = QPushButton('Browse')
        self.brow_button.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button.setIconSize(QtCore.QSize(15, 15))
        self.brow_button.clicked.connect(self.browse_file)

        self.generate_DTC_only = QPushButton('Generate')
        self.generate_DTC_only.setIcon(QtGui.QIcon(r'icon\generate.png'))
        self.generate_DTC_only.setIconSize(QtCore.QSize(15, 15))
        self.generate_DTC_only.clicked.connect(self.generate_dtc)

        self.text_box_SD = FileEdit()
        self.text_box_SD.setPlaceholderText('Drop System Degradation file here')

        self.brow_button_SD = QPushButton('Browse')
        self.brow_button_SD.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_SD.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_SD.clicked.connect(self.browse_file_SD)

        self.text_box_sheet_name = QLineEdit()
        self.text_box_sheet_name.setPlaceholderText('Sheet name')
        self.text_box_FCO_cell = QLineEdit()
        self.text_box_FCO_cell.setPlaceholderText('FCO first cell')
        # self.text_box_FCO_len = QLineEdit()
        # self.text_box_FCO_len.setPlaceholderText('FCO no. of cells')
        # self.text_box_FCS_cell = QLineEdit()
        # self.text_box_FCS_cell.setPlaceholderText('FCS first cell')
        # self.text_box_FCS_len = QLineEdit()
        # self.text_box_FCS_len.setPlaceholderText('FCS no. of cells')
        self.text_box_fault_cell = QLineEdit()
        self.text_box_fault_cell.setPlaceholderText('Fault cell')

        self.text_box_video_keyword = QLineEdit('AWV_VRUWARNINGFUNCTION_OFF')
        self.text_box_video_keyword.setPlaceholderText('Video keyword')

        self.text_eventID_PF28 = ''

        horibox = QHBoxLayout()
        horibox.addWidget(self.text_box_sheet_name)
        horibox.addWidget(self.text_box_FCO_cell)
        # horibox.addWidget(self.text_box_FCO_len)
        # horibox.addWidget(self.text_box_FCS_cell)
        # horibox.addWidget(self.text_box_FCS_len)
        horibox.addWidget(self.text_box_fault_cell)
        horibox.addWidget(self.text_box_video_keyword)

        self.minor_group_box = QGroupBox('')
        self.minor_group_box.setFont(QtGui.QFont('Calibri', 12))
        self.minor_group_box.setLayout(horibox)

        self.text_box_csv = FileEdit()
        self.text_box_csv.setPlaceholderText('Drop csv file here')
        self.brow_button_csv = QPushButton('Browse')
        self.brow_button_csv.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_csv.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_csv.clicked.connect(self.browse_file_csv)

        self.text_box_requirement = FileEdit()
        self.text_box_requirement.setPlaceholderText('Drop requirement file here')
        self.brow_button_requirement = QPushButton('Browse')
        self.brow_button_requirement.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_requirement.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_requirement.clicked.connect(self.browse_file_req)

        self.text_box_dbc = FileEdit()
        self.text_box_dbc.setPlaceholderText('Drop public dbc file here')
        self.brow_button_dbc = QPushButton('Browse')
        self.brow_button_dbc.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_dbc.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_dbc.clicked.connect(self.browse_file_dbc)



        self.run_button = QPushButton('Run')
        self.run_button.setIcon(QtGui.QIcon(r'icon\play-button.png'))
        self.run_button.setIconSize(QtCore.QSize(15, 15))
        self.run_button.clicked.connect(self.run_DTC)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.text_box, 0, 0)
        grid_layout.addWidget(self.generate_DTC_only, 0, 1)
        grid_layout.addWidget(self.text_box_SD, 1, 0)
        grid_layout.addWidget(self.brow_button_SD, 1, 1)
        grid_layout.addWidget(self.minor_group_box, 2, 0, 1, 2)
        grid_layout.addWidget(self.text_box_csv, 3, 0)
        grid_layout.addWidget(self.brow_button_csv, 3, 1)
        grid_layout.addWidget(self.text_box_requirement, 4, 0)
        grid_layout.addWidget(self.brow_button_requirement, 4, 1)
        grid_layout.addWidget(self.text_box_dbc, 5, 0)
        grid_layout.addWidget(self.brow_button_dbc, 5, 1)


        self.group_box.setLayout(grid_layout)

        hbox = QHBoxLayout()
        hbox.addWidget(self.group_box)
        hbox.addWidget(self.run_button)

        self.setLayout(hbox)

    def generate_dtc(self):
        if os.path.isfile(self.text_box.text()):
            try:
                DTC.generate_DTC_py(self.text_box.text())
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()

            try:
                os.startfile('output\\_prj_para')
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Invalid input file for generating DTC')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()


    def browse_file(self):
        file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
                                            'Excel Workbook (*xlsx);;Excel 97-2003 Workbook (*xls)')
        file_path = file_object[0]
        if file_path != '':
            self.text_box.setText(file_path)

    def browse_file_SD(self):
        file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
                                            'Excel Workbook (*xlsx);;Excel 97-2003 Workbook (*xls)')
        file_path = file_object[0]
        if file_path != '':
            self.text_box_SD.setText(file_path)

    def browse_file_csv(self):
        file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
                                            'Excel Workbook (*csv);;Excel 97-2003 Workbook (*csv)')
        file_path = file_object[0]
        if file_path != '':
            self.text_box_csv.setText(file_path)

    def browse_file_req(self):
        file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
                                            'Excel Workbook (*xlsx);;Excel 97-2003 Workbook (*xls)')
        file_path = file_object[0]
        if file_path != '':
            self.text_box_requirement.setText(file_path)

    def browse_file_dbc(self):
        file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
                                            'Public Database (*dbc)')
        file_path = file_object[0]
        if file_path != '':
            self.text_box_dbc.setText(file_path)

    def update_text_box_str(self, p_str):
        self.text_eventID_PF28 = p_str[2]
        if not os.path.isfile(self.text_box.text()):
            self.text_box.setText(p_str[0])
        if not os.path.isfile(self.text_box_csv.text()):
            self.text_box_csv.setText(p_str[1])

    def run_DTC(self):
        if os.path.isfile(self.text_box_SD.text()):
            if self.text_box_sheet_name.text() and not self.text_box_sheet_name.text().isspace():
                pattern = '[\$]?([aA-zZ]+)[\$]?(\d+)' #excel reference format
                result = re.match(pattern, self.text_box_FCO_cell.text())
                if result:
                    result = re.match(pattern, self.text_box_fault_cell.text())
                    if result:
                        if os.path.isfile(self.text_box_csv.text()):
                            if os.path.isfile(self.text_box_requirement.text()):
                                if os.path.isfile(self.text_box_dbc.text()):
                                    if os.path.isfile(self.text_box.text()):
                                        self.text_eventID_PF28 = self.text_box.text()
                                        self.get_thread = TabDTCThread(self.text_box_SD.text(), self.text_box_sheet_name.text(), self.text_box_FCO_cell.text(),
                                                                 self.text_box_fault_cell.text(), self.text_box_csv.text(), self.text_box_requirement.text(),
                                                                 self.text_box_dbc.text(), self.text_box.text(), self.text_eventID_PF28, self.text_box_video_keyword.text())
                                        self.get_thread.finished.connect(self.done)
                                        self.get_thread.start()
                                        self.run_button.setEnabled(False)
                                    else:
                                        dialog = QMessageBox()
                                        dialog.setWindowTitle('Error')
                                        dialog.setText('File used for generating DTC is invalid')
                                        dialog.setIcon(QMessageBox.Critical)
                                        dialog.exec_()
                                else:
                                    dialog = QMessageBox()
                                    dialog.setWindowTitle('Error')
                                    dialog.setText('Invalid dbc')
                                    dialog.setIcon(QMessageBox.Critical)
                                    dialog.exec_()
                            else:
                                dialog = QMessageBox()
                                dialog.setWindowTitle('Error')
                                dialog.setText('Invalid requirement file')
                                dialog.setIcon(QMessageBox.Critical)
                                dialog.exec_()
                        else:
                            dialog = QMessageBox()
                            dialog.setWindowTitle('Error')
                            dialog.setText('Invalid csv file')
                            dialog.setIcon(QMessageBox.Critical)
                            dialog.exec_()
                    else:
                        dialog = QMessageBox()
                        dialog.setWindowTitle('Error')
                        dialog.setText('Invalid fault cell name')
                        dialog.setIcon(QMessageBox.Critical)
                        dialog.exec_()
                else:
                    dialog = QMessageBox()
                    dialog.setWindowTitle('Error')
                    dialog.setText('Invalid FCO cell name')
                    dialog.setIcon(QMessageBox.Critical)
                    dialog.exec_()
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText('Invalid sheet name')
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Invalid System Degradation file')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def done(self):
        self.run_button.setEnabled(True)
        os.startfile('output')
        # dialog = QMessageBox()
        # dialog.setWindowTitle("Finished without errors")
        # dialog.setText("Successfully")
        # dialog.setIcon(QMessageBox.Information)
        # dialog.exec_()





class TabCompilerErrorThread(QThread):

    def __init__(self, directory, file_name):
        QThread.__init__(self)
        self.directory = directory
        self.file_name = file_name

    def __del__(self):
        self.wait()

    def run(self):
        CEF.run_compiler_error_fix(self.directory, self.file_name)


class TabCompilerErrorThread1(QThread):

    def __init__(self, signal_name, type, directory):
        QThread.__init__(self)
        self.directory = directory
        self.signal_name = signal_name
        self.type = type

    def __del__(self):
        self.wait()

    def run(self):
        CEF.run_signal_measure_calib(self.signal_name, self.type, self.directory)


class TabCompilerError(QWidget):
    def __init__(self):
        super().__init__()

        self.group_box = QGroupBox('Clarahil Build Fix')
        self.group_box.setFont(QtGui.QFont('Calibri', 12))

        self.text_box_dir = FileEdit()
        self.text_box_dir.setPlaceholderText('Drop simulation folder here')
        # self.text_box_error_log = FileEdit('Path of error log file (.txt)')
        self.text_edit_error_log = QTextEdit()
        self.text_edit_error_log.setFont(QtGui.QFont('Calibri', 12))
        self.text_edit_error_log.setPlaceholderText('Paste content of compiler error log here')
        self.text_edit_error_log.textChanged.connect(self.save_text_edit)

        self.brow_button_d = QPushButton('Browse')
        self.brow_button_d.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_d.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_d.clicked.connect(self.browse_path)

        # self.brow_button_e = QPushButton('Browse')
        # self.brow_button_e.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        # self.brow_button_e.setIconSize(QtCore.QSize(15, 15))
        # self.brow_button_e.clicked.connect(self.browse_file)

        self.run_button = QPushButton('Run')
        self.run_button.setIcon(QtGui.QIcon(r'icon\play-button.png'))
        self.run_button.setIconSize(QtCore.QSize(15, 15))
        self.run_button.clicked.connect(self.run_error_fix)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.text_box_dir, 0, 0)
        grid_layout.addWidget(self.brow_button_d, 0, 1)
        grid_layout.addWidget(self.text_edit_error_log, 1, 0, 1, 1)
        grid_layout.addWidget(self.run_button, 1, 1, 1, 1)
        # grid_layout.addWidget(self.text_box_error_log, 1, 0)
        # grid_layout.addWidget(self.brow_button_e, 1, 1)
        self.group_box.setLayout(grid_layout)

        self.group_box_1 = QGroupBox('Add Measurement/ Calibration')
        self.group_box_1.setFont(QtGui.QFont('Calibri', 12))

        self.text_measurement_name = QLineEdit()
        self.text_measurement_name.setFont(QtGui.QFont('Calibri', 12))
        self.text_measurement_name.setPlaceholderText('Measured Signal')

        self.combo_box_signal_cycle = QComboBox()
        self.combo_box_signal_cycle.addItem('mT20')
        self.combo_box_signal_cycle.addItem('mTC')
        self.combo_box_signal_cycle.addItem('mT10')


        self.add_measure_button = QPushButton('Add Measurement')
        self.add_measure_button.setIcon(QtGui.QIcon(r'icon\play-button.png'))
        self.add_measure_button.setIconSize(QtCore.QSize(15, 15))
        self.add_measure_button.clicked.connect(self.run_add_measure)

        self.text_calib_name = QLineEdit()
        self.text_calib_name.setFont(QtGui.QFont('Calibri', 12))
        self.text_calib_name.setPlaceholderText('Calibrated Signal')

        self.add_calib_button = QPushButton('Add Calibration')
        self.add_calib_button.setIcon(QtGui.QIcon(r'icon\play-button.png'))
        self.add_calib_button.setIconSize(QtCore.QSize(15, 15))
        self.add_calib_button.clicked.connect(self.run_add_calib)

        grid_layout_1 = QGridLayout()
        grid_layout_1.addWidget(self.text_measurement_name, 0, 0)
        grid_layout_1.addWidget(self.combo_box_signal_cycle, 0, 1)
        grid_layout_1.addWidget(self.add_measure_button, 0, 2)
        grid_layout_1.addWidget(self.text_calib_name, 1, 0, 1, 2)
        grid_layout_1.addWidget(self.add_calib_button, 1, 2)

        grid_layout_1.setColumnStretch(0, 5)
        grid_layout_1.setColumnStretch(1, 1)
        grid_layout_1.setColumnStretch(2, 1)

        self.group_box_1.setLayout(grid_layout_1)

        vbox = QVBoxLayout()
        vbox.addWidget(self.group_box)
        vbox.addWidget(self.group_box_1)
        self.setLayout(vbox)

    # def browse_file(self):
    #     file_object = QFileDialog.getOpenFileName(self, 'Open File', 'c://',
    #                                         'Text Files (*txt)')
    #     file_path = file_object[0]
    #     if file_path is not '':
    #         self.text_box_error_log.setText(file_path)

    def browse_path(self):
        file_object = QFileDialog.getExistingDirectory(self, "Select Directory")
        if file_object != '':
            self.text_box_dir.setText(str(file_object))

    def save_text_edit(self):
        output_file = open('Error_Log.txt', 'w')
        output_file.write(self.text_edit_error_log.toPlainText())
        output_file.close()

    def run_error_fix(self):
        if os.path.isdir(self.text_box_dir.text()) and os.path.isfile('Error_Log.txt'):
            self.get_thread = TabCompilerErrorThread(self.text_box_dir.text(), 'Error_Log.txt')
            self.get_thread.finished.connect(self.done)
            self.get_thread.start()
            self.run_button.setEnabled(False)

    def run_add_measure(self):
        if os.path.isdir(self.text_box_dir.text()) and self.text_measurement_name.text() != '':
            self.get_thread = TabCompilerErrorThread1(self.text_measurement_name.text(),self.combo_box_signal_cycle.currentText(),self.text_box_dir.text())
            self.get_thread.finished.connect(self.done)
            self.get_thread.start()
            self.add_measure_button.setEnabled(False)
            self.add_calib_button.setEnabled(False)
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Missing path to simulation folder or signal name is blank')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def run_add_calib(self):
        if os.path.isdir(self.text_box_dir.text()) and self.text_calib_name.text() != '':
            self.get_thread = TabCompilerErrorThread1(self.text_calib_name.text(),'calib',self.text_box_dir.text())
            self.get_thread.finished.connect(self.done)
            self.get_thread.start()
            self.add_measure_button.setEnabled(False)
            self.add_calib_button.setEnabled(False)
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Missing path to simulation folder or signal name is blank')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def done(self):
        self.run_button.setEnabled(True)
        self.add_calib_button.setEnabled(True)
        self.add_measure_button.setEnabled(True)
        dialog = QMessageBox()
        dialog.setWindowTitle("Finished without errors")
        dialog.setText("Successfully")
        dialog.setIcon(QMessageBox.Information)
        dialog.exec_()


class FlashSoftwareThread(QThread):

    def __init__(self, list_flashable_items, path_to_flash_all, path_to_canape, radar_type):
        QThread.__init__(self)
        self.list_flashable_items = list_flashable_items
        self.path_to_flash_all = path_to_flash_all
        self.path_to_canape = path_to_canape
        self.radar_type = radar_type
        self.cmd_success = False

    def __del__(self):
        self.wait()

    def run(self):
        self.cmd_success = FlaS.flash_software(self.list_flashable_items, self.path_to_flash_all, self.path_to_canape, self.radar_type)


class PingIpAddressThread(QThread):

    def __init__(self, ip_address, ini_location, radar_type):
        QThread.__init__(self)
        self.ip_address = ip_address
        self.ini_location = ini_location
        self.radar_type = radar_type
        self.response_message = ''
        self.response_type = ''
        self.is_response_ok = False

    def __del__(self):
        self.wait()

    def run(self):
        try:
            response_text = ping(self.ip_address, count=4)
            response_text_string = str(response_text)
        except Exception as e:
            response_text_string = str(e)
        is_updated = False
        is_detected = False
        if 'Reply' in response_text_string:
            try:
                fileObject = open(self.ini_location, "r")
                outObject = open(self.ini_location+'_fx', 'w')
                for line in fileObject:
                    store_line = line
                    if f'[Module_{self.radar_type}]' in line:
                        is_detected = True
                        outObject.write(store_line)
                        continue
                    if is_detected and 'HOST=' in line:
                        line = f'HOST={self.ip_address}\n'
                        store_line = line
                        is_detected = False
                    outObject.write(store_line)

                fileObject.close()
                outObject.close()
                # backup canape.ini
                backup = self.ini_location+'_bk'
                if os.path.isfile(backup):
                    os.remove(backup)
                os.rename(self.ini_location, backup)
                os.rename(self.ini_location+'_fx', self.ini_location)

                is_updated = True
            except Exception as e:
                self.response_message = f'Fail to update canape.ini: {e}'
                self.response_type = 'Error'
                self.is_response_ok = False

            if is_updated:
                self.response_message = 'IP Config Successfully' + '\\n' + response_text_string
                self.response_type = 'Ok'
                self.is_response_ok = True

        else:
            self.response_message = response_text_string
            self.response_type = 'Error'
            self.is_response_ok = False


class ClaraTEThread(QThread):

    def __init__(self, claratepath):
        QThread.__init__(self)
        self.claratepath = claratepath

    def __del__(self):
        self.wait()

    def run(self):

        my_cmd0 = self.claratepath[:self.claratepath.index(':') + 1]
        misc = '\\'
        my_cmd1 = f'cd "{self.claratepath[:self.claratepath.rfind(misc)]}"'
        subprocess.call([my_cmd0])
        subprocess.call([my_cmd1])
        subprocess.call([self.claratepath])

class ConfigCANAPEThread(QThread):

    def __init__(self, sw_path):
        QThread.__init__(self)
        self.sw_path = sw_path

    def __del__(self):
        self.wait()

    def run(self):
        CLARA_ConfigCANape.edit_config_canape(self.sw_path)



class FlashSoftware(QWidget):
    def __init__(self):
        super().__init__()
        self.group_box_1 = QGroupBox('Software Folder')
        self.group_box_1.setFont(QtGui.QFont('Calibri', 12))
        self.text_box_dir = FileEdit()
        self.text_box_dir.setPlaceholderText('Drop software folder here')

        self.brow_button_d = QPushButton('Browse')
        self.brow_button_d.setIcon(QtGui.QIcon(r'icon\folder-11.png'))
        self.brow_button_d.setIconSize(QtCore.QSize(15, 15))
        self.brow_button_d.clicked.connect(self.browse_path)

        h1_layout = QHBoxLayout()
        h1_layout.addWidget(self.text_box_dir)
        h1_layout.addWidget(self.brow_button_d)
        self.group_box_1.setLayout(h1_layout)

        # Find all .srec files
        self.group_box_2 = QGroupBox('Flashable Files')
        self.group_box_2.setFont(QtGui.QFont('Calibri', 12))

        self.no_file_found = 0
        self.no_file_selected = 0
        self.flashable_items_status = QLabel(f'{self.no_file_found} found, {self.no_file_selected} selected')
        self.flashable_items_status.setFont(QtGui.QFont("Calibri", 10))

        self.radar_type = 'N.A'
        self.flashable_radar_type = QLabel(f'Radar type: {self.radar_type}')
        self.flashable_radar_type.setFont(QtGui.QFont("Calibri", 10))

        self.flashable_items_list = []
        self.flashable_items_list_root_path = 'N.A'
        self.file_list_view = QListWidget()
        self.file_list_view.setAutoScroll(False)
        self.file_list_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list_view.itemSelectionChanged.connect(self.on_select_item_list_view)

        self.get_file_path_button = QPushButton('Get Files/ Paths')
        self.get_file_path_button.setIcon(QtGui.QIcon(r'icon\file-2.png'))
        self.get_file_path_button.setIconSize(QtCore.QSize(15, 15))
        self.get_file_path_button.clicked.connect(self.get_file_and_path)

        self.flash_button = QPushButton('Flash')
        self.flash_button.setIcon(QtGui.QIcon(r'icon\incoming.png'))
        self.flash_button.setIconSize(QtCore.QSize(15, 15))
        self.flash_button.clicked.connect(self.run_flash_software)

        grid2_layout = QGridLayout()
        grid2_layout.addWidget(self.file_list_view, 0, 0, 6, 1)
        grid2_layout.addWidget(self.get_file_path_button, 0, 1)
        grid2_layout.addWidget(self.flash_button, 1, 1)

        self.group_box_2s = QGroupBox('')
        self.group_box_2s.setLayout(grid2_layout)

        grid2s_layout = QGridLayout()
        grid2s_layout.addWidget(self.flashable_radar_type, 0, 0, 1, 2)
        grid2s_layout.addWidget(self.flashable_items_status, 1, 0, 1, 2)
        grid2s_layout.addWidget(self.group_box_2s, 2, 0, 10, 2)

        self.group_box_2.setLayout(grid2s_layout)

        # flash_all folder
        self.group_box_3 = QGroupBox('Misc.')
        self.text_box_flash_cna = FileEdit()
        self.text_box_flash_cna.setPlaceholderText('Path to flash.cna')

        self.text_box_ip_address = QLineEdit()
        self.text_box_ip_address.setPlaceholderText('IP address of RADAR sensor')

        self.ip_ping_cfg_button = QPushButton('IP Ping/ Config')
        self.ip_ping_cfg_button.setIcon(QtGui.QIcon(r'icon\wifi.png'))
        self.ip_ping_cfg_button.setIconSize(QtCore.QSize(15, 15))
        self.ip_ping_cfg_button.clicked.connect(self.ping_IP_address)

        self.ini_configParser = configparser.ConfigParser(allow_no_value=True)
        self.ini_configParser.optionxform = str
        fileObject = open(r'data\cfg.ini', "r")
        self.ini_configParser.read_file(fileObject)
        fileObject.close()




        self.text_box_canape = FileEdit()
        self.text_box_canape.setText(str(self.ini_configParser.get('PATH', 'CANAPE')))
        self.text_box_canape.setPlaceholderText('Path to canape.exe')

        self.canape_cfg_button = QPushButton('Config CANAPE')
        self.canape_cfg_button.setIcon(QtGui.QIcon(r'icon\compose.png'))
        self.canape_cfg_button.setIconSize(QtCore.QSize(15, 15))
        self.canape_cfg_button.clicked.connect(self.edit_configuration_canape)

        self.text_box_canalyzer = FileEdit()
        self.text_box_canalyzer.setText(str(self.ini_configParser.get('PATH', 'CANALYZER')))
        self.text_box_canalyzer.setPlaceholderText('Path to CANw64.exe')

        self.text_box_MRR1plus_cfg = QLineEdit()
        self.text_box_MRR1plus_cfg.setPlaceholderText('Path to MRR1plus.cfg ')
        self.MRR1plus_cfg_button = QPushButton('CANALYZER')
        self.MRR1plus_cfg_button.setIcon(QtGui.QIcon(r'icon\launch.png'))
        self.MRR1plus_cfg_button.setIconSize(QtCore.QSize(15, 15))
        self.MRR1plus_cfg_button.clicked.connect(self.launch_MRR1plus_cfg)

        self.text_box_MRR1plus_cna = QLineEdit()
        self.text_box_MRR1plus_cna.setPlaceholderText('Path to MRRxxx.cna ')
        self.MRR1plus_cna_button = QPushButton('CANAPE')
        self.MRR1plus_cna_button.setIcon(QtGui.QIcon(r'icon\launch.png'))
        self.MRR1plus_cna_button.setIconSize(QtCore.QSize(15, 15))
        self.MRR1plus_cna_button.clicked.connect(self.launch_MRR1plus_cna)

        self.text_box_DiaTester_cna = QLineEdit()
        self.text_box_DiaTester_cna.setPlaceholderText('Path to DiaTester.cna ')
        self.DiaTester_cna_button = QPushButton('DIATESTER')
        self.DiaTester_cna_button.setIcon(QtGui.QIcon(r'icon\launch.png'))
        self.DiaTester_cna_button.setIconSize(QtCore.QSize(15, 15))
        self.DiaTester_cna_button.clicked.connect(self.launch_DiaTester_cna)

        self.text_box_ClaraTE = FileEdit()
        self.text_box_ClaraTE.setText(str(self.ini_configParser.get('PATH', 'CLARA_TE')))
        self.text_box_ClaraTE.setPlaceholderText('Path to ClaraTE ')
        self.ClaraTE_button = QPushButton('ClaraTE')
        self.ClaraTE_button.setIcon(QtGui.QIcon(r'icon\launch.png'))
        self.ClaraTE_button.setIconSize(QtCore.QSize(15, 15))
        self.ClaraTE_button.clicked.connect(self.launch_ClaraTE)

        self.text_box_error_doc = FileEdit()
        self.text_box_error_doc.setPlaceholderText('Path to errordocu ')
        self.error_doc_button = QPushButton('errordocu')
        self.error_doc_button.setIcon(QtGui.QIcon(r'icon\folder-8.png'))
        self.error_doc_button.setIconSize(QtCore.QSize(15, 15))
        self.error_doc_button.clicked.connect(self.launch_errordoc)

        self.text_box_a2l = FileEdit()
        self.text_box_a2l.setPlaceholderText('Path to a2l ')
        self.a2l_button = QPushButton('a2l')
        self.a2l_button.setIcon(QtGui.QIcon(r'icon\folder-8.png'))
        self.a2l_button.setIconSize(QtCore.QSize(15, 15))
        self.a2l_button.clicked.connect(self.launch_a2l)

        self.text_box_dbc = FileEdit()
        self.text_box_dbc.setPlaceholderText('Path to dbc ')
        self.dbc_button = QPushButton('dbc')
        self.dbc_button.setIcon(QtGui.QIcon(r'icon\folder-8.png'))
        self.dbc_button.setIconSize(QtCore.QSize(15, 15))
        self.dbc_button.clicked.connect(self.launch_dbc)

        grid3_layout = QGridLayout()
        grid3_layout.addWidget(self.text_box_flash_cna, 0, 0, 1, 2)
        grid3_layout.addWidget(self.text_box_ip_address, 1, 0, 1, 1)
        grid3_layout.addWidget(self.ip_ping_cfg_button, 1, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_canape, 2, 0, 1, 1)
        grid3_layout.addWidget(self.canape_cfg_button, 2, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_canalyzer, 3, 0, 1, 2)
        grid3_layout.addWidget(self.text_box_MRR1plus_cfg, 4, 0, 1, 1)
        grid3_layout.addWidget(self.MRR1plus_cfg_button, 4, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_MRR1plus_cna, 5, 0, 1, 1)
        grid3_layout.addWidget(self.MRR1plus_cna_button, 5, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_DiaTester_cna, 6, 0, 1, 1)
        grid3_layout.addWidget(self.DiaTester_cna_button, 6, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_ClaraTE, 7, 0, 1, 1)
        grid3_layout.addWidget(self.ClaraTE_button, 7, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_error_doc, 8, 0, 1, 1)
        grid3_layout.addWidget(self.error_doc_button, 8, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_a2l, 9, 0, 1, 1)
        grid3_layout.addWidget(self.a2l_button, 9, 1, 1, 1)
        grid3_layout.addWidget(self.text_box_dbc, 10, 0, 1, 1)
        grid3_layout.addWidget(self.dbc_button, 10, 1, 1, 1)

        self.group_box_3.setLayout(grid3_layout)

        # Main layout
        grid_main = QGridLayout()
        grid_main.addWidget(self.group_box_1, 0, 0)
        grid_main.addWidget(self.group_box_2, 1, 0)
        grid_main.addWidget(self.group_box_3, 2, 0)
        grid_main.setRowStretch(0, 1)
        grid_main.setRowStretch(1, 5)
        grid_main.setRowStretch(2, 1)

        self.setLayout(grid_main)

        if str(self.ini_configParser.get('PATH', 'RECENT_SW')) != 'N.A':
            try:
                self.text_box_dir.setText(str(self.ini_configParser.get('PATH', 'RECENT_SW')))
                self.get_file_and_path()
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Unable to load recent SW')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()

    def edit_configuration_canape(self):
        sw_path = ''
        trigger = False
        if os.path.isdir(self.text_box_dir.text()):
            if 'RadarFC' in self.text_box_dir.text():
                sw_path = self.text_box_dir.text().replace('RadarFC','')
                trigger = True
            elif 'RadarRR' in self.text_box_dir.text():
                sw_path = self.text_box_dir.text().replace('RadarRR', '')
                trigger = True
            elif 'RadarRL' in self.text_box_dir.text():
                sw_path = self.text_box_dir.text().replace('RadarRL', '')
                trigger = True
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText('Invalid software path')
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()

            if trigger:
                self.get_thread = ConfigCANAPEThread(sw_path)
                self.get_thread.start()
                self.get_thread.finished.connect(self.edit_config_done)
                self.canape_cfg_button.setEnabled(False)

        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Invalid software path')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def edit_config_done(self):
        self.canape_cfg_button.setEnabled(True)
        dialog = QMessageBox()
        dialog.setWindowTitle('Information')
        dialog.setText('Process finished')
        dialog.setIcon(QMessageBox.Information)
        dialog.exec_()

    def browse_path(self):
        file_object = QFileDialog.getExistingDirectory(self, "Select Directory")
        if file_object != '':
            self.text_box_dir.setText(str(file_object))

    def on_select_item_list_view(self):
        item_list = self.file_list_view.selectedItems()
        self.no_file_selected = len(item_list)
        self.flashable_items_status.setText(f'{self.no_file_found} found, {self.no_file_selected} selected')

    def ping_IP_address(self):
        regex_ip = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
        ip_address = self.text_box_ip_address.text()
        x = re.match(regex_ip, ip_address)
        if x and os.path.isdir(self.text_box_flash_cna.text()) and self.radar_type != 'N.A':
            self.ping_thread = PingIpAddressThread(ip_address, self.text_box_flash_cna.text()+'\\canape.ini', self.radar_type)
            self.ping_thread.start()
            self.ping_thread.finished.connect(self.ip_done)
            self.get_file_path_button.setEnabled(False)
            self.flash_button.setEnabled(False)

    def ip_done(self):
        self.get_file_path_button.setEnabled(True)
        self.flash_button.setEnabled(True)
        if self.ping_thread.is_response_ok:
            dialog = QMessageBox()
            dialog.setWindowTitle(self.ping_thread.response_type)
            dialog.setText(self.ping_thread.response_message)
            dialog.setIcon(QMessageBox.Information)
            dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle(self.ping_thread.response_type)
            dialog.setText(self.ping_thread.response_message)
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_ClaraTE(self):
        self.ini_configParser['PATH']['CLARA_TE'] = self.text_box_ClaraTE.text()
        with open(r'data\cfg.ini', 'w') as configfile:
            self.ini_configParser.write(configfile)
        if os.path.isfile(self.text_box_ClaraTE.text()):
            try:
                # fb = open('ClaraTE.bat', 'w')
                temp = self.text_box_ClaraTE.text()
                # my_cmd0 = temp[:temp.index(':') + 1]
                misc = '\\'
                # my_cmd1 = f'cd "{temp[:temp.rfind(misc)]}"'
                path_t = f"{temp[:temp.rfind(misc)]}"
                os.startfile(path_t)
                # my_cmd2 = temp
                # fb.write(my_cmd0)
                # fb.write('\n')
                # fb.write(my_cmd1)
                # fb.write('\n')
                # fb.write(my_cmd2)
                # fb.close()
                # subprocess.Popen([temp], shell=True)
                # subprocess.call([temp], shell=True)
                # self.get_thread = ClaraTEThread(temp)
                # self.get_thread.finished.connect(self.done)
                # self.get_thread.start()
                # self.ClaraTE_button.setEnabled(False)

            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('ClaraTE is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def done(self):
        self.ClaraTE_button.setEnabled(True)

    def launch_errordoc(self):
        if os.path.isdir(self.text_box_error_doc.text()):
            try:
                os.startfile(self.text_box_error_doc.text())
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('errordoc is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_a2l(self):
        if os.path.isdir(self.text_box_a2l.text()):
            try:
                os.startfile(self.text_box_a2l.text())
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('a2l is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_dbc(self):
        if os.path.isdir(self.text_box_dbc.text()):
            try:
                os.startfile(self.text_box_dbc.text())
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('dbc is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_MRR1plus_cfg(self):
        self.ini_configParser['PATH']['CANALYZER'] = self.text_box_canalyzer.text()
        with open(r'data\cfg.ini', 'w') as configfile:
            self.ini_configParser.write(configfile)
        if os.path.isfile(self.text_box_MRR1plus_cfg.text()) and os.path.isfile(self.text_box_canalyzer.text()):
            try:
                #subprocess.call([self.text_box_MRR1plus_cfg.text()])
                subprocess.Popen([self.text_box_canalyzer.text(), '/f', self.text_box_MRR1plus_cfg.text()])
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('MRR1plus.cfg or canalyzer is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_MRR1plus_cna(self):
        self.ini_configParser['PATH']['CANAPE'] = self.text_box_canape.text()
        with open(r'data\cfg.ini', 'w') as configfile:
            self.ini_configParser.write(configfile)
        if os.path.isfile(self.text_box_MRR1plus_cna.text()) and os.path.isfile(self.text_box_canape.text()):
            try:
                fb = open('MRR1plus_cna.bat', 'w')
                temp = self.text_box_MRR1plus_cna.text()
                my_cmd0 = temp[:temp.index(':') + 1]
                misc = '\\'
                my_cmd1 = f'cd "{temp[:temp.rfind(misc)]}"'
                my_cmd2 = f'"{self.text_box_canape.text()}" -b "{self.text_box_MRR1plus_cna.text()}"'
                fb.write(my_cmd0)
                fb.write('\n')
                fb.write(my_cmd1)
                fb.write('\n')
                fb.write(my_cmd2)
                fb.close()
                subprocess.Popen('MRR1plus_cna.bat')
                #subprocess.call([self.text_box_canape.text(), self.text_box_MRR1plus_cna.text()])
                #subprocess.Popen([self.text_box_canape.text(), '-b', self.text_box_MRR1plus_cna.text()])
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('MRR1plus.cna or canape is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

    def launch_DiaTester_cna(self):
        self.ini_configParser['PATH']['CANAPE'] = self.text_box_canape.text()
        with open(r'data\cfg.ini', 'w') as configfile:
            self.ini_configParser.write(configfile)
        if os.path.isfile(self.text_box_DiaTester_cna.text()) and os.path.isfile(self.text_box_canape.text()):
            try:
                fb = open('DiaTester_cna.bat', 'w')
                temp = self.text_box_DiaTester_cna.text()
                my_cmd0 = temp[:temp.index(':') + 1]
                misc = '\\'
                my_cmd1 = f'cd "{temp[:temp.rfind(misc)]}"'
                my_cmd2 = f'"{self.text_box_canape.text()}" -b "{self.text_box_DiaTester_cna.text()}"'
                fb.write(my_cmd0)
                fb.write('\n')
                fb.write(my_cmd1)
                fb.write('\n')
                fb.write(my_cmd2)
                fb.close()
                subprocess.Popen('DiaTester_cna.bat')
                #subprocess.call([self.text_box_canape.text(), self.text_box_DiaTester_cna.text()])
                #subprocess.Popen([self.text_box_canape.text(), '-b', self.text_box_DiaTester_cna.text()])
            except Exception as e:
                dialog = QMessageBox()
                dialog.setWindowTitle('Error')
                dialog.setText(str(e))
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('DiaTester.cna or canape is not available')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()


    def run_flash_software(self):
        selected_flashabe_items = self.file_list_view.selectedItems()
        selected_flashabe_items_pass = []
        flag1 = False
        flag2 = False
        flag3 = False
        flag4 = False

        for item in selected_flashabe_items:
            item_text = self.flashable_items_list_root_path + item.text()
            item_name = item_text[item_text.rfind('\\')+1:]
            selected_flashabe_items_pass.append([item_text, item_name])

        if len(selected_flashabe_items) != 0:
            flag1 = True
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('No file is selected')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

        if os.path.isdir(self.text_box_flash_cna.text()):
            flag2 = True
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('flash_all folder path is invalid')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

        if os.path.isfile(self.text_box_canape.text()):
            flag3 = True
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('canape.exe cannot be found')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

        if self.radar_type != 'N.A':
            flag4 = True
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle('Error')
            dialog.setText('Radar type is undefined')
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

        if flag1 and flag2 and flag3 and flag4:
            self.get_thread = FlashSoftwareThread(selected_flashabe_items_pass, self.text_box_flash_cna.text(), self.text_box_canape.text(), self.radar_type)
            self.get_thread.start()
            self.get_thread.finished.connect(self.flash_done)
            self.get_file_path_button.setEnabled(False)
            self.flash_button.setEnabled(False)
            self.ip_ping_cfg_button.setEnabled(False)

    def flash_done(self):
        self.get_file_path_button.setEnabled(True)
        self.flash_button.setEnabled(True)
        self.ip_ping_cfg_button.setEnabled(True)
        if self.get_thread.cmd_success:
            dialog = QMessageBox()
            dialog.setWindowTitle("Ok")
            dialog.setText("Flash successfully")
            dialog.setIcon(QMessageBox.Information)
            dialog.exec_()
        else:
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setText("Fail to execute command line")
            dialog.setIcon(QMessageBox.Information)
            dialog.exec_()

    def get_file_and_path(self):

        self.flashable_items_list.clear()

        if os.path.isdir(self.text_box_dir.text()):

            self.ini_configParser['PATH']['RECENT_SW'] = self.text_box_dir.text()
            with open(r'data\cfg.ini', 'w') as configfile:
                self.ini_configParser.write(configfile)

            is_MRR1plus_cfg = False
            is_MRR1plus_cna = False
            is_MRRrear_cna = False
            is_DiaTester_cna = False

            origin_root = self.text_box_dir.text()
            idex1 = origin_root.rfind('/')
            idex2 = origin_root.rfind('\\')
            if idex1 != -1:
                self.flashable_items_list_root_path = origin_root[:idex1 + 1]
            elif idex2 != -1:
                self.flashable_items_list_root_path = origin_root[:idex2 + 1]
            shorten_idx = len(self.flashable_items_list_root_path)

            if 'RadarFC' in origin_root:
                self.radar_type = 'RadarFC'
            elif 'RadarRR' in origin_root:
                self.radar_type = 'RadarRR'
            for root, dirs, files in os.walk(self.text_box_dir.text()):
                for file in files:
                    if '.srec' in file:
                        self.flashable_items_list.append(root[shorten_idx:] + '\\' + file) # shorten the full path before adding to list
                    if 'MRR1plus.cfg' == file:
                        self.text_box_MRR1plus_cfg.setText(root+'\\'+file)
                        is_MRR1plus_cfg = True
                    if 'MRR1plus.cna' == file:
                        self.text_box_MRR1plus_cna.setText(root + '\\' + file)
                        is_MRR1plus_cna = True
                    if 'DiaTester.cna' == file:
                        self.text_box_DiaTester_cna.setText(root + '\\' + file)
                        is_DiaTester_cna = True
                    if 'MRRrear.cna' == file:
                        self.text_box_MRR1plus_cna.setText(root + '\\' + file)
                        is_MRRrear_cna = True
                    if '03_EventId_DTC_Mapping_Dem_Cfg_DtcId.h' == file:
                        set_global_str(root + '\\' + file, 1)
                    elif 'DTC_DTCID_PROJECT.h' == file:
                        set_global_str(root + '\\' + file, 1)
                    if '01_EventId_ITC_index_table_DEM_DDL.csv' == file:
                        set_global_str(root + '\\' + file, 2)
                    elif '01_DTCInfo_PROJECT.csv' == file:
                        set_global_str(root + '\\' + file, 2)
                    if 'Dem_EventIds_Project.h' == file:
                        set_global_str(root + '\\' + file, 3)

                for item in dirs:
                    if 'flash_all' in item:
                        self.text_box_flash_cna.setText(root+'\\'+item)
                    if 'errordocu' == item:
                        self.text_box_error_doc.setText(root+'\\'+item)
                    if 'a2l' == item:
                        self.text_box_a2l.setText(root+'\\'+item)

                    if 'dbc' == item:
                        self.text_box_dbc.setText(root+'\\'+item)
                    if 'RadarFC' == item:
                        self.radar_type = 'RadarFC'
                    elif 'RadarRR' == item:
                        self.radar_type = 'RadarRR'
            if self.radar_type != 'N.A':
                self.flashable_radar_type.setText(f'Radar type: {self.radar_type}')

            if is_MRR1plus_cfg is False:
                self.text_box_MRR1plus_cfg.setText('Cannot found MRR1plus.cfg')
            if is_MRR1plus_cna is False and is_MRRrear_cna is False:
                self.text_box_MRR1plus_cna.setText('Cannot found MRRxxx.cna')
            if is_DiaTester_cna is False:
                self.text_box_DiaTester_cna.setText('Cannot found DiaTester.cna')

            self.file_list_view.clear()

            # add found .srec into list view
            for index, item in enumerate(self.flashable_items_list):
                self.file_list_view.insertItem(index, self.flashable_items_list[index])
                self.no_file_found = len(self.flashable_items_list)
                self.flashable_items_status.setText(f'{self.no_file_found} found, {self.no_file_selected} selected')

            if os.path.isdir(self.text_box_flash_cna.text()):
                for root, dirs, files in os.walk(self.text_box_flash_cna.text()):
                    for file in files:
                        if 'canape.ini' == file:
                            canape_INI = root + '\\' + file
                            configParser = configparser.ConfigParser(allow_no_value=True)
                            configParser.optionxform = str
                            try:
                                fileObject = open(canape_INI, "r")
                                configParser.read_file(fileObject)
                                fileObject.close()
                                IP_address_RadarFC = configParser.get(f"Module_{self.radar_type}", "HOST")
                                self.text_box_ip_address.setText(IP_address_RadarFC)
                            except Exception as e:
                                dialog = QMessageBox()
                                dialog.setWindowTitle("Error")
                                dialog.setText(f'Fail to obtain IP address: {e}')
                                dialog.setIcon(QMessageBox.Critical)
                                dialog.exec_()
            else:
                dialog = QMessageBox()
                dialog.setWindowTitle("Error")
                dialog.setText("Invalid flash_all folder path")
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec_()

        else:
            dialog = QMessageBox()
            dialog.setWindowTitle("Error")
            dialog.setText("Invalid Software Path")
            dialog.setIcon(QMessageBox.Critical)
            dialog.exec_()

if __name__ == "__main__":
    App = QApplication([])
    window = MainWindow()
    sys.exit(App.exec())


