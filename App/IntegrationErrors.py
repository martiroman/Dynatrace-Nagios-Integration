''' 
Manejo de errores

'''
class IntegrationErrors(Exception):
    """Errores"""

class NagiosToDynaError(IntegrationErrors):
    """Errores de la integracion"""

class NagiosToDynaQueryError(NagiosToDynaError):
    """Fallo en la query al socket"""

class NagiosToDynaConnectError(NagiosToDynaError):
    """Error de conexion al socket"""