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
        
        if ((req.get("originalRequest") is not None) and (req.get("originalRequest").get("source") == "facebook")):
            return{
                "data": {
                    "facebook": {
                        "attachment": {
                            "type": "template",
                            "payload": {
                                "template_type": "list",
                                "elements": [{
                                    "title": "LaneBryant Active Promotions",
                                    "image_url": "https://xvir.github.io/img/apiai.png",
                                    "default_action": {
                                        "type": "web_url",
                                        "url": "http://www.lanebryant.com/"
                                    }
                                },
                                {
                                    "title": str(jdata["MainContent"][0]["freeFormContent"]),
                                    "image_url": "https://xvir.github.io/img/apiai.png",
                                    "default_action": {
                                        "type": "web_url",
                                        "url": "http://www.lanebryant.com/"
                                    }
                                },
                                {
                                    "title": str(jdata["MainContent"][1]["freeFormContent"]),
                                    "image_url": "https://xvir.github.io/img/apiai.png",
                                    "default_action": {
                                        "type": "web_url",
                                        "url": "http://www.lanebryant.com/"
                                    }
                                },
                                {
                                    "title": str(jdata["MainContent"][2]["freeFormContent"]),
                                    "image_url": "https://xvir.github.io/img/apiai.png",
                                    "default_action": {
                                        "type": "web_url",
                                        "url": "www.lanebryant.com"
                                    }
                                }]
                            }
                        }
                    }
                }
            }
        else:    
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
        matchDate = rq.text[rq.text.find("mar-date")+10:rq.text.find("<", rq.text.find("mar-date"))]
        date = DateTime.now()
        present = DateTime.now()
        
        if len(matchObj) < 50:
            print ("matchObj : ", matchObj)
            print ("matchDate : ", matchDate)
            status = matchObj
            date = DateTime.strptime(matchDate, '%m/%d/%Y') + TimeDelta(days=5)
        else:
            status = "I couldn't find that order. Either the number or the zipcode is not correct."
            print ("No match!!")
            
        if date >= present:
            if status == 'Shipped':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Partially Shipped':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Canceled':
                speech = "Order status is " + status + ". Please reach out to the customer support for more details about the order."
            elif status == 'Processing':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            else:
                speech = status
        else:
            if status == 'Shipped':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Partially Shipped':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Canceled':
                speech = "Order status is " + status + ". Please reach out to the customer support for more details about the order."
            elif status == 'Processing':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            else:
                speech = status
    elif req.get("result").get("action") == "Order_Status_no":
        result = req.get("result")
        parameters = result.get("parameters")
        zipcode = parameters.get("zipcode")
        email = parameters.get("email")
        ordertime = parameters.get("order-time")
        
        #TODO - Need to put here the API to get order number using email, zipcode and the timeframe
        if zipcode == '20166':
            ordernum = 'OJTW022967052'
        elif zipcode == '37122':
            ordernum = 'OJTW027567667'
        elif zipcode == '19148':
            ordernum = 'OJTW027678055'
        else:
            ordernum = 'OJTW022967052'
            
        rq = requests.post("https://www.shopjustice.com/justice/homepage/includes/order-response-html.jsp", data={'orderNum': ordernum, 'billingZip': zipcode, 'Action': 'fetchODDetails'})
        #print rq.text
        matchObj = rq.text[rq.text.find("mar-status")+12:rq.text.find("<", rq.text.find("mar-status"))]
        matchDate = rq.text[rq.text.find("mar-date")+10:rq.text.find("<", rq.text.find("mar-date"))]
        date = DateTime.now()
        present = DateTime.now()
        
        if len(matchObj) < 50:
            print ("matchObj : ", matchObj)
            print ("matchDate : ", matchDate)
            status = matchObj
            date = DateTime.strptime(matchDate, '%m/%d/%Y') + TimeDelta(days=5)
        else:
            status = "I couldn't find that order. Either the order number or the zipcode is not correct."
            print ("No match!!")
        
        if date >= present:
            if status == 'Shipped':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Partially Shipped':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Canceled':
                speech = "Order status is " + status + ". Please reach out to the customer support for more details about the order."
            elif status == 'Processing':
                speech = "Order status is " + status + ". You should receive the package by " + date.strftime('%m/%d/%Y') + "."
            else:
                speech = status
        else:
            if status == 'Shipped':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Partially Shipped':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            elif status == 'Canceled':
                speech = "Order status is " + status + ". Please reach out to the customer support for more details about the order."
            elif status == 'Processing':
                speech = "Order status is " + status + ". You should have received the package by " + date.strftime('%m/%d/%Y') + "."
            else:
                speech = status
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
