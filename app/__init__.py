# app/__init__.py

import os
from flask import Flask, redirect, url_for

def create_app(test_config=None):
    # Cria e configura a aplicação
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # Inicializa o banco de dados e registra o comando init-db
    from . import db
    db.init_app(app)

    # Registra os Blueprints (CRUD e Testes)
    from . import medicos, tests
    app.register_blueprint(medicos.bp)
    app.register_blueprint(tests.bp)
    
    # Rota principal para redirecionar para a página de médicos
    @app.route('/')
    def index():
        return redirect(url_for('medicos.index'))

    return app