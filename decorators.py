from flask import session, url_for, redirect, request
from functools import wraps

def requerAutenticacao(f):
    @wraps(f)
    def funcaoDecorada(*args, **kwargs):
        if 'nome' not in session:
            dados = {"error": "Login requerido"}
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return funcaoDecorada