import http.client
import json
import os
import urllib
import time

baseapi="/api/v2"

# TF_TOKEN_app_terraform_io
try:
    tfce=os.environ["TFE_HOSTNAME"]
except Exception:
    tfce="app.terraform.io"

token=os.environ["TFE_TOKEN"]
orgname=os.environ["TFE_ORGANIZATION"]

def getWorkspaceId(workspacedict):
    return workspacedict['id']

def getWorkspaceName(workspacedict):
    return workspacedict['attributes']['name']

def getWorkspaceTerraformVersion(workspacedict):
    return workspacedict['attributes']['terraform-version']

def getResources(stateversiondict):
    return stateversiondict['attributes']['resources']

def getModules(stateversiondict):
    return stateversiondict['attributes']['modules']

def listWorkspaces(tfce, orgname, page = 0, prevdata = []):
    if ( page != 0 ):
        params = urllib.parse.urlencode({"page[number]":page})
    else:
        params = urllib.parse.urlencode({})
    headers = {"Accept":"application/json", "Authorization": "Bearer "+token}
    conn = http.client.HTTPSConnection(tfce)
    conn.request("GET", baseapi+"/organizations/"+orgname+"/workspaces?"+params,"",headers)
    res = conn.getresponse()
    data = res.read()
    jdata=json.loads(data)
    workspaces=list(jdata["data"])
    next_page=jdata["meta"]["pagination"]["next-page"]
    if next_page != None:
        time.sleep(0.05)
        return listWorkspaces(tfce, orgname, next_page, prevdata+workspaces)
    else:
        return prevdata+workspaces

def getCurrentStateVersion(tfce, orgname, wsid):
    headers = {"Accept":"application/json", "Authorization": "Bearer "+token}
    conn = http.client.HTTPSConnection(tfce)
    conn.request("GET", baseapi+"/workspaces/"+wsid+"/current-state-version","",headers)
    res = conn.getresponse()
    if res.status == 404:
        return []
    data = res.read()
    jdata=json.loads(data)
    currentState=getResources(jdata["data"])
    return currentState

def printResourceLines(orgname, wsid, tfversion, resources):
    for res in resources:
        print(tfce+","+orgname+","+wsid+","+tfversion+","+res['type'])


workspaces=listWorkspaces(tfce, orgname)

for ws in workspaces:
    wsid=getWorkspaceId(ws)
    wsname=getWorkspaceName(ws)
    wstfversion=getWorkspaceTerraformVersion(ws)
    time.sleep(0.05)
    printResourceLines(orgname, wsname, wstfversion, getCurrentStateVersion(tfce, orgname, wsid))

