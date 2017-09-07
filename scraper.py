
import requests
import bs4
import re
import logging

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
        """Returns the number of seasons that player has played"""
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
        self.stats = getStats(playerPage,self.url)

def connectToPage(pageUrl):
    """Takes any given url and parses it into a bs4.BeautifulSoup object"""
    logger.info("Accessing data on " + pageUrl)
    gotPage = requests.get(pageUrl)

    #If the website isn't reached ends the program
    gotPage.raise_for_status()

    #parses the webpage and gets its text
    textFromPage = bs4.BeautifulSoup(gotPage.text, "html.parser")
    return textFromPage

def getTables(page):
    """Gets all the tables from a given page(BeautifulSoup4 Object"""
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
                names.append("Similarity Scores By Career")
            else:
                title = names[-1] + " (2)"
                logger.info("Additional table created called " + title)
        else:
            title = title.contents[0]
        names.append(title)
        newGetStats(table,data)
        cleanTable(data)
def cleanTable(data):
    cleanHtml = re.compile('<.*?>')
    for y in range(len(data)):
        for x in range(len(data[0])):
            data[y][x] = re.sub(cleanHtml, '',str(data[y][x]))
    print(data)
    exit()

def getColumns(table,data):
    columnHeaders = table.findAll('th', attrs={'scope': 'col'})
    for columnNames in columnHeaders:
        data[0].append(columnNames['aria-label'])

def newGetStats(table,data):
    tableRows = table.findAll('tr', attrs={'class': ''})
    #Pops a repeat of the column names from the Rows
    tableRows.pop(0)
    #tableHeight = len(tableRows)
    #tableWidth = len(data[0])
    for i, rows in enumerate(tableRows):
        header = rows.find('th').contents[0]
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

def getStats(page, url):
    """Takes a beautiful object and returns a table of stats"""
    table = page.find('table', attrs={'id' : 'stats_basic_plus_nhl'})

    #Checks if the table may be different in the case of an older player having a different id for their stats
    #The case that brought this up is Glenn Hall who played in the 1950s
    if not table:
        table = page.find('table', attrs={'id': 'stats_basic_nhl'})
    #If there is no info to gather after both tries it logs the url that failed so it can be inspected
    #Will later upload this to a database so it can gather all fringe cases

    if not table:
        logger.error("Failed to find the table on this url\n" + url)
        raise Exception("Failed to find table")

    #Gathers to column names from the table
    #Could be expanded into a function with better functionality
    columnSection = table.findAll('th', attrs={'scope': 'col'})
    columnNames = []
    for x,name in enumerate(columnSection):
        colName = columnSection[x].contents[0]
        if not colName:
            continue
        #columnNames.append(x)
        columnNames.append(colName)

    #Improves the quality of the column names
    #EV was used for both goals and assists
    #If statement makes sure the stats are for a player and not a goalie
    if columnNames[10] == "EV":
        for i in range(10,17):
            if i < 14:
                columnNames[i] += "G"
            else:
                columnNames[i] += "A"

    #Finds the table from this section
    tableBody = table.find('tbody')
    #Will list all the years in the table into a list
    tableRows = tableBody.findAll('tr')

    # Number of years they have played
    dataHeight = len(tableRows)
    # Number of stats available
    # 30 at time of testing
    dataLength = len(tableRows[0])

    data = getTableData(tableRows,dataLength,dataHeight)

    #A regex object that will strip the html tags that wrap the awards
    #Also strips a bold tag if that single statistic led the league
    cleanHtml = re.compile('<.*?>')
    #Looks through every single item in the lists and strips tags
    for row in data:
        for thing in row:
            thing[0] = re.sub(cleanHtml, '' , str(thing[0]))

    #Will take apart the list for the awards and
    #Create one concatenated string of all the honors from that year
    for row in data:
        #Base string to be added to or not if the player had no award nominations
        awardStr = ""
        #Refernces the last item in the row which is always awards
        awardList = row[-1]
        for i,thing in enumerate(awardList):
            awardStr += re.sub(cleanHtml,'',str(thing))
        #Places the newly constructed string into the awards column of the row
        row[-1] = [awardStr]


    returnStats = tableData(columnNames, data)
    return returnStats

#Takes the length and height of the column and loads them into a 2d list from the table about stats
def getTableData(tableInfo,length,height):
    #Constructs the 2d list
    data = [[None for x in range(length)] for y in range(height)]
    for y, row in enumerate(tableInfo):
        for x, col in enumerate(row):

            print(col.contents)
            # Makes the null values in the table set to 0
            # Such as faceoffs for wingers if they never took one in a given year
            #if not col.contents:
                #data[y][x] = ["0"]
                #continue
            #data[y][x] = col.contents
    return data



#Takes a string from a user input to search for a player
#Will return None if there were no results
#Will return a string if there was only one result
#Will return a searchResult object if there were multiple players found
def findPlayer(playerName):
    #Will take the user input string in the gui
    searchPage = requests.get(baseUrl+playerName)
    #Checks to see if it got a valid return
    searchPage.raise_for_status()
    if re.search(r'/players/',searchPage.url):
        #Returns if that search brings up an exact player
        return searchPage.url
    textFromPage = bs4.BeautifulSoup(searchPage.text, "html.parser")
    table = textFromPage.find('div', attrs={'id': 'players'})
    #If there are no search results return none
    if not table:
        return None
    #A list for all the players the search may have listed
    #Should always be at least 2 results
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
#Test cases to make sure the lookup works
#Run from the gui.py file to get the proper use of this application
if __name__ == "__main__":
    url = findPlayer("Ovechkin")
    page = connectToPage(url)
    table = getTables(page)


