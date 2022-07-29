'''
AlertManager Json



'''

 
import requests
import json

class Event(object):
    def __init__(self, receiver, status):
        self.receiver = receiver,
        self.status = status,
        self.alerts = []

class Alerts(object):
    def __init__(self, status, instance, job, startsAt, generatorURL, fingerprint):
        self.status = status,
        self.instance = instance,
        self.job = job,
        self.annotations = [],
        self.startsAt = startsAt,
        self.generatorURL = generatorURL
        self.fingerprint = fingerprint

class Annotattions(object):
    def __init__(self, descriptions):
        self.descriptions = descriptions
