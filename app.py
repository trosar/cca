#!/usr/bin/env python

import requests
import urllib
import json
import os
import re

from flask import Flask
from flask import request
from flask import make_response
from datetime import datetime as DateTime, timedelta as TimeDelta


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
    if req.get("result").get("action") == "browse.search.products":
        result = req.get("result")
        parameters = result.get("parameters")
        color = parameters.get("color")
        cat = parameters.get("catalog-category")
        if (((color is None) or (color is "")) and (req.get("originalRequest") is not None) and (req.get("originalRequest").get("source") == "facebook")):
            return {
                "data": {
                    "facebook": {
                        "text": "Pick a color:",
                        "quick_replies": [
                            {
                                "content_type": "text",
                                "title": "Red",
                                "payload": "red"
                            },
                            {
                                "content_type": "text",
                                "title": "Green",
                                "payload": "green"
                            }
                        ]
                    }
                }
            }
        else:
            rq = requests.get("http://www.lanebryant.com/lanebryant/search?Ntt=" + color + " " + cat + "&format=JSON")
            jdata = json.loads(rq.text)
            speech = "I found " + str(jdata["contents"][0]["MainContent"][0]["MainContent"][0]["contents"][0]["totalNumRecs"]) + " " + color + " " + cat + " products." 
    elif req.get("result").get("action") == "promos":
        result = req.get("result")
        headers = {'HOST': 'sit.catherines.com'}
        rq = requests.get("https://23.34.4.174/static/promo_01?format=json", headers=headers, verify=False)
        jdata = json.loads(rq.text)
        speech = "Promos are "
        for mc in jdata["MainContent"]:
            speech = speech + str(mc["freeFormContent"]) + "... "
    elif ((req.get("result").get("action") == "Order_Status_yes") or (req.get("result").get("action") == "checkout.order.status")):
        result = req.get("result")
        parameters = result.get("parameters")
        zipcode = parameters.get("zipcode")
        ordernum = parameters.get("order-number")
        
        rq = requests.post("https://www.shopjustice.com/justice/homepage/includes/order-response-html.jsp", data={'orderNum': ordernum, 'billingZip': zipcode, 'Action': 'fetchODDetails'})
        #print rq.text
        matchObj = rq.text[rq.text.find("mar-status")+12:rq.text.find("<", rq.text.find("mar-status"))]
        matchDate = rq.text[rq.text.find("mar-date")+12:rq.text.find("<", rq.text.find("mar-date"))]
        if len(matchObj) < 50:
            status = matchObj
            date = DateTime.strptime(matchDate, '%m-%d-%Y') + TimeDelta(days=5)
            print ("matchObj : ", matchObj)
            print ("matchDate : ", matchDate)
        else:
            status = "Not available"
            print ("No match!!")
            
        if status == 'Shipped':
            speech = "Order status is " + status + ". You shall receive the package by " + date + "."
        else:
            speech = "Order status is " + status + "."
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

    print ("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
