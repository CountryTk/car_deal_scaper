import sys
from bs4 import *
import urllib.request
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot, QThread
import webbrowser
from time import sleep






class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Find nice car deals'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.threading = Scrape()
        self.threading.start()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        label = QLabel(self)
        label.resize(500, 500)
        label.setText('lk')
        button = QPushButton("click for magic", self)
        button.clicked.connect(self.threading.find_deals)

        self.show()

class Scrape(QThread):
    def __init__(self):
        super().__init__()
        self.ok = 'wtf'
        self.url = 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101'
        self.urlreq = urllib.request.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.urlreq, 'lxml')
        self.find_deals()

    def find_deals(self):
        table = self.soup.find('table', class_='section search-list') # Finding the table that has a class called section search-list
        url = table.find_all('a') # Finding all the <a> tags in that table

        for href in url:
            ok = href.get('href') # Finding all the href tags

            if ok.startswith('/used') and ok.endswith('#loan=72') == False: # if the tag starts with /used then open it up also ignore loans
                car_url = "http://www.auto24.ee" + ok # this will be the url we will be working on mainly
                # webbrowser.open(car_url) # Opening the url for the person to see it (this should be the last step)
                new_url = urllib.request.urlopen(car_url).read() # the begininng of creating a bs4 object
                car_deal = BeautifulSoup(new_url, 'lxml') # Making it into an object

                def car_type():

                    car_info_table = car_deal.find('table', class_='section main-data')  # Finding the info table

                    table_type = car_info_table.find('tr', class_='field-liik')  # Finding the car type table

                    table_value = table_type.find('span', class_='value')  # Getting the value

                    type_of_car = table_value.text

                    if type_of_car == "sõiduauto":
                        return True
                    else:
                        return False

                def odometer():

                    car_info_table = car_deal.find('table', class_='section main-data')
                    # Finding the info table
                    table_type = car_info_table.find('tr', class_='field-labisoit')
                    # Finding the car odometer table
                    table_value = table_type.find('span', class_='value')

                    try:
                        odometer_size = table_value.string

                        nonBreakSpace = u'\xa0'  # Creating the breakspace so we could remove that

                        odometer_size_int = odometer_size.replace('km', '')

                        odometer_size_int_new = odometer_size_int.replace(nonBreakSpace, '')  # Removing &nonbreakspace

                        if int(odometer_size_int_new) > 200000: # If there are more than 200k km on the odometer then it's bad
                            return False
                        else:
                            return True

                    except AttributeError:
                        return False
                def check_vin():
                    car_info_table = car_deal.find('table', class_='section main-data')
                    # Finding the info table
                    table_type = car_info_table.find('tr', class_='field-tehasetahis')
                    vin_preview = table_type.find('span', class_= 'preview')
                    try:
                        vin = vin_preview.text
                        return True
                    except AttributeError:
                        return False

                if car_type() == True and odometer() == True and check_vin() == True:
                    webbrowser.open(car_url)
                    print("Car found!")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()  # uncomment this later
    #lol = Scrape()
    sys.exit(app.exec_())
