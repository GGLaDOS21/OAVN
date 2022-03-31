import json


with open ("states.json") as stat:
    data = json.load(stat)

    for i in data["states"]:
        print(i)

dict1 ={

    "name": "Lisa",
    "designation": "programmer",
    "age": "34",
    "salary": "54000"


}

with open("myjs.json","w") as out:
    json.dump(dict1, out, indent="")

jdict = json.dumps(dict1, indent="")

print(jdict)

sortdict= sorted(dict1)

jdict2 = json.dumps(sortdict, indent=4)

print(jdict2)

with open ("states.json") as stat:
    data = json.load(stat)
    newStates=[]
    for i in data["states"]:
        state={"name": i["name"], "abbreviation" : i["abbreviation"]}
        newStates.append(state)
    statesDict={"States" : newStates}
    print(statesDict)
    with open("states_no_area.json", "w") as out:
        json.dump(statesDict,out, indent= 2)


