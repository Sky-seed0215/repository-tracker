import requests

url = "https://api.github.com/repos/CinnamonSea2073/CinnamonBot/issues/15"

r = requests.get(url=url)

rr = r.json()

print(rr["title"])
