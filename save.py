import csv
csv.register_dialect('hockdia', delimiter=':')
import os
from scraper import *

def saveTable(name,tableData):
    makeDir(name)
    table = tableData.stats
    tableName = tableData.name + '.csv'
    tableName = tableName.replace(" ", "_")
    path = "Saves/" + name + "/" + tableName
    with open(path, "w") as f:
        writer = csv.writer(f,'hockdia')
        writer.writerows(table)
    
def loadTable(name):
    name = name + '.csv'
    name = name.replace(' ', '_')
    with open("Saves/" + name, 'r') as r:
        reader = csv.reader(r,'hockdia')
        table = list(reader)
    return table
    
def setupSave():
    makeDir()
    
def makeDir(path = "Saves"):
    if path != "Saves":
        path = "Saves/" + path
    if not os.path.exists(path):
        os.makedirs(path)

if __name__ == '__main__':
    setupSave()
    url = findPlayer("Ovechkin")
    page = connectToPage(url)
    name = url.split("/")[-1]
    #TableData object is returned by getTables
    tables = getTables(page)
    saveTable(name,tables[0])
    