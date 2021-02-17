import os,json,random
from .Util import Util
from .Base import Base




class JsonProvider(Base):
  
    def __init__(self, dbName: str = "database.json"):
  
        if not dbName.endswith(".json"):
            dbName += ".json"
  
        super().__init__(dbName,"json")
        self.__filePath = "{}/{}".format(os.getcwd(), dbName)
  
        if not os.path.isfile(self.__filePath):
  
            with open(self.__filePath, "w") as file:
                file.write(json.dumps({}))
                file.close()
  
        self.__util = Util()
        return

    def all(self, limit: int = None) -> list:
  
        with open(self.__filePath, "r") as file:
            strData = file.read()
            file.close()
            data = json.loads(strData)
            dataList = []
  
            for i in data:
                dataList.append({"ID": i, "data": data[i]})
  
            if type(limit) == int:
                dataList = dataList[:limit]
  
        return dataList

    def toJSON(self, limit: int = None):
  
        allDataList = self.all(limit)
        JSON = {}
  
        for item in allDataList:
            JSON[item["ID"]] = item["data"]
  
        return JSON

    def fetchAll(self, limit: int = None) -> list:
        return self.all(limit)

    def set(self, key: str, value):
        
        parsed = self.__util.parseKey(key)
        target = parsed["target"]
        allData = self.toJSON()
        
        try:
            if target:
                self.__util.setData(target, allData, value)
            else:
                allData[key] = value
        except AttributeError as Error:
            del allData[parsed["key"]]
            self.__util.setData(target,allData,value)
        
        self.__save(allData)
        return value

    def fetch(self, key: str):
        
        parsed = self.__util.parseKey(key)
        target = parsed["target"]
        allData = self.toJSON()
        
        if target:
            getData = self.__util.getData(target, allData)
            return getData
        try:
            return allData[parsed["key"]]
        except KeyError:
            return None

    def get(self, key: str):
        return self.fetch(key)

    def math(self, key: str, value: int or float, operator: "+" or "-" or "*" or "/" or "//" or "%"):
        
        if type(value) == int or type(value) == float:
            getData = self.get(key)
        
            if not getData:
                return self.set(key, value)
        
            if type(getData) == int or type(getData) == float:
               
                if operator == "+":
                    getData += value
                    return self.set(key, getData)
                elif operator == "-":
                    getData -= value
                    return self.set(key,getData)
                elif operator == "*":
                    getData *= value
                    return self.set(key, getData)
                elif operator == "/":
                    getData /= value
                    return self.set(key, getData)
                elif operator == "//":
                    getData //= value
                    return self.set(key, getData)
                elif operator == "%":
                    getData %= value
                    return self.set(key,getData)
            else:
                raise TypeError("Veri int yada float tipte olmak zorunda.\nVeri tipi: {}".format(type(getData)))
        else:
            raise TypeError("Value int yada float tipte olmak zorunda.\nValue tipi: {}".format(type(value)))

    
    def add(self, key: str, value: int or float):
        return self.math(key, value, "+")
    
    def substr(self, key: str, value: int or float):
        return self.math(key,value,"-")
    
    def has(self, key: str) -> bool:
       
        data = self.get(key)
       
        if data != None:
            return True
       
        return False
    
    def exists(self, key: str) -> bool:
        return self.has(key)

    def delete(self, key: str):
       
        if not self.has(key):
            raise Exception("Silinicek veri bulunamadı.")
       
        allData = self.toJSON()
        parsed = self.__util.parseKey(key)
        target = parsed["target"]
       
        if target:
            unSet = self.__util.unSetData(target, allData)
            return self.__save(unSet)
       
        del allData[key]
        return self.__save(allData)


    def deleteAll(self):
        return self.__save({})
    
    
    def type(self, key: str):
        return type(self.get(key))

    def push(self, key: str, value):
       
        if not self.has(key):
            return self.set(key, [value])
       
        data = self.get(key)
       
        if type(data) != list:
            raise TypeError("Veri bir list değil.")
       
        data.append(value)
        return self.set(key,data)

    def pull(self, key: str, value):
      
        if not self.has(key):
            raise Exception("Veri yok.")
      
        data = self.get(key)
        if type(data) != list:
            raise TypeError("Veri bir list değil.")
      
        data.remove(value)
        return self.set(key, data)
    
    def valueList(self, limit: int = None) -> list:
       
        allDataList = self.all(limit)
       
        def dataMap(item):
            return item["data"]
       
        value_list = list(map(dataMap, allDataList))
        return value_list

    def keyList(self, limit: int = None) -> list:
       
        allDataList = self.all(limit)
       
        def keyMap(item):
            return item["ID"]
       
        key_list = list(map(keyMap,allDataList))
        return key_list

    def listHasValue(self, key: str, value) -> bool:
       
        if not self.has(key):
            raise Exception("Veri yok.")
       
        data = self.get(key)
       
        if type(data) != list:
            raise TypeError("Veri list tipinde değil.")
       
        if type(value) == list:
            result = {}
       
            for item in value:
                if item in data:
                    result[item] = True
                else:
                    result[item] = False
            return result
        else:
            for item in data:
                if item == value:
                    return True
        return False

    def includes(self, key: str):
       
        allKey = self.keyList()
        allKey = list(filter(lambda item: item.__contains__(key), allKey))
        allData = self.toJSON()
        result = {}
       
        for key in allKey:
            result[key] = allData[key]
       
        return result

    def startsWith(self, key: str):
       
        allKey = self.keyList()
        allKey = list(filter(lambda item: item.startswith(key), allKey))
        allData = self.toJSON()
        result = {}
       
        for key in allKey:
            result[key] = allData[key]
       
        return result

    def valueFilter(self, func) -> list:
        valueList = self.valueList()
        return list(filter(func,valueList))

    def keyFilter(self, func) -> list:
        keyList = self.keyList()
        return list(filter(func,keyList))

    def findValue(self, func):
        return self.valueFilter(func)[0]

    def findKey(self, func):
        return self.keyFilter(func)[0]

    
    def list(self, limit: int = None):
        return self.all(limit)
        
    def randomValue(self, limit: int = None):
      
        allValue = self.valueList()
      
        if type(limit) == int:
            if limit > len(allValue):
                limit = len(allValue)
            result = []
      
            for i in range(limit):
                result.append(self.randomValue())
            return result
        else:
            randomInt = random.randint(0, (len(allValue) - 1))
            return allValue[randomInt]

    def randomKey(self, limit: int = None):
       
        allKey = self.keyList()
       
        if type(limit) == int:
            if limit > len(allKey):
                limit = len(allKey)
            result = []
          
            for i in range(limit):
                result.append(self.randomKey())
            return result
        else:
            randomInt = random.randint(0, (len(allKey) - 1))
            return allKey[randomInt]
    
    def __save(self, data):
        
        with open(self.__filePath, "w") as file:
            jsonStr = json.dumps(data, indent=4)
            file.write(jsonStr)
            file.close()
            return

    def __iter__(self):
      
        allData = self.all()
      
        for item in allData:
            yield item
