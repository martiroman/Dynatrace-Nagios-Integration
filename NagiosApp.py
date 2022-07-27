import IntegrationErrors
import re
#https://github.com/arthru/python-mk-livestatus
from mk_livestatus import Socket

class Connection(object):
    """Realiza las querys al socket de Nagios"""
    def __init__(self):
        try:
            self._sock = Socket(NAGIOS_SOCKET)
        except Exception as err:
            raise IntegrationErrors.NagiosToDynaConnectError(err)
        
    def getHosts(self):
        '''Realiza la query para obtener los hosts'''
        try:
            q = self._sock.hosts.columns('name', 'alias', 'address', 'groups')
            return q.call() 
        except Exception as err:
            raise IntegrationErrors.NagiosToDynaQueryError(err)

    def getMetricas(self, hostname):
        '''Realiza la query para obtener los servicios y cada una de las metricas'''
        try:
            q = self._sock.services.columns('service_description', 'state', 'latency', 'perf_data',
                                            'process_performance_data', 'check_command', 'acknowledged','execution_time', 
                                            'is_flapping').filter('host_name = ' + hostname)
            return q.call()
        except Exception as err:
            raise IntegrationErrors.NagiosToDynaQueryError(err)

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