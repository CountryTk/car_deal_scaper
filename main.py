import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QLabel, QCheckBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from multiprocessing import Process
from time import sleep
from bs4 import *
import urllib.request
from subprocess import Popen, PIPE
import webbrowser
import platform
from PyQt5 import QtTest
import os
import pwd

fwd = None
rwd = None
vin_choice = None
gear_box_choice = None
value = None
running = None

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Car deal finder'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.run = True
        #self.ignore()
        self.initUI()

    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.gear_box = QCheckBox("Manual?", self)
        self.vin = QCheckBox("Check Vin?", self)
        self.rwd = QCheckBox("RWD?", self)

        self.gear_box.move(0, 320)
        self.vin.move(70, 320)
        self.rwd.move(0, 300)

        #creating a textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(0, 350)
        self.textbox.resize(100, 30)
        newlabel = QLabel("<--- Enter the page number (1, 2, etc)", self)
        newlabel.move(100,350)
        newlabel.resize(200,30)
        button_submit_page_number = QPushButton("Search", self)
        autist = QPushButton('Exit', self)
        autist.clicked.connect(self.wat)
        button_submit_page_number.move(0,380)
        button_submit_page_number.clicked.connect(self.on_click)
        textbox_value = self.textbox.text()
        #Help label
        help_label = QLabel('''How to use:
        1) Checking the "Manual" checkbox will only look for manual transmission
        cars, unchecking it will only look for automatic transmission cars.
        2) Checking "RWD?sys" will only look for rear wheel drive cars and unchecking
        it will only look for front wheel drive cars.
        3) Checking "Check Vin?" will only look for cars that have vin codes and
        unchecking it only looks for cars
        without vin code.
         ''', self)
        help_label.move(320,0)
        help_label.resize(600,180)
        odometer_value = QLabel("Maksimum läbisõit (km)", self)
        self.odometer_value_box = QLineEdit(self)
        self.odometer_value_box.move(0,270)
        odometer_value.move(0, 250)
        self.show()

    @pyqtSlot()
    def on_click(self):
        global value
        global gear_box_choice
        global vin_choice
        global fwd
        global rwd
        global running

        try:
            odometer_value = self.odometer_value_box.text()
            odometer_value_int = int(odometer_value)
            print(odometer_value_int)
            value = self.textbox.text()
            print(value)
        except:
            pass
        gear_box_value = self.gear_box.isChecked()
        vin_box_value = self.vin.isChecked()
        rwd_check = self.rwd.isChecked()
        if gear_box_value is True:
            gear_box_choice = True

        else:
            gear_box_choice = False
        if vin_box_value is True:
            vin_choice = True
        else:
            vin_choice = False
        if rwd_check is True:
            rwd = True
        else:
            rwd = False


        running = True
        print("Page selected: " + str(value))
        self.on_click_run()
    def auto24_scraper(self):
        global running
        while running:
            i = 0
            temporary = 1
            if running is True:
                print(running)
            else:
                print("Breaking")
                break
            for pages in range(325):

                pagenumber = temporary * 50 - 50
                if running is True:
                    pass
                else:
                    print("Breaking")
                    break
                url = "http://www.auto24.ee/kasutatud/nimekiri.php?a=101&ak=" + str(pagenumber)
                print("Moving to page: {}".format(url))
                print("Currently on page: {}".format(temporary))
                request_url = urllib.request.urlopen(url).read()
                object = BeautifulSoup(request_url, 'lxml')
                table = object.find('table', class_="section search-list")
                url = table.find_all('a', href=True, class_="small-image")
                for href in url:

                    ok = href.get('href')
                    if ok.startswith('/used') and ok.endswith('#loan=72') is False:
                        car_url = "http://www.auto24.ee" + ok
                        print(car_url)
                        new_url = urllib.request.urlopen(car_url).read()
                        i += 1
                        print("Cars scanned {}".format(i))
                        if running is True:
                            pass
                        elif running is False:
                            print("Breaking...")
                            break
                        car_deal = BeautifulSoup(new_url, 'lxml')

                    def odometer():
                        car_info_table = car_deal.find('table', class_='section main-data')
                        table_type = car_info_table.find('tr', class_='field-labisoit')
                        table_value = table_type.find('span', class_='value')
                        try:
                            odometer_size = table_value.string
                            nonBreakSpace = u'\xa0'  # Creating the breakspace so we could remove that
                            odometer_size_int = odometer_size.replace('km', '')
                            odometer_size_int_new = odometer_size_int.replace(nonBreakSpace, '')  # Removing &nonbreakspace
                            if int(odometer_size_int_new) > int(self.odometer_value_box.text()): # If there are more than 200k km on the odometer then it's bad
                                return False
                            else:
                                return True

                        except AttributeError:
                            return False
                    def check_vin():
                        global vin_choice
                        if vin_choice is True:
                            car_info_table = car_deal.find('table', class_='section main-data')
                            table_type = car_info_table.find('tr', class_='field-tehasetahis')
                            vin_preview = table_type.find('span', class_='preview')
                            try:
                                vin = vin_preview.text
                                return True
                            except AttributeError:
                                return False
                        elif vin_choice is False:
                            car_info_table = car_deal.find('table', class_='section main-data')
                            table_type = car_info_table.find('tr', class_='field-tehasetahis')
                            vin_preview = table_type.find('span', class_='preview')
                            try:
                                vin = vin_preview.text
                                return True
                            except AttributeError:
                                return True

                    def check_gearbox():
                        global gear_box_choice
                        if gear_box_choice is True:
                            car_info_table = car_deal.find('table', class_='section main-data')
                            table_type = car_info_table.find('tr', class_='field-kaigukast_kaikudega')
                            value = table_type.find('span', class_='value')
                            try:
                                gearbox = value.text
                                if gearbox == "manuaal":
                                    return True
                                else:
                                    return False
                            except AttributeError:
                                return True
                        elif gear_box_choice is False:
                            car_info_table = car_deal.find('table', class_='section main-data')
                            table_type = car_info_table.find('tr', class_='field-kaigukast_kaikudega')
                            value = table_type.find('span', class_='value')
                            try:
                                gearbox = value.text
                                if gearbox == "automaat":
                                    return True
                                else:
                                    return False
                            except AttributeError:
                                return True
                    def check_rwd():
                        global rwd
                        if rwd is True:
                            car_info_table = car_deal.find('table', class_="section main-data")
                            table_type = car_info_table.find('tr', class_='field-vedavsild')
                            value = table_type.find('span', class_='value')
                            try:
                                new_value = value.text
                                if new_value == "tagavedu":
                                    return True
                            except AttributeError:
                                return False
                        elif rwd is False:
                            car_info_table = car_deal.find('table', class_="section main-data")
                            table_type = car_info_table.find('tr', class_='field-vedavsild')
                            value = table_type.find('span', class_='value')
                            try:
                                new_value = value.text
                                if new_value == "esivedu":
                                    return True
                            except AttributeError:
                                    return False
                    def check_dealer():
                        car_info_table = car_deal.find('h1', class_='commonSubtitle')  # GOing in the h1 class
                        get_dealer = car_info_table.find('a', class_='dealer-name')
                        try:
                            scam = get_dealer.text
                            if scam == "- Autojärelmaks24 Kesk-Sõjamäe" or scam == "- Autojärelmaks24 Lasnamäe":  # Then checking if the car dealer is auto24jarelmaks(shit)
                                return False
                            else:
                                return True
                        except AttributeError:
                            return True
                    def check_price():
                        car_info_table = car_deal.find('table', class_='section main-data')
                        table_type = car_info_table.find('tr', class_='field-hind')
                        price_table = table_type.find('td', class_='field')
                        price = price_table.find('span', class_="value")
                        discount_table_type = car_info_table.find('tr', class_='field-soodushind')
                        try:
                            discount_price_table = discount_table_type.find('td', class_='field')
                            discount_price = discount_price_table.find('span', class_="value")
                            print("Price: " + price.text)
                            print("Discount price: " + discount_price.text)

                        except:
                            print("Car has no discount price")

                    if check_vin() is True and check_gearbox() is True and check_rwd() is True and check_dealer() is True \
                            and odometer() is True:
                        print("Car found...")
                        print("Opening...")
                        print("Waiting 20 seconds...")
                        check_price()
                        webbrowser.get('firefox').open(car_url)
                        QtTest.QTest.qWait(20000)

                temporary += 1

    def wat(self):
        os._exit(1)
    def on_click_run(self):
        self.auto24_scraper()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    os._exit(app.exec_())
