import http.client
import json
import os
import urllib
import time

tfce="app.terraform.io"
baseapi="/api/v2"

# TF_TOKEN_app_terraform_io
token=os.environ["TFC_TOKEN"]
orgname="carlos-villegas-sandbox"

def getWorkspaceId(workspacedict):
    return workspacedict['id']

def getWorkspaceName(workspacedict):
    return workspacedict['attributes']['name']

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
    #print(params)
    conn.request("GET", baseapi+"/organizations/"+orgname+"/workspaces?"+params,"",headers)
    res = conn.getresponse()
    #print(res.status, res.reason)
    data = res.read()
    #print(len(data))
    #print(data)
    jdata=json.loads(data)
    #workspaces=list(map(getWorkspaceId, jdata["data"]))
    workspaces=list(jdata["data"])
    #print(workspaces)
    next_page=jdata["meta"]["pagination"]["next-page"]
    #print(next_page)
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

workspaces=listWorkspaces(tfce, orgname)

#workspaceIds=list(map(getWorkspaceId, workspaces))
#print(workspaceIds)

def printResourceLines(orgname, wsid, resources):
    for res in resources:
        print(tfce+","+orgname+","+wsid+","+res['type']+"\n")

for ws in workspaces:
    wsid=getWorkspaceId(ws)
    wsname=getWorkspaceName(ws)
    time.sleep(0.05)
    printResourceLines(orgname, wsname, getCurrentStateVersion(tfce, orgname, wsid))

