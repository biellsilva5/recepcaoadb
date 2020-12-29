from main import db

from bson import ObjectId
from datetime import datetime

## Banco de dados ##
recepcao = db['recepcao']
users = db['users']
visitas = db['visitas']

class Funcoes(object):
    def __init__(self):
        pass
    
    def buscarBanco(self, id=None):
        if id:
            pessoa = recepcao.find_one({'_id': ObjectId(id)})
            return pessoa
        pessoas = recepcao.find({})
        lista = []
        for pessoa in pessoas:
            pessoa['_id'] = str(pessoa['_id'])
            lista.append(pessoa)
        return lista

    def insereVisita(self, id):
        dicio = {
            'idRef': str(id),
            'data': datetime.now()
            }
        inserted = visitas.insert_one(dicio)
        if inserted.inserted_id:
            return True
        else:
            return False
    def buscarVisita(self, id):
        visita = visitas.find({'idRef': id})
        return visita
    
    def buscarAllVisitas(self):
        return list(visitas.find({}))
    
    def buscarUser(self, email=None, pwd=None, id=None):
        if pwd:
            pessoa = users.find_one({'email': email, "password": pwd})
            if not pessoa:
                return False 
            else:
                return pessoa
            
        elif id:
            pessoa = users.find_one({'_id': ObjectId(id)})
            return pessoa
            
        
    def buscarAllUsers(self):
        pessoa = users.find({})
        return list(pessoa)
    def newUser(self, email, pwd, name):
        inserted = users.insert_one({
            'nome': name,
            'email': email,
            'password': pwd
        })
        if inserted.inserted_id:
            return True
        else:
            return False

    def editUser(self, id, nome, email, pwd):
        dic = {'_id': ObjectId(id)}
        new = { '$set': {
            'nome' : nome,
            'email': email,
            'password': pwd
        }}

        updated = users.update_one(dic, new)
        print(updated)

    def delUser(self, id):
        removed = users.remove({'_id':  ObjectId(id)})
        print(removed)
        if removed['n'] == 1:
            return True
        else:
            return False

    def countAdmin(self):
        p = users.find({})
        v = visitas.find({})
        dicio = {
            'users': p.count(),
            'visitas': v.count()
        }

        return dicio