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

            detailsUrl = f"https://store.steampowered.com/api/appdetails?appids={item['id']}"
            details = requests.get(detailsUrl)

            if details.status_code != 200:
                print('didnt get game info')
                return
            data = details.json()
            print(json.dumps(data, indent=4))


        
    

    else:
        print(f"error: {response.status_code}") #incase the request fails
        return []

if __name__ == "__main__":
    search_games("Undertale")
