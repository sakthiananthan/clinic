import json

def read_json(f):
    try:
        with open(f) as jf:
            data=json.load(jf)
    except:
        print("unable to read data")
        return { "users" : [] }
    return data 

def writejson(data,f):
    try:
        with open(f,"w") as jf:
            json.dump(data,jf,indent=3)
    except:
        print("unable to write data")