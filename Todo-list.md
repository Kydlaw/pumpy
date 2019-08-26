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