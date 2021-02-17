import pymongo, random
from pymongo import MongoClient
from pydash import set_, get, unset
from .Base import Base
from .Util import Util

class MongoProvider(MongoClient, Base):
    
    def __init__(self, host=None, port=None, document_class=dict, tz_aware=None, connect=None, type_registry=None, dbName="json", **kwargs):
        
        super().__init__(host, port, document_class, tz_aware, connect, type_registry, **kwargs)
        Base.__init__(self, dbName, "mongo")
        
        self.__database = self[dbName]
        self.__collection = self.__database[dbName]
        self.databaseNames = self.list_database_names()
        self.collectionNames = self.__database.list_collection_names()
        self.__util = Util()
    
    def set(self, key: str, value):

        utilParsed = self.__util.parseKey(key)
        target = utilParsed["target"]
        _value = value

        if target:
            _value = self.__util.setData(key, {}, value)[utilParsed["key"]]
            key = utilParsed["key"]

        parsed = self.__parseKeyValue(key,_value)
        
        if self.has(key):
            self.__collection.update_many({"ID": key}, {"$set": parsed})
            return value
        else:
            self.__collection.insert_one(parsed)
            return value
    
    def fetch(self, key: str):

        utilParsed = self.__util.parseKey(key)
        parsed = self.__parseKey(utilParsed["key"])
        target = utilParsed["target"]
        item = self.__collection.find_one(parsed)
        data = item

        if target:
            _key = utilParsed["key"]
            data = {_key: data["data"]}
            data = self.__util.getData(key,data)
        elif data:
            data = data["data"]

        return data
    
    def get(self, key: str):
        return self.fetch(key)
    
    def all(self, limit: int = None) -> list:

        allData = self.__collection.find()
        result = []

        for i in allData:
            result.append(self.__parseData(i))

        if type(limit) == int:
            result = result[:limit]

        return result

    def fetchAll(self, limit: int = None):
        return self.all(limit)
    
    def toJSON(self, limit: int = None):

        allDataList = self.all(limit)
        JSON = {}

        for item in allDataList:
            JSON[item["ID"]] = item["data"]

        return JSON



    def has(self, key: str) -> bool:

        data = self.get(key)

        if data != None:
            return True

        return False
    
    def exists(self, key: str) -> bool:
        return self.has(key)
    
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
                    return self.set(key, getData)
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
                    return self.set(key, getData)
            else:
                raise TypeError("Veri int yada float tipte olmak zorunda.\nVeri tipi: {}".format(type(getData)))
        else:
            raise TypeError("Value int yada float tipte olmak zorunda.\nValue tipi: {}".format(type(value)))

    def add(self, key: str, value: int or float):
        return self.math(key, value, "+")

    def substr(self, key: str, value: int or float):
        return self.math(key, value, "-")
    
    def delete(self, key: str):

        if not self.has(key):
            raise Exception("Silinicek veri bulunamadı.")
        
        utilParsed = self.__util.parseKey(key)
        parsed = self.__parseKey(utilParsed["key"])
        target = utilParsed["target"]

        if target:
            _key = utilParsed["key"]
            item = self.get(_key)
            data = { _key: item }
            unSetData = self.__util.unSetData(key, data)
            self.set(_key,unSetData[_key])
            return

        self.__collection.find_one_and_delete(self.__parseKey(key))
        return
    
    def deleteAll(self):
        self.__collection.delete_many({})
        return
    
    def type(self, key: str):
        return type(self.get(key))
    
    def push(self, key: str, value):

        if not self.has(key):
            return self.set(key, [value])

        data = self.get(key)
        
        if type(data) != list:
            raise TypeError("Veri bir list değil.")
        
        data.append(value)
        return self.set(key, data)

    def pull(self, key: str, value)
    :
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
        
        key_list = list(map(keyMap, allDataList))
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
        return list(filter(func, valueList))

    def keyFilter(self, func) -> list:
        keyList = self.keyList()
        return list(filter(func, keyList))

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

    def __parseKey(self, key):
        return {"ID":key}

    def __parseKeyValue(self, key, value):
        return {"ID": key, "data": value}
    
    def __parseData(self, item):
        return {"ID": item["ID"], "data": item["data"]}
