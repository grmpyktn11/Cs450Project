import requests
import json
from dotenv import load_dotenv
import os
import oracledb


load_dotenv()
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
            detailsUrl = f"https://store.steampowered.com/api/appdetails?appids={item['id']}&cc=US&1-english"
            details = requests.get(detailsUrl)
            if details.status_code != 200:
                print('didnt get game info')
                return
            data = details.json()
            gameData = data[str(item['id'])]['data']
            return gameData.get('header_image')


def search_games(gameName):
    url = f"https://store.steampowered.com/api/storesearch?term={gameName}&l=english&cc=US"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items",[])

        print(f"results for {gameName}:")
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
            gameData = data[str(item['id'])]['data']
            rating = gameData.get('metacritic',{}).get('score',None)
            
            # Check if game is free
            isFree = gameData.get('is_free', False)
            
            # Handle pricing - free games don't have price_overview
            if isFree:
                extractedData = {
                    'id': item['id'],
                    'gamename': gameData['name'],
                    'isFree': True,
                    'initialPrice': None,
                    'currentPrice': None,
                    'discount': None,
                    'rating': rating,
                    'genre': ", ".join([g['description'] for g in gameData.get('genres', [])]),
                    'releaseDate': gameData['release_date']['date'],
                    'description': gameData['short_description'],
                    'url': storeUrl,
                    'image': getPic(gameName)
                }
            else:
                # Paid game with price info
                priceOverview = gameData.get('price_overview', {})
                extractedData = {
                    'id': item['id'],
                    'gamename': gameData['name'],
                    'isFree': False,
                    'initialPrice': priceOverview.get('initial', 0) / 100,
                    'currentPrice': priceOverview.get('final', 0) / 100,
                    'discount': priceOverview.get('discount_percent', 0),
                    'rating': rating,
                    'genre': ", ".join([g['description'] for g in gameData.get('genres', [])]),
                    'releaseDate': gameData['release_date']['date'],
                    'description': gameData['short_description'],
                    'url': storeUrl,
                    'image': getPic(gameName)
                }
            
            return extractedData
    else:
        print(f"error: {response.status_code}")
        return 


def addFreeGame(gameinfo):
    """Add a free game to the FREEGAMES table"""
    sql = """
    INSERT INTO FREEGAMES (STEAMAPPID, GAMENAME, STEAMURL, RATING, GENRE, RELEASEDATE, DESCRIPTION, IMAGE)
    VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'Mon DD, YYYY'), :7, :8)
    """
    cur.execute(sql, (
        gameinfo['id'],
        gameinfo['gamename'],
        gameinfo['url'],
        gameinfo['rating'],
        gameinfo['genre'],
        gameinfo['releaseDate'],
        gameinfo['description'],
        gameinfo['image']
    ))
    con.commit()
    print(f"successfully added free game {gameinfo['gamename']} to FREEGAMES")
    return gameinfo


def addPaidGame(gameinfo):
    """Add a paid game to the GAME table"""
    sql = """
    INSERT INTO GAME (STEAMAPPID, GAMENAME, STEAMURL, BASEPRICE, CURRPRICE, RATING, GENRE, RELEASEDATE, DESCRIPTION, IMAGE)
    VALUES (:1, :2, :3, :4, :5, :6, :7, TO_DATE(:8, 'Mon DD, YYYY'), :9, :10)
    """
    cur.execute(sql, (
        gameinfo['id'],
        gameinfo['gamename'],
        gameinfo['url'],
        gameinfo['initialPrice'],
        gameinfo['currentPrice'],
        gameinfo['rating'],
        gameinfo['genre'],
        gameinfo['releaseDate'],
        gameinfo['description'],
        gameinfo['image']
    ))
    con.commit()
    print(f"successfully added paid game {gameinfo['gamename']} to GAME")
    return gameinfo


def updatePriceHistory(steamAppId, basePrice, currentPrice):
    """Update or create price history entry"""
    # Check if price history exists
    sql_check = "SELECT LOWESTPRICESEEN FROM PRICEHISTORY WHERE STEAMAPPID = :id"
    cur.execute(sql_check, {"id": steamAppId})
    row = cur.fetchone()
    
    if row:
        # Price history exists - check if we need to update lowest price
        currentLowest = row[0]
        if currentPrice < currentLowest:
            sql_update = """
            UPDATE PRICEHISTORY 
            SET LOWESTPRICESEEN = :lowest 
            WHERE STEAMAPPID = :id
            """
            cur.execute(sql_update, {"lowest": currentPrice, "id": steamAppId})
            con.commit()
            print(f"Updated lowest price to {currentPrice}")
    else:
        # No price history yet - create initial entry
        sql_insert = """
        INSERT INTO PRICEHISTORY (STEAMAPPID, LOWESTPRICESEEN, BASEPRICE)
        VALUES (:id, :lowest, :base)
        """
        cur.execute(sql_insert, {
            "id": steamAppId,
            "lowest": currentPrice,
            "base": basePrice
        })
        con.commit()
        print(f"Created price history with base price {basePrice} and initial lowest {currentPrice}")


def searchGame(gameName):
    """Search for a game, add it if not in database, update price history"""
    # First, search Steam for the game info
    gameinfo = search_games(gameName)
    if not gameinfo:
        print("Game not found on Steam")
        return None

    steamAppId = gameinfo['id']
    
    # Check if it's a free game
    if gameinfo['isFree']:
        # Check if free game already exists
        sql_check = "SELECT * FROM FREEGAMES WHERE STEAMAPPID = :id"
        cur.execute(sql_check, {"id": steamAppId})
        row = cur.fetchone()
        
        if row:
            print(f"{gameinfo['gamename']} (free) already in DB")
            columns = ["id", "gamename", "url", "rating", "genre", "releaseDate", "description", "image"]
            gameDict = dict(zip(columns, row))
            gameDict['isFree'] = True
            return gameDict
        else:
            print(f"{gameinfo['gamename']} (free) not in DB, adding now...")
            return addFreeGame(gameinfo)
    else:
        # Paid game - check if it exists in GAME table
        sql_check = "SELECT * FROM GAME WHERE STEAMAPPID = :id"
        cur.execute(sql_check, {"id": steamAppId})
        row = cur.fetchone()
        
        if row:
            print(f"{gameinfo['gamename']} already in DB")
            columns = ["id", "gamename", "url", "initialPrice", "currentPrice",
                      "rating", "genre", "releaseDate", "description", "image"]
            gameDict = dict(zip(columns, row))
            gameDict['isFree'] = False
            
            # Update price history with current prices
            updatePriceHistory(steamAppId, gameDict['initialPrice'], gameinfo['currentPrice'])
            
            return gameDict
        else:
            print(f"{gameinfo['gamename']} not in DB, adding now...")
            result = addPaidGame(gameinfo)
            
            # Create initial price history entry
            updatePriceHistory(steamAppId, gameinfo['initialPrice'], gameinfo['currentPrice'])
            
            return result

    
if __name__ == "__main__":
    try:
        # Test with a free game
        print("Testing with Dota 2 (free):")
        print(searchGame("dota 2"))
        print("\n" + "="*50 + "\n")
        
        # Test with a paid game
        print("Testing with Undertale (paid):")
        print(searchGame("undertale"))
    finally:
        cur.close()
        con.close()