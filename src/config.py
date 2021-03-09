import json

def getconfig(cfgfile):
    cfg = {}
    
    with open(cfgfile) as f:
        cfg = json.load(f)
    
    return cfg