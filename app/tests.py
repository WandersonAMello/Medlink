from flask import Blueprint, render_template
from app.db import get_db
import time

bp = Blueprint('tests', __name__, url_prefix='/tests')

@bp.route('/')
def index():
    results = []
    db = get_db()
    cur = db.cursor()

    # Teste 1: Conexão com o Banco
    try:
        cur.execute('SELECT version()')
        version = cur.fetchone()[0]
        results.append({'name': 'Conexão com PostgreSQL', 'status': 'OK', 'details': version})
    except Exception as e:
        results.append({'name': 'Conexão com PostgreSQL', 'status': 'Falha', 'details': str(e)})
        return render_template('tests/index.html', results=results)

    # Teste 2: Verificar se a tabela Pessoas existe
    try:
        cur.execute("SELECT 1 FROM Pessoas LIMIT 1")
        results.append({'name': 'Tabela "Pessoas" existe', 'status': 'OK', 'details': 'Tabela encontrada.'})
    except:
        results.append({'name': 'Tabela "Pessoas" existe', 'status': 'Falha', 'details': 'Não foi possível consultar a tabela.'})

    # Teste 3: Testar Trigger de DataAtualizacao
    try:
        cur.execute("INSERT INTO Pessoas (Cpf, Senha, Email, TipoPessoa) VALUES ('12312312312', 'test', 'test@trigger.com', 'MEDICO') RETURNING Id, DataCriacao")
        pessoa_id, data_criacao = cur.fetchone()
        db.commit()
        time.sleep(1) # Espera 1 segundo para garantir que o timestamp seja diferente
        cur.execute("UPDATE Pessoas SET Email = 'test_update@trigger.com' WHERE Id = %s", (pessoa_id,))
        db.commit()
        cur.execute("SELECT DataAtualizacao FROM Pessoas WHERE Id = %s", (pessoa_id,))
        data_atualizacao = cur.fetchone()[0]
        
        if data_atualizacao > data_criacao:
            results.append({'name': 'Trigger "DataAtualizacao"', 'status': 'OK', 'details': f'Registro atualizado em {data_atualizacao}'})
        else:
            results.append({'name': 'Trigger "DataAtualizacao"', 'status': 'Falha', 'details': 'Timestamp não foi atualizado.'})
        
        # Limpeza
        cur.execute("DELETE FROM Pessoas WHERE Id = %s", (pessoa_id,))
        db.commit()
    except Exception as e:
        db.rollback()
        results.append({'name': 'Trigger "DataAtualizacao"', 'status': 'Falha', 'details': str(e)})

    cur.close()
    return render_template('tests/index.html', results=results)