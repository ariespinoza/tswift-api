import requests, json
BASE = "https://tswift-api.onrender.com"

print("Root:", requests.get(f"{BASE}/").json())
print("Albums first:", requests.get(f"{BASE}/albums").json()[:1])

print("Favs initial:", requests.get(f"{BASE}/favorites").json())

new = {
  "name":"1989","artist":"Taylor Swift","favoriteSong":"Blank Space",
  "listenCompleted":True,"commented":True,"comment":"Top!"
}
created = requests.post(f"{BASE}/favorites", json=new).json()
print("Created:", created)

fid = created["id"]
updated = requests.patch(f"{BASE}/favorites/{fid}", json={"comment":"Re-escuchar deluxe"}).json()
print("Patched:", updated)

print("Delete:", requests.delete(f"{BASE}/favorites/{fid}").json())
print("Favs final:", requests.get(f"{BASE}/favorites").json())
