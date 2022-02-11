import json
class cam:
    def __init__(self, nom, ip, quad, localisation, status):
        self.nom = nom
        self.ip = ip
        self.quad = quad
        self.localisation = localisation
        self.status = status


def getNom(self):
    return self.nom

def getIp(self):
    return self.ip

def getQuad(self):
    return self.quad

def getLocalisation(self):
    return self.localisation

def getStatus(self):
    return self.status

def setStatus(self, status):
    self.status = status

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, 
    sort_keys=True, indent=4)