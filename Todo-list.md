# Miner des tweets

1. Mode **Stream**
   Args :
   
   - API
   
   - Un dir de destination
   
   Renvoit :
   
   - Un fichier de destination
   
   - Un état?

1. Mode **Getter**

Exemple utilisation: 

```py
api = AuthApi("getter", cred1, cred2, cred3, cred4)
>>> miner1 = Miner("getter")
# Les données sont récupérés depuis un fichier qui contient les ids.
# Deux possibilités d'écriture: fichier ou BDD
>>> miner1.from_file("../data/CrisisLexT26/Colorado_2016_ids.csv")
.to("../data/tweets-from-ids/")
# ou
>>> miner1.from_file("../data/CrisisLexT26/Colorado_2016_ids.csv")
.to("database").db_config(arg1, arg2, arg3...)
# Puis on passe l'api qui sera utilisée pour récupérer les données.
# Cela lance également la récupération des données jusqu'à ce qu'on atteigne la limite
# d'appels
>>> miner1.mine(api)
```

2. Mode **Stream**
```py
api = AuthApi("stream", cred1, cred2, cred3, cred4)
>>> miner2 = Miner("stream")
# Les données sont récupérés directement depuis le live, il n'y a donc pas de méthode
# from_file().
>>> miner2.to("../data/tweets/")
# ou 
>>> miner2.to("database").db_config(arg1, arg2, arg3...)
>>> miner2.mine(api)
```


monkeypatch
    PRO: comes with pytest, no extra dependencies in python2 / python 3
    PRO (or CON depending on your attitude here, MagicMock is some crazy shenanigans): is dead simple, no MagicMock, no call tracking, just normal attribute setting
    CON: as it's a fixture, the scope is often more broad than expected instead of "just part of the function" or "just the function", it can often lead to patches "leaking" into other fixtures / etc. It's also difficult to control the ordering in some cases
        ok this isn't strictly fair, there is a context manager version, it's just not the "default style"
    CON: potentially less battle tested than mock (for example, #4536)
mock
    CON: for python2.x you need a dependency on the mock backport
    PRO: if you're python3.x only, it comes with the standard library (unittest.mock)
    PRO: many more features than monkeypatch (call tracking, MagicMock, assertion framework (though it has a really bad api (out of date article before mock 2.x made this ~slightly better))
    PRO: tight control over mocked context via context managers / decorators (if you want fixtures, you can make those too with yield
    CON: MagicMock is some crazy magic
pytest-mock: adds a mocker fixture which uses mock under the hood but with a surface area / api similar to monkeypatch
    Basically all of the features of mock, but with the api of monkeypatch. I don't like using it due to the same reasons I mentioned about scoping of patches in monkeypatch
