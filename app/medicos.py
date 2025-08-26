from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from app.db import get_db

bp = Blueprint('medicos', __name__, url_prefix='/medicos')

# Rota principal (READ)
@bp.route('/')
def index():
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT m.Id, m.NomeCompleto, m.Especialidade, p.Cpf, p.Email'
        ' FROM Medicos m JOIN Pessoas p ON m.PessoaId = p.Id'
        ' ORDER BY m.NomeCompleto'
    )
    medicos = cur.fetchall()
    cur.close()
    return render_template('medicos/index.html', medicos=medicos)

# Rota para (CREATE)
@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        nome = request.form['nome']
        especialidade = request.form['especialidade']
        cpf = request.form['cpf']
        email = request.form['email']
        senha = request.form['senha'] # Em um app real, use hash!
        
        db = get_db()
        cur = db.cursor()
        error = None

        if not nome or not cpf or not email or not senha:
            error = 'Todos os campos são obrigatórios, exceto especialidade.'

        if error is None:
            try:
                # Insere na tabela Pessoas primeiro, e retorna o ID gerado
                cur.execute(
                    "INSERT INTO Pessoas (Cpf, Senha, Email, TipoPessoa)"
                    " VALUES (%s, %s, %s, %s) RETURNING Id",
                    (cpf, senha, email, 'MEDICO')
                )
                pessoa_id = cur.fetchone()[0]

                # Usa o ID retornado para inserir na tabela Medicos
                cur.execute(
                    "INSERT INTO Medicos (NomeCompleto, Especialidade, PessoaId)"
                    " VALUES (%s, %s, %s)",
                    (nome, especialidade, pessoa_id)
                )
                db.commit()
            except db.IntegrityError:
                error = f"CPF {cpf} ou Email {email} já cadastrado."
                db.rollback()
            else:
                return redirect(url_for('medicos.index'))
        
        flash(error)
        cur.close()

    return render_template('medicos/create.html')

# Função para buscar um médico por ID para as rotas de Update e Delete
def get_medico(id):
    db = get_db()
    cur = db.cursor()
    cur.execute(
        'SELECT m.Id, m.NomeCompleto, m.Especialidade, p.Cpf, p.Email, p.Id as PessoaId'
        ' FROM Medicos m JOIN Pessoas p ON m.PessoaId = p.Id WHERE m.Id = %s',
        (id,)
    )
    medico = cur.fetchone()
    cur.close()
    if medico is None:
        abort(404, f"Médico com id {id} não encontrado.")
    return medico

# Rota para (UPDATE)
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    medico = get_medico(id)

    if request.method == 'POST':
        nome = request.form['nome']
        especialidade = request.form['especialidade']
        email = request.form['email']
        pessoa_id = medico[5]
        error = None

        if not nome or not email:
            error = 'Nome e Email são obrigatórios.'

        if error is None:
            try:
                db = get_db()
                cur = db.cursor()
                cur.execute(
                    'UPDATE Medicos SET NomeCompleto = %s, Especialidade = %s WHERE Id = %s',
                    (nome, especialidade, id)
                )
                cur.execute(
                    'UPDATE Pessoas SET Email = %s WHERE Id = %s',
                    (email, pessoa_id)
                )
                db.commit()
                cur.close()
            except Exception as e:
                error = f"Erro ao atualizar: {e}"
                db.rollback()
            else:
                return redirect(url_for('medicos.index'))
        flash(error)

    return render_template('medicos/update.html', medico=medico)

# Rota para (DELETE)
@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    medico = get_medico(id)
    pessoa_id = medico[5]
    db = get_db()
    cur = db.cursor()
    # Graças ao ON DELETE CASCADE, ao deletar a Pessoa, o Medico correspondente será deletado.
    cur.execute('DELETE FROM Pessoas WHERE Id = %s', (pessoa_id,))
    db.commit()
    cur.close()
    return redirect(url_for('medicos.index'))