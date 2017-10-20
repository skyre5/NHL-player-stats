import csv
csv.register_dialect('hockdia', delimiter=':')
import os
from scraper import *

def saveTable(name,tableData):
    '''Saves an individual table to a .csv file to a given directory by playerId
    and the name of the table which is in the tableData object
    '''
    makeDir(name)
    table = tableData.stats
    tableName = tableData.name + '.csv'
    tableName = tableName.replace(" ", "_")
    path = "Saves/" + name + "/" + tableName
    with open(path, "w") as f:
        writer = csv.writer(f,'hockdia')
        writer.writerows(table)
    
def saveAllTables(name,listOfTables):
    '''Saves all the tables in a list of tableData objects'''
    for table in listOfTables:
        saveTable(name,table)

def listAllPlayers():
    '''Lists all the player ids from the saves directory'''
    listOfTables = os.listdir("Saves/")
    return listOfTables
    
def listTablesFromPlayer(playerId):
    '''Lists all the tables for a given player and prints them out'''
    listOfTables = os.listdir("Saves/" + playerId)
    print(listOfTables)

def loadTable(dirName,name):
    '''Loads a given table from a playerId and the the table wanted into
    a 2d list
    '''
    name = name + '.csv'
    name = name.replace(' ', '_')
    with open("Saves/" + dirName + '/' + name, 'r') as r:
        reader = csv.reader(r,'hockdia')
        table = list(reader)
    return table
    
def setupSave():
    '''Makes sure that the save directory exists'''
    makeDir()
    
def makeDir(path = "Saves"):
    '''Makes the directory for a given playerId'''
    if path != "Saves":
        path = "Saves/" + path
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == '__main__':
    setupSave()
    url = findPlayer("Ovechkin")
    page = connectToPage(url)
    name = url.split("/")[-1]
    #Separates the .html from the name ideally
    name = name.split(".")[0]
    #TableData object is returned by getTables
    tables = getTables(page)
    saveAllTables(name,tables)
    x = loadTable('ovechal01', 'Other_Playoffs')
    print(x)