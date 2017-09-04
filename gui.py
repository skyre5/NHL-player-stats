#TODO
#Build a database connection
#Be able to list off any table on a given players page

import sys, scraper, logging
from PyQt4 import QtCore, QtGui, uic
#Sets up the logging system for the program
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fillInData(self,tableWidget,player):
    url = scraper.findPlayer(player)
    if url is None:
        self.statusLabel.setText("None Found")
    elif isinstance(url[0], scraper.searchResult):
        self.statusLabel.setText(str(len(url)) + " Players Found")
        player = scraper.playerInfo(url[0].url)
    else:
        player = scraper.playerInfo(url)
    player.getPlayerInfo()
    tableData = player.stats
    tableWidget.setRowCount(len(tableData.stats))
    tableWidget.setColumnCount(len(tableData.columns))
    for i,name in enumerate(tableData.columns):
        tableWidget.setHorizontalHeaderItem(i,QtGui.QTableWidgetItem(name))
    #for x, row in enumerate(tableData.stats):
        #for y, col in enumerate(tableData.stats[0]):
    statsTable = tableData.stats
    for x,row in enumerate(statsTable):
        for y, name in enumerate(row):
            try:
                tableWidget.setItem(x,y,QtGui.QTableWidgetItem(name[0]))
            except Exception as e:
                print(e)

    tableWidget.resizeColumnsToContents()
qtCreatorFile = "form.ui"  # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        fillInData(self, self.tableWidget,"Hall")
        self.pushButton.clicked.connect(self.handleButton)
    def handleButton(self):
        text = self.lineEdit.text()
        fillInData(self,self.tableWidget,text)


if __name__ == "__main__":
    print(sys.path)
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())