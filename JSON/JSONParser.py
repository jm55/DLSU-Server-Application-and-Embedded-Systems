import json

def writejson(dev_id:str, cmd:str, val:str):
    out = "{\"dev_id\":\"" + dev_id + "\", \"cmd\":\"" + cmd + "\", \"val\":\"" + val + "\"}"
    #UNIVERSAL JSON FORMAT:
    #{"dev_id":"deviceID", "cmd":"command", "val":"value"}
    return out

def readjson(input:str):
    x = None
    try:
        x = json.loads(input)
        return x
    except: 
        return None
    
def cleanresponse(response:str):
    parsedval = ""
    parsed = readjson(response)
    if parsed is None:
        parsedval = "ERROR OCCURED"
    else:
        parsedval = parsed['val']
        if parsedval is None:
            parsedval = "ERROR OCCURED"
    return parsedval

def errjson(dev_id:str):
    return writejson(dev_id,"ERR","ERROR")