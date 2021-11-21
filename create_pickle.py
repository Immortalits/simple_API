import json
import pickle

f = open('projects.json', )

data = json.load(f)

#data[projects]

with open("projects.pickle", "wb") as fajl:
    #kiírja az adatokat egy fájlba
    pickle.dump(data, fajl)

f.close()
