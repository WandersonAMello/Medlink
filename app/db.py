import os
import psycopg2
import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            os.environ['DATABASE_URL'],
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    with current_app.open_resource('schema.sql') as f:
        cur.execute(f.read().decode('utf8'))
    db.commit()
    cur.close()

@click.command('init-db')
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas."""
    init_db()
    click.echo('Banco de dados inicializado.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)