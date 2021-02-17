








class Base:
    def __init__(self, dbName: str,dataType:str):
        self.__dbName = dbName
        self.__dataType = dataType
    
    def getDbName(self):
        return self.__dbName
    
    def getDataType(self):
        return self.__dataType