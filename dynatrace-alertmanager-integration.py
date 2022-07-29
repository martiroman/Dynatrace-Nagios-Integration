#!/usr/bin/env python
"""
Dynatrace + Alertmanager Integration

AlertManager Configuration:
- name: 'dynatrace-receiver'
    webhook_configs:
    - sends_resolved: true
      url: 'http://10.250.1.102:5999/notification'
"""

import sys
import json
from flask import Flask, request, Response
import App.DynatraceApp as Dyna
import App.AlertManagerApp as Alert

with open('config.json', 'r') as file: config = json.load(file)

lstEvents = []
DynaConn = Dyna.Connection(config["DYNATRACE"]["API_URL"], config["DYNATRACE"]["API_TOKEN"])

app = Flask(__name__)

@app.route('/', methods=['POST'])

def HomeResponse():
    return 'Webhook AlertManager Notifications'

@app.route('/notification', methods=['POST'])


def webhook():
    print("\n\n *Alert Notification - Received")
    sys.stdout.flush()

    if request.method == 'POST':
        data = request.json
        for alert in data['alerts']:
            print(alert['status'])
            print(alert['labels']['alertname'])
            print(alert['labels']['instance'])
            print(alert['labels']['severity'])
            print(alert['labels']['job'])
            sys.stdout.flush()
            
        return Response('Alerts received', status=200)
    else:
        return Response('Error request', status=400)

def checkIfEvent(hostName, serviceName, state):
        encontrado = False

        for event in lstEvents:
            if DynaConn.CompareEvents(event, serviceName, hostName):
                encontrado = True

        if encontrado == True:
            if state == "resolved":
                print("eliminar evento")
        else:
            if state == "firing":   
                oEvent = DynaConn.addEvent("CUSTOM_ALERT", serviceName, hostName)
                lstEvents.append(oEvent)

if __name__ == '__main__':
    app.run(debug=True, host=SERVER, port=PORT)
