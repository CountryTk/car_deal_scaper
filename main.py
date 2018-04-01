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

            if ok.startswith('/used'): # if the tag starts with /used then open it up
                car_url = "http://www.auto24.ee" + ok # this will be the url we will be working on mainly
                #webbrowser.open(car_url) # Opening the url for the person to see it (this should be the last step)
                new_url = urllib.request.urlopen(car_url).read() # the begininng of creating a bs4 object
                car_deal = BeautifulSoup(new_url, 'lxml') # Making it into an object
                car_info_table = car_deal.find('table', class_='section main-data')  #Finding the info table
                a = car_info_table.find('tr', class_='field-liik') #Finding the liik table
                b = a.find('span', class_='value') #Getting the value
                print(b.text)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()  # uncomment this later
    #lol = Scrape()
    sys.exit(app.exec_())