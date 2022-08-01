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

#ERROR SI NO ENCUENTRA EL ARCHIVO
with open('/etc/dynatrace-integrations/config.json', 'r') as file: config = json.load(file)

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
            
            host = alert['labels']['instance'].split(":")[0]
            alertName = alert['labels']['alertname']
            statusError = False
            if alert['status'] != "resolved":
                statusError = True

            DynaConn.checkIsEvent(host, alertName, statusError)

            sys.stdout.flush()
            
            DynaConn.sendEvents()

        return Response('Alerts received', status=200)
    else:
        return Response('Error request', status=400)

if __name__ == '__main__':
    app.run(debug=True, host=config["ALERTMANAGER"]["SERVER"], port=config["ALERTMANAGER"]["PORT"])
