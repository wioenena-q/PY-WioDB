# wiodb



# İndirmek için
```bash
pip install wiodb
````





# Kullanım

```py
from wiodb import JsonProvider, SqliteProvider

db = JsonProvider()
sqliteDb = SqliteProvider()

db.set("test",3)

db.fetch("test")

db.add("test",3)

db.all()

db.fetchAll(2)

db.toJSON()

db.get("test")

db.math("test",5,"//")

db.substr("test",3)

db.has("test")

db.exists("test")

db.delete("test")

db.deleteAll()

db.type("test")

db.push("list",3)

db.pull("list",3)

db.valueList()

db.keyList()


db.listHasValue("list",3 or [3,2,1])

db.includes("te")

db.startsWith("tes")

def valueFilter(item):
    if type(item) == int:
        return True
    return False

db.valueFilter(valueFilter)

def keyFilter(item):
    if item.includes("te"):
        return True
    return False

db.keyFilter(keyFilter)


def findValue(item):
    if type(item) == int:
        return True
    return False


db.findValue(findValue)


def findKey(item):
    if item.includes("te"):
        return True
    return False

db.findKey(findKey)

db.list()

db.randomValue() # or db.randomValue(3)

db.randomKey() # or db.randomKey(3)

# Contact

[İnstagram](https://www.instagram.com/wioenena.q/)

- Discord: wioenena.q#6251
