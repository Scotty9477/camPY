

from flask import Flask, jsonify

import boto3
import json

app = Flask(__name__)

@app.route('/api/campy')
def camera():
    file = open("cams.json","r")
    content =  file.read()    
    file.close()
    nomCam = []

    tabCams = json.loads(content)
    attributedName = []
    for uneCam in tabCams:
        if uneCam['Camera'] not in attributedName:
            nomCam.append(uneCam['Camera'])
            attributedName.append(uneCam['Camera'])


    shadows = []
    for i in range (0, len(nomCam)):
        response = client.get_thing_shadow(thingName=nomCam[i], shadowName='cam_shadow')
        streamingBody = response["payload"]
        jsonState = json.loads(streamingBody.read())
        shadows.append(jsonState["state"]["reported"])
    
    return jsonify(shadows)



if __name__ == "__main__":
    client = boto3.client('iot-data', region_name='eu-west-3')
    app.run()