
import logging
import re

import bs4
import requests

logger = logging.getLogger(__name__)
#Base url of the website that is scraped
website = "https://www.hockey-reference.com"
#The url that will take a search query
baseUrl = "https://www.hockey-reference.com/search/search.fcgi?search="

class searchResult:
    """Class that transports the results of a vague search with multiple results"""

    def __init__(self,name,url,lastPlayed):
        self.name = name
        self.url = url
        self.lastPlayed = lastPlayed

class tableData:
    """Class that holds the data for a table.
    Has separate variables for the column names and actual stats
    """

    def __init__(self,name,allStats):
        """Initializes the tableData object with a name
        and all the stats in a 2d rectangle list
        """
        self.name = name
        self.stats = allStats

    def __str__(self):
        """Returns the name of the table"""
        return self.name

class playerInfo:
    """Class that holds a players info as it is gathered online"""

    def __init__(self,pageUrl):
        """Stats is a 2d list that is gathered by getStats
        url is the website url of the player being gathered from
        """
        self.stats = None
        self.url = pageUrl

    def getPlayerInfo(self):
        """Takes the url, makes it into a BeautifulSoup object through connect
        page and then gathers the stats from the page through getStats
        """
        playerPage = connectToPage(self.url)
        #self.stats = getStats(playerPage,self.url)
        self.stats = getTables(playerPage)

def connectToPage(pageUrl):
    """Takes any given url and parses it into a bs4.BeautifulSoup object"""
    
    logger.info("Accessing data on " + pageUrl)
    gotPage = requests.get(pageUrl)

    #If the website isn't reached ends the program
    gotPage.raise_for_status()

    #parses the webpage into soup
    textFromPage = bs4.BeautifulSoup(gotPage.text, "html.parser")
    return textFromPage

def getTables(page):
    """Gets all the tables from a given BeautifulSoup4 Object (SOUP)"""
    
    #List of tableData objects which hold the name of the table and 2d stats
    returnData = []
    names = []
    tablesFromPage = page.findAll('div', attrs={'class' : 'table_wrapper'})
    for divs in tablesFromPage:
        table = divs.find('table')
        if not table:
            """The data in the comment is up to date and was the only way to access the data
            I believe the issue was due to javascript loading in this data after the state
            this program has"""
            placeholder = divs.find(text = lambda text:isinstance(text,bs4.Comment))
            html = bs4.BeautifulSoup(placeholder,'html.parser')
            table = html.find('table')
        data = [[]]
        getColumns(table,data)
        title = divs.find('h2')
        if title is None:
            if names[-1] == "Similarity Scores":
                names[-1] = "Similarity Scores By Career Length"
                title = "Similarity Scores By Career"
                names.append("Similarity Scores By Career")
            else:
                title = names[-1] + " (2)"
                logger.info("Additional table created called " + title)
        else:
            title = title.contents[0]
        names.append(title)
        newGetStats(table,data)
        cleanTable(data)
        returnData.append(tableData(title,data))
    return returnData


def cleanTable(data):
    """Cleans out any tags from the table. The examples I founder were
    hyperlinks for the award or bolding for leading the league in category
    """
    
    #Creates a regex that finds and then subtracts all found tags and contents
    cleanHtml = re.compile('<.*?>')
    for y in range(len(data)):
        for x in range(len(data[0])):
            data[y][x] = re.sub(cleanHtml, '',str(data[y][x]))

def getColumns(table,data):
    """Turns first row of data into column names"""
    
    #Finds all table headers and puts them into a list
    columnHeaders = table.findAll('th', attrs={'scope': 'col'})
    for columnNames in columnHeaders:
        data[0].append(columnNames['aria-label'])

def newGetStats(table,data):
    """Takes a table container in html and parses it's contents into
    my 2d list stats table.
    """
    
    #Finds all table rows from within the table. No class.... Damn
    tableRows = table.findAll('tr', attrs={'class': ''})
    
    #Pops a repeat of the column names from the Rows
    tableRows.pop(0)
    
    for i, rows in enumerate(tableRows):
        header = rows.find('th').contents[0]
        #Appends the header into the list as a list so it can be appended to
        data.append([header])
        for cols in rows.findAll('td'):
            if not cols.contents:
                #If the data is null in the table appends a blank string
                data[i + 1].append("")
            else:
                if len(cols.contents) > 1:
                    #Only for the awards category will make the list of Tags into Strings
                    #Which can use the join function to make it into one long string
                    rowInfo = ''.join(str(v) for v in cols.contents)
                else:
                    rowInfo = cols.contents[0]
                data[i + 1].append(rowInfo)
    return data


def findPlayer(playerName):
    '''Takes a string with a players name
    Returns a list of searchResult objects in case of a conflict
    Returns a url if a single player was found
    Returns none if there were no results found
    '''
    searchPage = requests.get(baseUrl+playerName)
    #Checks to see if it got a valid return
    searchPage.raise_for_status()
    #Returns in the case of a single player found
    if re.search(r'/players/',searchPage.url):
        return searchPage.url
        
    textFromPage = bs4.BeautifulSoup(searchPage.text, "html.parser")
    #Finds the container with the search result info
    table = textFromPage.find('div', attrs={'id': 'players'})
    
    #If there are no search results return none
    if not table:
        return None
        
    returnList = []
    #Finds all the search-items which lists each player that matched
    players = table.findAll('div', attrs={'class':'search-item'})
    #Goes through each player found and constructs an object
    for player in players:
        #The pathway to the data I want to return
        parsedInfo = player.contents[1].contents[1]
        #Finds the link to the player, name of the player, and the last team the player played for
        link = website + parsedInfo['href']
        name = parsedInfo.contents
        try:
            team = player.contents[7].contents
        except:
            logger.info(name[0] + " did not have a team statistic")
            team = "Unknown"

        #Creates the searchresult object and appends it onto a returnlist
        returnPlayer = searchResult(name,link,team)
        returnList.append(returnPlayer)
    return returnList



if __name__ == "__main__":
    url = findPlayer("Ovechkin")
    page = connectToPage(url)
    table = getTables(page)


