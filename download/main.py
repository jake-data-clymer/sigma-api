import http.client
import requests
import json
from time import sleep

client='6ad28d7f6a9e813ced4a428068cf8c8b80ec0dd3923580cded47d8dc7b72d2d7'
secret='0d368a9b43a769e06e3a6e80aee610826ae5e596031b4b8380049c4a777f8da7a0a7c0b2f8099b083623769df9bd9d8bb79da5f800f48f26a6dabb2e1332c9ec'

downloadType = 'pdf'
workbookDetails = {
    "pageId": "uswkpPxjM0",
    "format": {
        "type": ""+downloadType +"",
        "layout": "landscape"
    },
    "timeout": 5,
    "filters": {
        "Airline": "DL",
        "Year": 2015
    }
}

#requests the bearer token. Probably doesn't need to happen everytime. I think there is a refresh endpoint. 
def get_bearer(client_id,client_secret):
    conn = http.client.HTTPSConnection("aws-api.sigmacomputing.com")
    payload = 'grant_type=client_credentials&client_id='+client_id+'&client_secret='+client_secret
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("POST", "/v2/auth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    rawBearer = json.loads(data)
    bearer = rawBearer['access_token']

    return bearer

#Requests the queryid to download the workbook details
def request_download(bearer,workbook):
    conn = http.client.HTTPSConnection("aws-api.sigmacomputing.com")
    payload = json.dumps(workbook)
    headers = {
    'Content-Type': 'application/json',
    'accept': 'application/json',
    'Authorization': 'Bearer '+bearer
    }
    conn.request("POST", "/v2/workbooks/1GHyXZ3mpEpSfpafZ63L9Y/export", payload, headers)
    res = conn.getresponse()
    data = res.read()
    queryidRaw = json.loads(data)
    queryid = queryidRaw['queryId']
    print(queryid)
    return queryid 

#downloads the workbook details
def download(client_id, client_secret,workbook,downloadType):
    bearer = get_bearer(client_id,client_secret)
    queryid = request_download(bearer,workbook)
    sleep(30) #The response from /v2/workbooks/export contains the job status and queryid. There doesn't appear to be a way to check if the job is complete. An arbitrary sleep value may be the only option.
    url = "https://aws-api.sigmacomputing.com/v2/query/"+queryid+"/download"
    payload={}
    headers = {
    'accept': 'application/json',
    'Authorization': 'Bearer '+bearer
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    with open('workbook.'+downloadType, "wb") as file:
        file.write(response.content)

download(client,secret,workbookDetails,downloadType)
