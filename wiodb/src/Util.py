import pydash
from pydash import set_,get,unset,clone_deep








class Util:

    def __init__(self):
        return
        
    def parseKey(self, key: str):

        if key.__contains__("."):
            parseDot = key.split(".")
            targetKey = parseDot[0]
            target = ".".join(parseDot)

            return {"key": targetKey, "target": target}
        else:
            return {"key": key, "target": None}
    
    def setData(self, key: str, data, value):

        parsed = self.parseKey(key)
        target = parsed["target"]

        if type(data) == dict and target:
            return set_(data, target, value)

        return data

    def getData(self, key: str, data):

        parsed = self.parseKey(key)
        target = parsed["target"]

        if target:
            return get(data, target)
            
        return data
    
    def unSetData(self, key, data):

        parsed = self.parseKey(key)
        target = parsed["target"]
        cloneData = clone_deep(data)

        if type(data) == dict and target:
            unset(cloneData, target)

        return cloneData