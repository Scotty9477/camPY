# coding: utf-8
import json
from datetime import datetime
from cam import cam, getNom, getStatus, setStatus, getIp, getLocalisation
import subprocess
import boto3
import os
from apscheduler.schedulers.blocking import BlockingScheduler

os.environ['AWS_PROFILE'] = "default"
os.environ['AWS_DEFAULT_REGION'] = "eu-west-3"
client = boto3.client('iot', region_name='eu-west-3')
client2 = boto3.client('iot-data', region_name='eu-west-3')
log = open("logs/log"+str(datetime.now())+".log", "w")

def parseCam() : 
    file = open("cams.json","r")
    content =  file.read()
    file.close()
    tabCams = json.loads(content)
    cams = []
    for uneCam in tabCams:
        if uneCam['Localisation'] == 0:
            uneCam['Localisation'] = [0,0]
        c = cam(uneCam['Camera'], uneCam['IP'], uneCam['Quad'], uneCam['Localisation'], 0)
        cams.append(c)
    return cams

def createThings(cams,log):
    log.write("[CREATE THINGS]\n\n")
    for uneCam in cams:

        thingName = getNom(uneCam)
        ip = getIp(uneCam)
        status = getStatus(uneCam)

        response = client.create_thing(
        thingName=thingName,
        attributePayload={
            'attributes': {
                'ip': ip,
                'name': thingName
            },
            'merge': False
        }
        )
        log.write("IOT response: " + str(response) + "\n\n")
        print("IOT response: " + str(response))  


def PingLesCams(cams):
    attributedName = []
    pingedCams = []         
    for i in range(0, len(cams)):
        
        if getNom(cams[i]) not in attributedName:
            command = ['ping', '-c', '1', getIp(cams[i])]
            responsePing = subprocess.call(command)
            attributedName.append(getNom(cams[i]))
            if responsePing == 0:
                print('ok')
                setStatus(cams[i], 'on')
                pingedCams.append(cams[i])
            else:
                print('nok')
                setStatus(cams[i], 'off')
                pingedCams.append(cams[i])
        else:
            command = ['ping', '-c', '1', getIp(cams[i])]
            responsePing = subprocess.call(command)      
            
            if responsePing == 0:
                print('ok')
                for j in range(0, len(pingedCams)):
                    if(getNom(cams[i]) == getNom(pingedCams[j])):
                        setStatus(pingedCams[j], 'on')
                    break
            
    return pingedCams

def updateThings(cams, log):
    log.write("[UPDATE THINGS]\n\n")
    for uneCam in cams:

        thingName = getNom(uneCam)
        ip = getIp(uneCam)
        status = getStatus(uneCam)
        localisation = getLocalisation(uneCam)
        latitude = localisation[0]
        longitude = localisation[1]
        payload = json.dumps({'state': { 'reported': { 'ip': ip, 'nom': thingName,
        "status": status,'latitude' : latitude,'longitude' : longitude, } }})
        
        response = client2.update_thing_shadow(
            thingName = getNom(uneCam),
            shadowName='cam_shadow', 
            payload =  payload
            )
            
        print("IOT response: " + str(response) )
        log.write("IOT response: " + str(response) + "\n\n")



def create():
    try:
        CamsPing = PingLesCams(parseCam())
        
    except:
        log.write("ERROR : Impossible de créer les objets")
    createThings(CamsPing, log)
def update():
    try: 
        nlog = open("logs/log"+str(datetime.now())+".log", "w")
        CamsPing = PingLesCams(parseCam())
        updateThings(CamsPing, nlog)
        nlog.close()
    except:
        nlog.write("ERROR : impossible de mettre a jour les objets")
        nlog.close()


create()
log.close()
update()
scheduler = BlockingScheduler()
scheduler.add_job(update, 'interval', hours=1)
scheduler.start()

