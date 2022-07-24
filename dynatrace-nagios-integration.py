#!/usr/bin/env python
"""
Integracion Nagios-Dynatrace:
Consulta los datos de hosts de Nagios a traves de MK-Livestatus y envia las metricas a Dynatrace creando el CUSTOM DEVICE
en caso de no existir

TODO: Envio de problems por alerta a activa en Nagios
TODO: Creacion de metricas descubiertas en un host de Nagios

"""
import re
import datetime
import json
import time
import requests

#https://github.com/arthru/python-mk-livestatus
from mk_livestatus import Socket

#####CONFIGURACION############################################################################################################
DT_API_URL = CONFIGURAR
DT_API_TOKEN = CONFIGURAR
NAGIOS_SOCKET = '/usr/local/nagios/var/rw/nagios.qh'
HOST_WHITELIST =  False #o ['host1','host2'...]
SERVICE_WHITELIST = False #o ['service1','service2'...]

#####CLASES###################################################################################################################
class NagiosConnection(object):
    """Realiza las querys al socket de Nagios"""
    def __init__(self):
        try:
            self._sock = Socket(NAGIOS_SOCKET)
        except Exception as err:
            raise NagiosToDynaConnectError(err)
        
    def getHosts(self):
        '''Realiza la query para obtener los hosts'''
        try:
            q = self._sock.hosts.columns('name', 'alias', 'address', 'groups')
            return q.call() 
        except Exception as err:
            raise NagiosToDynaQueryError(err)

    def getMetricas(self, hostname):
        '''Realiza la query para obtener los servicios y cada una de las metricas'''
        try:
            q = self._sock.services.columns('service_description', 'state', 'latency', 'perf_data',
                                            'process_performance_data', 'check_command', 'acknowledged','execution_time', 
                                            'is_flapping').filter('host_name = ' + hostname)
            return q.call()
        except Exception as err:
            raise NagiosToDynaQueryError(err)

    def parsePerfData(self, perfData):
        '''Parsea la PerfData de los Services de Nagios'''
        campos = {}
        for raw in perfData.split(" "):
            metrica = raw.split('=')
            nombre = metrica[0]
            datos = metrica[1].split(';')
            
            valorMetricaSinFormato = re.compile('([0-9.]+)([^0-9.]+)?').match(datos[0])
            if not valorMetricaSinFormato:
                 valorMetrica = datos[0]
                 unidad = ''
            else:
                valor, unidad = valorMetricaSinFormato.groups('')
            
            datos[0] = valor
            datos.append(unidad)
            campos[nombre] = datos
        return campos

class NagiosToDynaError(Exception):
    """Errores de la integracion"""

class NagiosToDynaQueryError(NagiosToDynaError):
    """Fallo en la query al socket"""

class NagiosToDynaConnectError(NagiosToDynaError):
    """Error de conexion al socket"""

##Clases Dynatrace
class DataPoint(object):
    def __init__(self, tiempo, valor):
        self.timestamp = int(time.mktime(tiempo.timetuple()) * 1000)
        self.valor = valor

    #TODO: Si no es valor numerico
    def formatDataPoint(self):
        return [self.timestamp, float(self.valor)]

class Serie(object):
    def __init__(self, ServiceName, dimensions):
        self.timeseriesId = 'custom:host.service.' + ServiceName.replace(" ", "").lower()
        self.dimensions = { 'metrica' : dimensions }
        self.dataPoints = []
    
    def addDataPoint(self, tiempo, valor):
        dp = DataPoint(tiempo, valor)
        self.dataPoints.append(dp.formatDataPoint())
                        
class CustomHost(object):
    def __init__(self, displayName, ipAdresses, listenPorts, type, favicon, configUrl):
        self.displayName = displayName
        self.ipAdresses = [ipAdresses]
        self.listenPorts = [listenPorts]
        self.type = type
        self.favicon = favicon
        self.configUrl = configUrl
        self.series = []
        
    def addSerie(self, servicename, metrica, valor):
        dt = datetime.datetime.now()
        serie = Serie(servicename, metrica)
        serie.addDataPoint(dt, valor)
        self.series.append(serie)

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class DynatraceConnection(object):
    def __init__(self):
        self.lstHost = []

    def addCustomHost(self, name, address, puerto, type, favicon, configUrl):
        dHost = CustomHost(name, address, puerto, type, favicon, configUrl)
        self.lstHost.append(dHost)
        return dHost

    def createMetric():
        #TODO: Crear metrica en Dyna
        '''Pendiente'''
    
    def sendProblems():
        #TODO: Crear problem en Dyna
        '''Pendiente'''

    def sendMetrics(self):
        for host in self.lstHost:
            r = requests.post(DT_API_URL + '/api/v1/entity/infrastructure/custom/' + host.displayName + '?Api-Token=' + DT_API_TOKEN, json=json.loads(host.toJson()))
            print(host.displayName +": " + r.text + " | " + r.reason)

class Integracion(object):
    def __init__(self):
        self.NagiosConn = NagiosConnection()
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
            dHost = self.DynaConn.addCustomHost(host['name'], host['address'], '80', 'Nagios', favicon, '')
            lstTmpServices = self.NagiosConn.getMetricas(host['name'])
            
            if SERVICE_WHITELIST:
                for nagServ in lstTmpServices:
                    if nagServ["service_description"] in SERVICE_WHITELIST:
                        lstServices.append(nagServ)
            else:
                lstServices = lstTmpServices
            
            for service in lstServices:
                lstMetricas = self.NagiosConn.parsePerfData(service["perf_data"])
                for metrica in lstMetricas:
                    dHost.addSerie(service["description"], metrica, lstMetricas[metrica][0])

    def EnviarMetricas(self):
        '''Eviar los datos a Dynatrace'''
        self.DynaConn.sendMetrics()

#####MAIN###############################################################################################################
def main():
    try:
        integracion = Integracion()
        integracion.CargarHosts()
        integracion.CargarMetricas()
        integracion.EnviarMetricas()
    except NagiosToDynaError as err:
        print(err)

if __name__ == '__main__':
    main()