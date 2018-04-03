import sys
from bs4 import *
import urllib.request
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QLabel, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot, QThread
import webbrowser
from time import sleep
import re




value = None

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
        label.setText('Find your car  T O D A Y !!! ! ! !! ! ')
        #creating a textbox?
        self.textbox = QLineEdit(self)
        self.textbox.move(0,350)
        self.textbox.resize(100,40)
        button_submit_page_number = QPushButton("Submit page number", self)
        button_submit_page_number.move(0,390)
        #button_submit_page_number.clicked.connect(self.threading.find_deals)
        button_submit_page_number.clicked.connect(self.on_click)
        textbox_value = self.textbox.text()
        print(textbox_value)
        self.show()
    def on_click(self):
        global value
        value = self.textbox.text()
        print(value)
        self.threading.find_deals()
class Scrape(QThread):
    def __init__(self):
        super().__init__()
        self.ok = 'wtf'

        #self.page = input("Enter the page number:")
        #self.url = ''

        #self.find_deals()

        #url = 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101' + '&ak=' + str(50)



    def find_deals(self):
        global value
        value = int(value)
        def page_algorithm(i): #An algorithm that makes it easy to turn to a next page
            if i > 1:
                i = i * 50 - 50
                return 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101' + '&ak=' + str(i)
            else:
                return 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101'

        page_number = page_algorithm(value)

        self.url = page_number
        self.urlreq = urllib.request.urlopen(self.url).read()
        self.soup = BeautifulSoup(self.urlreq, 'lxml')
        table = self.soup.find('table', class_='section search-list')  # Finding the table that has a class called section search-list
        text = re.compile("kW$")  # using regex to see if a string ends with kW (this will not get the hrefs of pictures)
        url = table.find_all('a', href=True, text=text)  # Finding all the <a> tags in that table when the text ends with kW
        def new_page():
            url = 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101'+'&ak='+str(50)
            urlreq = urllib.request.urlopen(self.url).read()
            soup = BeautifulSoup(urlreq, 'lxml')
        i = 0
        for href in url:
            ok = href.get('href') # Finding all the href tags

            if ok.startswith('/used') and ok.endswith('#loan=72') == False:  # if the tag starts with /used then open it up also ignore loans

                car_url = "http://www.auto24.ee" + ok  # this will be the url we will be working on mainly

                new_url = urllib.request.urlopen(car_url).read()  # the beginning of creating a bs4 object
                i = i + 1
                print("Cars scanned: {} ".format(i))
                if 47 <= i <= 50:
                    print("First page finished") #turn to next page &ak=100
                    new_page()
                car_deal = BeautifulSoup(new_url, 'lxml')  # Making it into an object

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
                def check_dealer():
                    car_info_tale = car_deal.find('h1', class_='commonSubtitle')  # GOing in the h1 class
                    get_dealer = car_info_tale.find('a', class_='dealer-name')
                    try:
                        scam = get_dealer.text
                        if scam == "- Autojärelmaks24 Kesk-Sõjamäe" or scam == "- Autojärelmaks24 Lasnamäe":  # Then checking if the car dealer is auto24jarelmaks(shit)
                            return False
                        else:
                            return True
                    except AttributeError:
                        return True
                if car_type() is True and odometer() is True and check_vin() is True and check_dealer() is True:

                    webbrowser.open(car_url)

                    print("Car found!")
                def check_price():
                    car_info_table = car_deal.find('table', class_='section main-data')

                    table_type = car_info_table.find('tr', class_='field-hind')

                    price_table = table_type.find('td', class_='field')

                    price = price_table.find('span', class_="value")

                    discount_table_type = car_info_table.find('tr', class_='field-soodushind')

                    try:
                        discount_price_table = discount_table_type.find('td', class_='field')
                        discount_price = discount_price_table.find('span', class_="value")
                        print("Discount price: " + discount_price.text)
                        print("Price: " + price.text)
                    except:
                        print("car has no discount price")

                    #print(discount_price.text)
                check_price()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()  # uncomment this later
    # lol = Scrape()
    sys.exit(app.exec_())
