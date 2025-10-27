import requests
import json

#function to return an json of the steam game
#this will later be used in other functions this was just a test 
def search_games(gameName):
    url = f"https://store.steampowered.com/api/storesearch?term={gameName}&l=english&cc=US"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("items",[])

        print(f"results for {gameName}:")
        for item in items[:1]:              #edit this line if you want to change how many results you get btw
            print(f"    app id: {item}")
        
        return items

    else:
        print(f"error: {response.status_code}") #incase the request fails
        return []

if __name__ == "__main__":
    search_games("Witcher 3")
    search_games("factorio")
    search_games("scrimblo bimblo 999")