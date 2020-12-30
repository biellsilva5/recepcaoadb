from flask import Flask
from pymongo import MongoClient
app = Flask(__name__)

app.config.from_object('config')

client = MongoClient('mongodb+srv://adb:recadb@recepadb.3k4vl.mongodb.net/recepcao?retryWrites=true&w=majority')
db =  client[app.config['DATABASE']]

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
            'data': datetime.datetime.now()
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



from flask import render_template, request, jsonify, url_for, redirect, flash, session, Response
import datetime
import base64



from marcadagua import marcadagua
from decorators import requerAutenticacao

func = Funcoes()

## Banco de dados ##
recepcao = db['recepcao']
users = db['users']
visitas = db['visitas']

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js'), 200, {'Content-Type': 'text/javascript'}

@app.route('/')
def busca():
    lista = func.buscarBanco()
    return render_template('busca.html')

@app.route('/f/buscar')
def retBusca():
    pesquisa = request.args.get('p')
    if not pesquisa:
        return jsonify(func.buscarBanco())
    else:
        pessoas = recepcao.find({'nome': { "$regex": pesquisa, "$options" :'i'}}, {'img':False})
        
        lista = []
        for pessoa in pessoas:
            pessoa['_id'] = str(pessoa['_id'])
            lista.append(pessoa)
        return jsonify(lista)

@app.route('/profile/<id>')
def profile(id):
    pessoa = None
    visitas = None
    try:
        pessoa = func.buscarBanco(id)
        pessoa['_id'] = id
    except:
        return '<h1>ID inválido</h1> <a href="' + url_for('busca') + '">Voltar</a>'

    visitas = func.buscarVisita(id)
    view = request.args.get('view')
    return render_template('profile.html', dados = pessoa, view=view, visitas=visitas)

@app.route('/insere/visita/<id>')
@requerAutenticacao
def inserirVisita(id):
    inserindo = func.insereVisita(str(id))
    flash("Visita Adicionada")
    return redirect(request.referrer)

@app.route('/insere', methods=['GET', 'POST'])
def formulario():
    if request.method == 'GET':
        nome = request.args.get('nome')
        return render_template('formulario.html', nome=nome)
    elif request.method == 'POST':
        dados = request.form
        try:
            birth_date = datetime.datetime.strptime(dados['birth_date'], "%d - %m - %Y")
        except ValueError:
            birth_date = datetime.datetime.strptime(dados['birth_date'], "%d-%m-%Y")

        im_water = ''
        img_form = request.files['photofile']
        img_str = base64.b64encode(img_form.read())
        im_water = marcadagua(img_str)

        dicio = {
            'nome': dados['name'],
            'email': dados['email'],
            'gender': dados['gender'],
            'phone_number': dados['phone_number'],
            'casado': dados['casado'],
            'batizado': dados['batizado'],
            'sua_primeira_vez': dados['sua_primeira_vez'],
            'frequenta_igreja': dados['frequenta_igreja'],
            'qual_igreja': dados['qual_igreja'],
            'img': im_water,
            'birth_date':  birth_date
        }

        inserted = recepcao.insert_one(dicio)
        visitar = func.insereVisita(inserted.inserted_id)

        return render_template('formulario.html')

@app.route('/admin')
@requerAutenticacao
def admin():
    infos = func.countAdmin()
    return render_template('dash/index.html', infos=infos)

@app.route('/admin/visitas')
@requerAutenticacao
def adVisita():
    visitas = func.buscarAllVisitas()
    return render_template('dash/visitas.html', visitas = visitas, buscarBanco=func.buscarBanco)

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@requerAutenticacao
def adUser():
    i = request.args.get('i')
    edit = request.args.get('edit')
    delete = request.args.get('del')

    if request.method == 'POST':
        if i:
            dados = request.form
            insert = func.newUser(dados['email'], dados['password'], dados['nome'])
            if insert:
                flash('Usuario criado com sucesso.')
                return redirect(url_for('adUser'))
        elif edit:
            dados = request.form
            update = func.editUser(edit, dados['nome'], dados['email'], dados['password'])
            flash('Usuario editado.')
            return redirect(url_for('adUser'))
    
    

    if delete and func.delUser(delete):
        flash('Usuario deletado')
        return redirect(url_for('adUser'))


    users = func.buscarAllUsers()
    for user in users:
        user['_id'] = str(user['_id'])

    userE = {}
    if edit:
        userE = func.buscarUser(id=edit)  
        
    return render_template('dash/usuarios.html', i=i, users=users, edit=edit, userE=userE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        dados = request.form
        try:
            user = func.buscarUser(dados['email'], dados['password'])
            if user:
                session.clear()
                session['email'] = user['email']
                session['nome'] = user['nome']
                return redirect(url_for('admin'))
            else:
                flash('Usuario e/ou senha inválido')
                return redirect(url_for('login'))
        except KeyError:
            print('Key Error')
            return redirect(url_for('login'))
    return render_template('dash/login.html')

@app.route('/admin/logout')
@requerAutenticacao
def logout():
    session.clear()
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run()