# Dynatrace Integrations

## Integracion Nagios

    * Consumo de metricas de la perfData de Nagios
    * Envio de Alertas de Nagios

> dynatrace-nagios-integration.py

## Integracion AlertManager

    * Webhook para recibir alertas desde Prometheus

> dynatrace-alertmanager-integration.py

## Configuracion

> vim /etc/dynatrace-integrations/config.json

```json
{
    "DYNATRACE": {
        "API_URL" : "http://xxx.dynatrace.xxx",
        "API_TOKEN" : "xxxxxxxxxxxxxxxxxx"
    },
    "NAGIOS": {
        "NAGIOS_SOCKET" : "/usr/local/nagios/var/rw/nagios.qh",
        "HOST_WHITELIST" :  false,
        "SERVICE_WHITELIST" :  false
    },
    "ALERTMANAGER": {
        "SERVER" : "xx.xx.xx.xx",
        "PORT" : 9999
    }
 }
```