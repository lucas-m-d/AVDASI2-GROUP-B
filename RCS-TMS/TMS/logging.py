from flask import jsonify
import json

def getData(data_list):
    response = []

    for data in data_list:
        keys = {}
        for key in data.schema:
            keys[key] = getattr(data, key)

        response.append({"time":data.time, "data":keys})
    print(response)
    return jsonify(response)