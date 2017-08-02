#!/usr/bin/env python

import requests
import urllib
import json
import os
import re

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
    if req.get("result").get("action") == "search.items":
        result = req.get("result")
        parameters = result.get("parameters")
        color = parameters.get("color")
        cat = parameters.get("catalog-category")

        rq = requests.get("http://www.lanebryant.com/lanebryant/search?Ntt=" + color + " " + cat + "&format=JSON")
        jdata = json.loads(rq.text)
        speech = "I found " + str(jdata["contents"][0]["MainContent"][0]["MainContent"][0]["contents"][0]["totalNumRecs"]) + " " + color + " " + cat + " products." 
    elif req.get("result").get("action") == "some.else":
        result = req.get("result")
        parameters = result.get("parameters")
        zipcode = parameters.get("zipcode")
        ordernum = parameters.get("order-number")
        
        rq = requests.get("https://www.shopjustice.com/justice/homepage/includes/order-response-html.jsp?orderNum=" + ordernum + "&billingZip=" + zipcode + "&Action=fetchODDetails")
        #matchObj = re.match( r'.*<span class="mar-status">(.*?)<\/span>.*', rq.text, re.M|re.I)
        matchObj = rr.text[rq.text.find("mar-status")+12:rq.text.find("<", rq.text.find("mar-status"))]
        #print rq.text
        #matchObj = re.match( r'.*<span class="mar-status">(.*?)<\/span>.*', rq.text, re.M|re.I)
        matchObj = r.text[r.text.find("mar-status")+12:r.text.find("<", r.text.find("mar-status"))]
        #print rq.text
        status = "Not available"
        if len(matchObj) < 50:
            status = matchObj
            print "matchObj : ", matchObj
        else:
            print "No match!!"
        speech = "Order status is " + status
    else:
        return{}
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
