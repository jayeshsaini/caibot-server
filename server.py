from flask import Flask, request, jsonify
import json
import os
import requests
import time
from datetime import datetime, timedelta

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def index():
    return "<h2>SAP Conversational AI Agent<h2>"

#Inspection Report - Assembly
@app.route('/count_assembly', methods=['POST'])
def count_assembly():
    if request.method == 'POST':
        print(request.json)
        assembly = request.json["conversation"]["memory"]["assembly"]["raw"]
        time = request.json["nlp"]["entities"]["time-period"][0]["value"]
        date = request.json["nlp"]["timestamp"]
    if assembly == "Perfect" or assembly == "perfect" or assembly == "Ok" or assembly == "ok":
        assembly = 'Ok'
    elif assembly == "Missing" or assembly == "missing":
        assembly = 'Missing'
    elif assembly == "Misaligned" or assembly == "misaligned":
        assembly = "Misaligned"

    formatdate = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f+00:00')

    reply = "Didn't find any data for this type in backend"

    switches = ""

    hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
    url = "https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZFD4_INSP_RESULT_SRV/InspectionSet"
    
    if assembly == "Ok" or assembly == "Missing" or assembly == "Misaligned":
        if time == "all":
            url = url + "/$count?$filter=Assembly eq '" + assembly + "'"

            r = requests.get(url, headers = hdr)
            if r.status_code != 200:
                reply = 'Did not get any reply from SAP...'
            else:
                switches = str(r.content, 'utf-8')
                
        elif time =="today":
            todaydate = datetime.strftime(formatdate, '%Y-%m-%dT00:00:00')
            url = url + "/$count?$filter=Assembly eq '" + assembly + "' and Crdate eq datetime'" + todaydate + "'"

            r = requests.get(url, headers = hdr)
            if r.status_code != 200:
                reply = 'Did not get any reply from SAP...'
            else:
                switches = str(r.content, 'utf-8')

        elif time =="yesterday":
            formatdate = formatdate - timedelta(days=1)
            todaydate = datetime.strftime(formatdate, '%Y-%m-%dT00:00:00')
            url = url + "/$count?$filter=Assembly eq '" + assembly + "' and Crdate eq datetime'" + todaydate + "'"

            r = requests.get(url, headers = hdr)
            if r.status_code != 200:
                reply = 'Did not get any reply from SAP...'
            else:
                switches = str(r.content, 'utf-8')

        elif time =="last week":
            formatdate = formatdate - timedelta(days=7)
            todaydate = datetime.strftime(formatdate, '%Y-%m-%dT00:00:00')
            url = url + "/$count?$filter=Assembly eq '" + assembly + "' and Crdate eq datetime'" + todaydate + "'"

            r = requests.get(url, headers = hdr)
            if r.status_code != 200:
                reply = 'Did not get any reply from SAP...'
            else:
                switches = str(r.content, 'utf-8')

        elif time =="last month":
            formatdate = formatdate - timedelta(days=30)
            todaydate = datetime.strftime(formatdate, '%Y-%m-%dT00:00:00')
            url = url + "/$count?$filter=Assembly eq '" + assembly + "' and Crdate eq datetime'" + todaydate + "'"

            r = requests.get(url, headers = hdr)
            if r.status_code != 200:
                reply = 'Did not get any reply from SAP...'
            else:
                switches = str(r.content, 'utf-8')
        
    if switches != "":
        if assembly == "Ok":
            reply = 'There are ' + switches + ' switches with perfectly aligned gaskets'
        elif assembly == "Misaligned":
            reply = switches + ' switches have gaskets misaligned'
        elif assembly == "Missing":
            reply = switches + ' switches have gaskets missing'
        print(reply)    

    return jsonify(
        status = 200,
        replies = [
            {
                'type': 'text',
                'content': reply
                }
            ]
        )

#Production Order details
@app.route('/orderNo', methods = ['POST'])
def orderNo():
    req = json.loads(request.get_data())
    OrderNo = req["nlp"]["source"]

    OrderNo = '00000' + str(OrderNo)
    hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
    url = "https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZFD4_INSP_REPORT_SRV/InspectionReportSet"
    url = url + "?$filter=Orderno eq '" + OrderNo + "'&$format=json"

    r = requests.get(url, headers = hdr)
    result = json.loads(r.content)

    if r.status_code != 200:
        reply = "Cannot reach backend. Kindly check your S/4 HANA system."
    elif result['d']['results'][0]=="":
        reply = 'Sorry, I don\'t think that is a valid Order No'
    else:
        result = json.loads(r.content)
        temp = result['d']['results'][0]
        temp = dict(temp)
        Qty = str(temp.get('Qty'))
        Yield = str(temp.get('Yield'))
        Scrap = str(temp.get('Scrap'))

        reply = "Qty: " + Qty + "\nYield: " + Yield + "\nScrap: " + Scrap
        print(reply)

    return jsonify(
        status = 200,
        replies = [
            {
                'type': 'text',
                'content': reply
                }
            ]
        )

#Plant Maintenance Order details
@app.route('/PMOrder', methods = ['POST'])          
def PMOrder():
    req = json.loads(request.get_data())
    Status = req["nlp"]["source"]
    if Status == "Open":
        Status = 'OPEN'
    elif Status == "Close":
        Status = 'CLOSE'
        
    url = "https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZGW_CREATE_PMO_SRV/WorkOrderSet"
    url = url + "?$filter=Response eq '" + Status + "'&$format=json&$orderby=WoNum desc"

    hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
    r = requests.get(url, headers = hdr)

    if r.status_code != 200:
            reply = "Sorry, Wrong input"
    else:
        response = json.loads(r.content)
        data = response['d']['results'][0]
        WoNum = data.get('WoNum')
        WoDate = data.get('WoCreateDate')
        WoDate = WoDate[6:]
        WoDate = int(WoDate[:10])
        WoDate = time.ctime(WoDate)
        desc = data.get('ShortDesc')
        plant = data.get('Plant')
        reply = 'Plant Maintenance Order: ' + WoNum + ', Created on: ' + WoDate + ', Plant: ' + plant + ', Reason: ' + desc
        
        return jsonify(
            status = 200,
            replies = [
            {
                'type': 'text',
                'content': reply
                }
            ]
        )

@app.route('/fan-fail', methods = ['POST'])
def startkit():
    if request.method == 'POST':
        print(request.json)
        kit = request.json['nlp']['entities']['fan'][0]['raw']
    if kit == "primary fan" or kit == 'fan':
        reply = 'fan'


    payload = {
        'text': 'fan'
    }
    url = 'https://fastdigital.localtunnel.me/fan-fail'
    headers = {'Content-Type': 'application/json'}
        
    reponse = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)

    if reponse.status_code == 200:
        reply = 'Primary Fan is off'
    else:
        reply = 'Kit is not connected. Please check and try again.'
    
    print(reply)

    return jsonify(
        status = 200,
        replies = [
            {
                'type': 'text',
                'content': reply
                }
            ]
        )

app.run(port=port, host="0.0.0.0")
