import csv
import os
#def saveTable():

#def loadTable():

def checkIfDirExists():
    if not os.path.exists("Saves"):
        os.makedirs("Saves")
    else:
        print("DIR EXISTS")
        
checkIfDirExists()