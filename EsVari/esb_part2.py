import json

#def decode_states(dt):



with open ("states.json") as stat:
    data = stat.read()
    states = json.load(data)