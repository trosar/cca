#!/usr/bin/env python

import requests
import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeWebhookResult(req):
    if req.get("result").get("action") != "search.items":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    color = parameters.get("color")
    cat = parameters.get("catalog-category")

    rq = requests.get("http://www.lanebryant.com/lanebryant/search?Ntt=" + color + " " + cat + "&format=JSON")
    jdata = json.loads(rq.text)

    speech = "I found " + str(jdata["contents"][0]["MainContent"][0]["MainContent"][0]["contents"][0]["totalNumRecs"]) + " " + color + " " + cat + " products." 

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-search"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
