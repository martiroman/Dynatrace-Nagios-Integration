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

#TODO: GET events Dynatrace y quitar la lista

#ERROR SI NO ENCUENTRA EL ARCHIVO
with open('/etc/dynatrace-integrations/config.json', 'r') as file: config = json.load(file)

DynaConn = Dyna.Connection(config["DYNATRACE"]["API_URL"], config["DYNATRACE"]["API_TOKEN"])

app = Flask(__name__)

@app.route('/', methods=['GET'])

def HomeResponse():
    return 'Webhook Dynatrace Notifications'

@app.route('/api/v2/alerts', methods=['POST'])


def webhook():
    print(request.json)
    print("\n\n * Alert Notification - Received")
    sys.stdout.flush()

    if request.method == 'POST':
        data = request.json

        for alert in data:

            host = alert['labels']['instance'].split(":")[0]
            alertName = alert['labels']['alertname']
            statusError = False
            if alert['labels']['severity'] != "resolved":
                statusError = True

            DynaConn.checkIsEvent(host, alertName, statusError)

            DynaConn.sendEvents()
        #print("\n\n")
        #print(data)
        #sys.stdout.flush()

        #return Response('Alerts received', status=200)
        return 'Alerts received', 200
    else:
        return Response('Error request', status=400)
