import sys
from bs4 import *
import urllib.request
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QCheckBox, QLabel, QDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot, QThread
import webbrowser
import pymsgbox
import os

fwd = None
rwd = None
vin_choice = None
gear_box_choice = None
value = None

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Find nice car deals'
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600
        self.auto_pic = r'image.png'
        self.threading = Scrape()
        self.threading.start()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.gear_box = QCheckBox("Manual?", self)
        self.vin = QCheckBox("Check Vin?", self)
        self.rwd = QCheckBox("RWD?", self)

        self.gear_box.move(0, 320)
        self.vin.move(60, 320)
        self.rwd.move(0, 300)
        self.stopbutton = QPushButton("Exit", self)
        self.stopbutton.clicked.connect(self.exit)
        #creating a textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(0, 350)
        self.textbox.resize(100, 30)
        button_submit_page_number = QPushButton("Page number", self)
        button_submit_page_number.move(0,380)
        button_submit_page_number.clicked.connect(self.on_click)
        textbox_value = self.textbox.text()
        #Creating auto24 logo
        auto24 = QLabel(self)
        auto24_pic = QPixmap(self.auto_pic)
        auto24.setPixmap(auto24_pic)
        auto24.resize(444, 86)
        auto24.move(350, 0)

        self.show()
    def on_click(self):
        global value
        global gear_box_choice
        global vin_choice
        global fwd
        global rwd
        try:
            value = self.textbox.text()
        except:
            os._exit(1)
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


        print(gear_box_value)
        print("Page selected: " + value)
        self.threading.find_deals()
    def exit():
        os._exit(1)
class Scrape(QThread):
    def __init__(self):
        super().__init__()
        self.ok = 'wtf'

    def find_deals(self):
        global value
        try:
            value = int(value)
        except:
            print("Incorrect value, exiting the program, PLEASE ONLY INPUT AN INTEGER")
            os._exit(1)

        def page_algorithm(i): #An algorithm that makes it easy to turn to a next page
            if i > 1:
                i = i * 50 - 50
                return 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101' + '&ak=' + str(i)
            else:
                return 'http://www.auto24.ee/kasutatud/nimekiri.php?a=101'

        page_number = page_algorithm(value)
        print(page_number)
        def deals():
            self.url = page_number
            self.urlreq = urllib.request.urlopen(self.url).read()
            self.soup = BeautifulSoup(self.urlreq, 'lxml')
            table = self.soup.find('table', class_='section search-list')  # Finding the table that has a class called section search-list
            #text = re.compile("kW$")  # using regex to see if a string ends with kW (this will not get the hrefs of pictures) ( NOT USING IT ATM )
            url = table.find_all('a', href=True, class_='small-image') # Finding all the <a> tags in that table with a class small-image
            i = 0
            for href in url:
                ok = href.get('href') # Finding all the href tags
                if ok.startswith('/used') and ok.endswith('#loan=72') is False:  # if the tag starts with /used then open it up also ignore loans
                    car_url = "http://www.auto24.ee" + ok  # this will be the url we will be working on mainly
                    new_url = urllib.request.urlopen(car_url).read()  # the beginning of creating a bs4 object
                    i = i + 1
                    print("Cars scanned: {} ".format(i))
                    if i >= 50:
                        print("First page finished")
                        pymsgbox.alert("First page finished!")
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
                        if int(odometer_size_int_new) > 250000: # If there are more than 200k km on the odometer then it's bad
                            return False
                        else:
                            return True

                    except AttributeError:
                        return False
                def check_vin():
                    if vin_choice is True:
                        car_info_table = car_deal.find('table', class_='section main-data')
                        # Finding the info table
                        table_type = car_info_table.find('tr', class_='field-tehasetahis')
                        vin_preview = table_type.find('span', class_= 'preview')
                        try:
                            vin = vin_preview.text
                            return True

                        except AttributeError:
                            return False
                    elif vin_choice is False:
                        car_info_table = car_deal.find('table', class_='section main-data')
                        # Finding the info table
                        table_type = car_info_table.find('tr', class_='field-tehasetahis')
                        vin_preview = table_type.find('span', class_='preview')
                        try:
                            vin = vin_preview.text
                            return False

                        except AttributeError:
                            return True
                def check_gearbox():

                    if gear_box_choice is True:
                        car_info_table = car_deal.find('table', class_='section main-data')
                        table_type = car_info_table.find('tr', class_='field-kaigukast_kaikudega')
                        value = table_type.find('span', class_='value')
                        try:
                            new_value = value.text
                            if new_value == "manuaal":
                                return True
                            else:
                                return False
                        except AttributeError:
                            return False
                    elif gear_box_choice is False:
                        car_info_table = car_deal.find('table', class_='section main-data')
                        table_type = car_info_table.find('tr', class_='field-kaigukast_kaikudega')
                        value = table_type.find('span', class_='value')
                        try:
                            new_value = value.text
                            if new_value == "automaat":
                                return True
                            else:
                                return False
                        except AttributeError:
                            return False

                def check_rwd():
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
                        print("Discount price: " + discount_price.text)
                        print("Price: " + price.text)
                    except:
                        print("car has no discount price")

                    #print(discount_price.text)
                def best_car():
                    pass
                if car_type() is True and odometer() is True and check_vin() is True and check_dealer() is True and \
                check_gearbox() is True and check_rwd() is True:
                    print("Car found, opening url...")
                    webbrowser.get('firefox').open(car_url)
                elif rwd is True and vin_choice is True and gear_box_choice is True:
                    def find_rwd_cars():
                        temp = 1
                        for page in range(11): # &ak=50
                            page = temp * 50 - 50
                            temp += 1
                            #print(page)
                            rwd_car_deal = urllib.request.urlopen('http://www.auto24.ee/kasutatud/nimekiri.php?bn=2&a=101&aj=&i=1&p=2&ae=2&af=50&ag=0&ag=1&otsi=otsi&ak=' +str(page)).read()
                            soup = BeautifulSoup(rwd_car_deal, 'lxml')

                            rwd_table = soup.find('table', class_="section search-list")
                            rwd_url = rwd_table.find_all('a', href=True, class_="small-image")
                            car_count = 0
                            for rwd_href in rwd_url:
                                rwd_link = rwd_href.get('href')
                                print(rwd_link)

                                if rwd_link.startswith('/used') and rwd_link.endswith('#loan=72') is False:
                                    rwd_car_url = "http://www.auto24.ee" + rwd_link
                                    rwd_car_url_2 = urllib.request.urlopen(rwd_car_url).read()

                                    rwd_car_object = BeautifulSoup(rwd_car_url_2, 'lxml')

                                    car_info_table = rwd_car_object.find('table', class_="section main-data")
                                    table_type = car_info_table.find('tr', class_="field-tehasetahis")
                                    table_value = table_type.find('span', class_="preview")
                                    if vin is not None:
                                        webbrowser.get('firefox').open(rwd_car_url)


                    find_rwd_cars()



        deals()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()  # uncomment this later
    # lol = Scrape()
    sys.exit(app.exec_())

