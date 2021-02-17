import sqlite3,os,random,json
from .Base import Base
from .Util import Util

class SqliteProvider(Base):

    def __init__(self, dbName: str = "json.sqlite"):
    
        if not dbName.endswith(".sqlite"):
            dbName += ".sqlite"
    
        super().__init__(dbName,"sqlite")
    
        dbPath = "{}/{}".format(os.getcwd(), dbName)
    
        self.__dbPath = dbPath
        self.__connection = sqlite3.connect(dbPath)
        self.__cursor = self.__connection.cursor()
        self.__cursor.execute("CREATE TABLE IF NOT EXISTS wiodb (id,data)")
        self.__connection.commit()
        self.__connection.close()
        self.__util = Util()
        return

    def set(self, key: str, value):    
       
        if type(value) == list or type(value) == dict:
       
            if self.has(key):
                self.__connect()
                self.__cursor.execute("UPDATE wiodb SET data = ? WHERE id = ?", [value,key])
            else:
                self.__connect()
                self.__cursor.execute("INSERT INTO wiodb VALUES (?,?)", (key, value))
            self.__save()
            return value
       
        if self.has(key):
            self.__connect()
            self.__cursor.execute("UPDATE wiodb SET data = ? WHERE id = ?", [value, key])
        else:
            self.__connect()
            self.__cursor.execute("INSERT INTO wiodb VALUES (?,?)", (key, value))
        self.__save()
        return value

    def fetch(self, key: str):
      
        self.__connect()
      
        allData = self.__cursor.execute("SELECT * FROM wiodb WHERE id = ?", [key]).fetchone()
        
        if not allData:
            return None
        
        allData = self.__parseData(allData)
        self.__save()
        data = allData["data"]
        
        try:
            data = json.loads(data)
        except:
            pass
        return data

    def get(self, key: str):
        return self.fetch(key)

    def all(self, limit: int = None) -> list:
       
        self.__connect()
       
        dataList = self.__cursor.execute("SELECT * FROM wiodb").fetchall()
        result = []
       
        for i in dataList:
            result.append(self.__parseData(i))
       
        if type(limit) == int:
            result = result[:limit]
       
        self.__save()
        return result

    def toJSON(self, limit: int = None):
       
        allDataList = self.all(limit)
        JSON = {}
       
        for item in allDataList:
            JSON[item["ID"]] = item["data"]
        return JSON

    def fetchAll(self, limit: int = None) -> list:
        return self.all(limit)

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
        self.__connect()
        self.__cursor.execute("DELETE FROM wiodb WHERE id = ?", [key])
        
        self.__save()

    def deleteAll(self):
        
        self.__connect()
        self.__cursor.execute("DELETE FROM wiodb")
        self.__save()

    def type(self, key: str):
        return type(self.get(key))

    def push(self, key: str, value):
        
        if not self.has(key):
            return self.set(key, [value])
        
        self.__connect()
        data = self.get(key)
        
        if type(data) != list:
            raise TypeError("Veri bir list değil.")
        data.append(value)
        
        return self.set(key, data)

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
            try:
                return json.loads(item["data"])
            except:
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

    def __connect(self):
        self.__connection = sqlite3.connect(self.__dbPath)
        self.__cursor = self.__connection.cursor()
        return

    def __save(self):
        self.__connection.commit()
        self.__connection.close()

    def __parseData(self, data):
        return {"ID": data[0], "data": data[1]}
    
    def __iter__(self):
        allData = self.all()
        for item in allData:
            yield item
