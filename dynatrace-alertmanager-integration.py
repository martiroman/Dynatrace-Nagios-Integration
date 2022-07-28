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
from flask import Flask, request, Response
import DynatraceApp
import AlertManagerApp

SERVER='10.250.1.102'
PORT=5999

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
        

        return Response('Alerts received', status=200)
    else:
        return Response('Error request', status=400)

if __name__ == '__main__':
    app.run(debug=True, host=SERVER, port=PORT)
