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
        assembly = request.json['conversation']['memory']['assembly']['value']
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

@app.route('/orderNo/<OrderNo>', methods = ['GET'])
def orderNo(OrderNo):
    OrderNo = '00000' + str(OrderNo)
    hdr = {'Authorization': 'Basic cm5haXJhbmQ6ZmQ0Njg4NQ=='}
    url = 'https://appsnadevtest.apimanagement.hana.ondemand.com:443/ZFD4_INSP_REPORT_SRV'
    url = url + '/InspectionReportSet'
    url = url + '?$filter=Orderno%20eq%20%27' + OrderNo + '%27&$format=json'

    r = requests.get(url, headers = hdr)
    if r.status_code != 200:
        reply = 'Did not get any reply from SAP...'
        print(reply)
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
        url = 'https://e1438a78.ngrok.io/startkit'
        reponse = requests.post(url, data=json.dumps(payload))

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