from flask import Flask, jsonify, request # type: ignore
import json
from TMS.logging import *
from datarefs import DataRef ## dataRef is a customisable list of data that is being tracked
from dotenv import load_dotenv
import os

# set up with ports
load_dotenv()
PORT = os.getenv("RCSTMS_PORT")

app = Flask(__name__)

# for now
dataList = [DataRef(time=12345678, flapLeft=0.5)]

# set up app routings
@app.route('/data', methods=['GET'])
def httpGetData():
    return getData(dataList)


if __name__ == '__main__':
   app.run(port=PORT)


