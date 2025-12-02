import requests
import json
from dotenv import load_dotenv
import os
import oracledb


load_dotenv() #load the env stuff 
# setup for the database
user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")
dsn = os.getenv("ORACLE_DSN")

con = oracledb.connect(user=user, password=password, dsn=dsn)

cur = con.cursor()

def getPic(gameName):
    url = f"https://store.steampowered.com/api/storesearch?term={gameName}&l=english&cc=US"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items",[])
        if len(items) == 0:
            print("no game here")
            return
        else:
            item = items[0]
            name = item['name'].replace(' ','_')
            storeUrl = f"https://store.steampowered.com/app/{item['id']}/{name}/"
            detailsUrl = f"https://store.steampowered.com/api/appdetails?appids={item['id']}&cc=US&1-english"
            details = requests.get(detailsUrl)
            if details.status_code != 200:
                print('didnt get game info')
                return
            data = details.json()
            gameData = data[str(item['id'])]['data']
            return gameData.get('header_image')



#function to return a dict with the info of the steam game
def search_games(gameName):
    url = f"https://store.steampowered.com/api/storesearch?term={gameName}&l=english&cc=US"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items",[])

        print(f"results for {gameName}:")
        # for item in items[:1]:              #edit this line if you want to change how many results you get btw
        #     print(f"{item['id']}")
        if len(items) == 0:
            print('no results found')
            return
        else:
            item = items[0]
            name = item['name'].replace(' ','_')
            storeUrl = f"https://store.steampowered.com/app/{item['id']}/{name}/"
            print(storeUrl)

            detailsUrl = f"https://store.steampowered.com/api/appdetails?appids={item['id']}&cc=US&1-english"
            details = requests.get(detailsUrl)

            if details.status_code != 200:
                print('didnt get game info')
                return
            data = details.json()
            # print(json.dumps(data, indent=4))
            gameData = data[str(item['id'])]['data']
            rating = gameData.get('metacritic',{}).get('score',None) #will set to none if theres no metacritic
            genres = ", ".join([i['description'] for i in data[str(item['id'])]['data']['genres']])
            extractedData = {
                'id': item['id'],
                'image': gameData['img_logo_url'],
                'gamename': gameData['name'],
                'isFree': gameData['is_free'],
                'initialPrice': gameData['price_overview']['initial'] / 100,   # convert cents to dollars
                'currentPrice': gameData['price_overview']['final'] / 100,     # convert cents to dollars
                'discount': gameData['price_overview']['discount_percent'],
                'rating': rating,
                'genre': ", ".join([g['description'] for g in gameData['genres']]),  # plain string
                'releaseDate': gameData['release_date']['date'],
                'description': gameData['short_description'],
                'url': storeUrl
            }
            
            # print(extractedData)
            return(extractedData)
    

    else:
        print(f"error: {response.status_code}") #incase the request fails
        return 

#function to actually add it to the database, see sqldev to make sure
def addGame(gameName):
    gameinfo = search_games(gameName)
    sql = """
    INSERT INTO GAME (STEAMAPPID, IMAGE, GAMENAME, STEAMURL, BASEPRICE, CURRPRICE, RATING, GENRE, RELEASEDATE, DESCRIPTION)
    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, TO_DATE(:9, 'Mon DD, YYYY'), :10)
    """
    cur.execute(sql, (
        gameinfo['id'],
        gameinfo['image'],
        gameinfo['gamename'],
        gameinfo['url'],
        gameinfo['initialPrice'],
        gameinfo['currentPrice'],
        gameinfo['rating'],
        gameinfo['genre'],          # now a plain string
        gameinfo['releaseDate'],
        gameinfo['description']
    ))
    con.commit()
    print(f"successfully commited {gameinfo['gamename']}")
    return gameinfo


#function to search for a game, adds a game if its not in the database 
def searchGame(gameName):
    # First, search Steam for the game info
    gameinfo = search_games(gameName)
    if not gameinfo:
        print("Game not found on Steam")
        return None  # stop here if no game found

    # Check if the game is already in the database by STEAMAPPID
    sql_check = "SELECT * FROM GAME WHERE STEAMAPPID = :id"
    cur.execute(sql_check, {"id": gameinfo['id']})
    row = cur.fetchone()

    if row:
        # Game already exists, return it as a dict
        columns = [
            "id", "image", "gamename", "url", "initialPrice", "currentPrice",
            "rating", "genre", "releaseDate", "description"
        ]
        gameDict = dict(zip(columns, row))
        print(f"{gameinfo['gamename']} already in DB")
        return gameDict
    else:
        # Game not in DB, add it
        print(f"{gameinfo['gamename']} not in DB, adding now...")
        return addGame(gameName)

    
if __name__ == "__main__":
    try:
        # search_games('deltarune')
        # print(searchGame("undertale"))
        print(getPic('undertale'))
    finally:
        cur.close()
        con.close()
