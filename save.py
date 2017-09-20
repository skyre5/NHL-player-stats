import csv
csv.register_dialect('hockdia', delimiter=':')
import os
from scraper import *
def saveTable(tableData):
    table = tableData.stats
    name = tableData.name + '.csv'
    name = name.replace(" ", "_")
    with open("Saves/" + name, "w") as f:
        writer = csv.writer(f,'hockdia')
        writer.writerows(table)
    
def loadTable(name):
    name = name + '.csv'
    name = name.replace(' ', '_')
    with open("Saves/" + name, 'r') as r:
        reader = csv.reader(r,'hockdia')
        table = list(reader)
    return table
    

def checkIfDirExists():
    if not os.path.exists("Saves"):
        os.makedirs("Saves")

if __name__ == '__main__':
    url = findPlayer("Ovechkin")
    page = connectToPage(url)
    print(page[0])
    exit()
    #TableData object is returned by getTables
    tables = getTables(page)
    loadTable('NHL_Standard')
    