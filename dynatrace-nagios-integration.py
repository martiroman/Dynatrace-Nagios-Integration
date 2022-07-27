#!/usr/bin/env python
"""
Integracion Nagios-Dynatrace:
Consulta los datos de hosts de Nagios a traves de MK-Livestatus y envia las metricas a Dynatrace creando el CUSTOM DEVICE
en caso de no existir

TODO: Creacion de metricas descubiertas en un host de Nagios

Dynatrace Type Events:
    AVAILABILITY_EVENT
    CUSTOM_ALERT
    CUSTOM_ANNOTATION
    CUSTOM_CONFIGURATION
    CUSTOM_DEPLOYMENT
    CUSTOM_INFO
    ERROR_EVENT
    MARKED_FOR_TERMINATION
    PERFORMANCE_EVENT
    RESOURCE_CONTENTION_EVENT
"""

import time
import sched

import DynatraceApp
import NagiosApp
import IntegrationErrors

#####CONFIGURACION############################################################################################################
DT_API_URL = CONFIGURAR
DT_API_TOKEN = CONFIGURAR
NAGIOS_SOCKET = '/usr/local/nagios/var/rw/nagios.qh'
HOST_WHITELIST =  False #o ['host1','host2'...]
SERVICE_WHITELIST = False #o ['service1','service2'...]

#####CLASES###################################################################################################################

class Integracion(object):
    def __init__(self):
        self.NagiosConn = Nagios.Connection()
        self.DynaConn = DynatraceConnection()
        self.lstHosts = []

    def CargarHosts(self):
        '''Obtiene el listado de hosts a monitorear'''
        tmpHosts = self.NagiosConn.getHosts()
        if HOST_WHITELIST:
            for naghost in tmpHosts:
                if naghost["name"] in HOST_WHITELIST:
                    self.lstHosts.append(naghost)
        else:
            self.lstHosts = tmpHosts

    def CargarMetricas(self):
        '''Crea el Custom Host y le asocia cada una de las metricas'''
        favicon = "http://assets.dynatrace.com/global/icons/infographic_rack.png"
        lstServices = []

        for host in self.lstHosts:
            #TODO: Configurar puertos del host
            dHost = self.DynaConn.addCustomHost(host['name'], host['address'], ['80','8080','443','8428','9100','9104','53862','53852'], 'Nagios', favicon, '', host['groups'][0])
            dHost.addTag(host['groups'])
            lstTmpServices = self.NagiosConn.getMetricas(host['name'])
            
            if SERVICE_WHITELIST:
                for nagServ in lstTmpServices:
                    if nagServ["service_description"] in SERVICE_WHITELIST:
                        lstServices.append(nagServ)
            else:
                lstServices = lstTmpServices
            
            for service in lstServices:
                self.DynaConn.checkIfEvent(dHost.displayName, service["description"], service["state"])
                lstMetricas = self.NagiosConn.parsePerfData(service["perf_data"])
                for metrica in lstMetricas:
                    dHost.addSerie(service["description"], metrica, lstMetricas[metrica][0])

    def EnviarMetricas(self):
        '''Eviar los datos a Dynatrace'''
        self.DynaConn.sendMetrics()

    def EnviarEventos(self):
        '''Eviar los eventos a Dynatrace'''
        self.DynaConn.sendEvents()

#####MAIN###############################################################################################################
oInteg = Integracion()
s = sched.scheduler(time.time, time.sleep)

def programa(start, end, interval, func, args=()):
    event_time = start
    while event_time < end:
        s.enterabs(event_time, 0, func, args)
        event_time += interval

    s.run()

def service_integration():
    oInteg.CargarMetricas()
    oInteg.EnviarMetricas()
    oInteg.EnviarEventos()


def main():
    try:
        oInteg.CargarHosts()

        print("Inicio - Recoleccion de Metricas de Nagios")

        #Ajustar los tiempos (+100000 1 dia)
        programa(time.time()+5, time.time()+100000, 90, service_integration)

    except IntegrationErrors.NagiosToDynaError as err:
        print(err)

if __name__ == '__main__':
    main()