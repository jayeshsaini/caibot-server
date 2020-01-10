from flask import Flask, request, jsonify
import json
import os
import requests
import time

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

@app.route('/')
def index():
    return "<h2>SAP Conversational AI Agent<h2>"

@app.route('/count_assembly', methods=['POST'])
def count_assembly():
    if request.method == 'POST':
        print(request.json)
        assembly = request.json["nlp"]["source"]
    if assembly == "Perfect" or assembly == "perfect" or assembly == "Ok" or assembly == "ok":
        assembly = 'Ok'
    elif assembly == "Missing" or assembly == "missing":
        assembly = 'Missing'
    elif assembly == "Misaligned" or assembly == "misaligned":
        assembly = "Misaligned"

    if assembly == "Ok" or assembly == "Missing" or assembly == "Misaligned":
        hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
        url = 'https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZFD4_INSP_RESULT_SRV'
        url = url + '/InspectionSet'
        url = url + '/$count?$filter=Assembly%20eq%20%27' + assembly + '%27'

        r = requests.get(url, headers = hdr)
        if r.status_code != 200:
            reply = 'Did not get any reply from SAP...'
        else:
            switches = str(r.content, 'utf-8')
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

@app.route('/orderNo', methods = ['POST'])
def orderNo(OrderNo):
    OrderNo = '00000' + str(OrderNo)
    hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
    url = 'https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZFD4_INSP_REPORT_SRV'
    url = url + '/InspectionReportSet'
    url = url + '?$filter=Orderno%20eq%20%27' + OrderNo + '%27&$format=json'

    r = requests.get(url, headers = hdr)
    if r.status_code != 200:
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

@app.route('/PMOrder', methods = ['POST'])
def PMOrder():
    req = json.loads(request.get_data())
    Status = req["nlp"]["source"]
    if Status == "Open":
        Status = 'OPEN'
    elif Status == "Close":
        Status = 'CLOSE'
        
    url = 'https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZGW_CREATE_PMO_SRV'
    url = url + '/WorkOrderSet'
    url = url + '?$filter=Response%20eq%20%27' + Status + '%27&$format=json&$orderby=WoNum%20desc'

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

@app.route('/startkit', methods = ['POST'])
def startkit():
    if request.method == 'POST':
        print(request.json)
        print(type(request.json))
        kit = request.json['nlp']['entities']['kit'][0]['raw']
    if kit == "Visual Inspection":
        reply = 'VisualInspection'
    elif kit == "Smart Asset Monitoring":
        reply = 'Smart Asset Monitoring'

        payload = {
            'text': 'Smart Asset Monitoring'
        }
        url = 'https://fastdigital.localtunnel.me/startkit'
        headers = {'Content-Type': 'application/json'}
        
        reponse = requests.post(url, data=json.dumps(payload), headers=headers)

        if reponse.status_code == 200:
            reply = 'Started Kit'


    elif kit == "Connected Manufacting":
        reply = 'cm'

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