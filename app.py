from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from pathlib import Path
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "chave-local-clinica-vida")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "clinica.db"


def conectar():
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def criar_banco():
    with conectar() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT,
                data_nascimento TEXT
            );

            CREATE TABLE IF NOT EXISTS consultas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                medico TEXT NOT NULL,
                data_consulta TEXT NOT NULL,
                horario TEXT NOT NULL,
                motivo TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Agendada',
                FOREIGN KEY (paciente_id) REFERENCES pacientes(id) ON DELETE CASCADE
            );
        """)


def buscar_pacientes(termo=""):
    # Primeiro pego os pacientes do banco. Depois faço a busca e a ordenação em Python.
    with conectar() as db:
        registros = db.execute("SELECT * FROM pacientes").fetchall()

    encontrados = []
    for paciente in registros:
        if termo.lower() in paciente["nome"].lower():
            encontrados.append(paciente)

    # Ordenação por inserção: coloca os nomes em ordem alfabética.
    for i in range(1, len(encontrados)):
        atual = encontrados[i]
        j = i - 1
        while j >= 0 and encontrados[j]["nome"].lower() > atual["nome"].lower():
            encontrados[j + 1] = encontrados[j]
            j -= 1
        encontrados[j + 1] = atual

    return encontrados


def listar_consultas():
    with conectar() as db:
        return db.execute("""
            SELECT consultas.*, pacientes.nome AS paciente_nome
            FROM consultas
            JOIN pacientes ON consultas.paciente_id = pacientes.id
            WHERE consultas.status != 'Cancelada'
            ORDER BY consultas.data_consulta, consultas.horario
        """).fetchall()


@app.route("/")
def inicio():
    with conectar() as db:
        total_pacientes = db.execute("SELECT COUNT(*) FROM pacientes").fetchone()[0]
        total_consultas = db.execute("SELECT COUNT(*) FROM consultas").fetchone()[0]
        proximas = db.execute("""
            SELECT consultas.*, pacientes.nome AS paciente_nome
            FROM consultas
            JOIN pacientes ON consultas.paciente_id = pacientes.id
            WHERE consultas.status = 'Agendada'
            ORDER BY consultas.data_consulta, consultas.horario
            LIMIT 5
        """).fetchall()
    return render_template(
        "index.html",
        total_pacientes=total_pacientes,
        total_consultas=total_consultas,
        proximas=proximas
    )


@app.route("/pacientes", methods=["GET", "POST"])
def pacientes():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        telefone = request.form.get("telefone", "").strip()
        email = request.form.get("email", "").strip()
        nascimento = request.form.get("data_nascimento", "")
        if not nome or not telefone:
            flash("Nome e telefone são obrigatórios.", "erro")
        else:
            with conectar() as db:
                db.execute(
                    "INSERT INTO pacientes (nome, telefone, email, data_nascimento) VALUES (?, ?, ?, ?)",
                    (nome, telefone, email, nascimento)
                )
            flash("Paciente cadastrado com sucesso.", "sucesso")
            return redirect(url_for("pacientes"))
    termo = request.args.get("busca", "").strip()
    return render_template("pacientes.html", pacientes=buscar_pacientes(termo), busca=termo)


@app.route("/pacientes/<int:paciente_id>/editar", methods=["GET", "POST"])
def editar_paciente(paciente_id):
    with conectar() as db:
        paciente = db.execute("SELECT * FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()
        if paciente is None:
            flash("Paciente não encontrado.", "erro")
            return redirect(url_for("pacientes"))
        if request.method == "POST":
            nome = request.form.get("nome", "").strip()
            telefone = request.form.get("telefone", "").strip()
            if not nome or not telefone:
                flash("Nome e telefone são obrigatórios.", "erro")
            else:
                db.execute("""
                    UPDATE pacientes
                    SET nome = ?, telefone = ?, email = ?, data_nascimento = ?
                    WHERE id = ?
                """, (nome, telefone, request.form.get("email", "").strip(),
                      request.form.get("data_nascimento", ""), paciente_id))
                flash("Dados do paciente atualizados.", "sucesso")
                return redirect(url_for("pacientes"))
    return render_template("editar_paciente.html", paciente=paciente)


@app.route("/pacientes/<int:paciente_id>/excluir", methods=["POST"])
def excluir_paciente(paciente_id):
    with conectar() as db:
        db.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
    flash("Paciente e consultas relacionadas foram excluídos.", "sucesso")
    return redirect(url_for("pacientes"))


@app.route("/consultas", methods=["GET", "POST"])
def consultas():
    if request.method == "POST":
        paciente_id = request.form.get("paciente_id", type=int)
        medico = request.form.get("medico", "").strip()
        data = request.form.get("data_consulta", "")
        horario = request.form.get("horario", "")
        motivo = request.form.get("motivo", "").strip()
        if not all([paciente_id, medico, data, horario, motivo]):
            flash("Preencha todos os campos da consulta.", "erro")
        else:
            with conectar() as db:
                existe = db.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()
                if existe:
                    db.execute("""
                        INSERT INTO consultas
                        (paciente_id, medico, data_consulta, horario, motivo)
                        VALUES (?, ?, ?, ?, ?)
                    """, (paciente_id, medico, data, horario, motivo))
                    flash("Consulta agendada.", "sucesso")
                    return redirect(url_for("consultas"))
                flash("Selecione um paciente válido.", "erro")
    with conectar() as db:
        lista_pacientes = db.execute("SELECT id, nome FROM pacientes ORDER BY nome").fetchall()
        lista_consultas = db.execute("""
            SELECT consultas.*, pacientes.nome AS paciente_nome
            FROM consultas
            JOIN pacientes ON consultas.paciente_id = pacientes.id
            ORDER BY consultas.data_consulta DESC, consultas.horario
        """).fetchall()
    return render_template("consultas.html", pacientes=lista_pacientes, consultas=lista_consultas)


@app.route("/consultas/<int:consulta_id>/editar", methods=["GET", "POST"])
def editar_consulta(consulta_id):
    with conectar() as db:
        consulta = db.execute("SELECT * FROM consultas WHERE id = ?", (consulta_id,)).fetchone()
        pacientes_lista = db.execute("SELECT id, nome FROM pacientes ORDER BY nome").fetchall()
        if consulta is None:
            flash("Consulta não encontrada.", "erro")
            return redirect(url_for("consultas"))
        if request.method == "POST":
            paciente_id = request.form.get("paciente_id", type=int)
            medico = request.form.get("medico", "").strip()
            data = request.form.get("data_consulta", "")
            horario = request.form.get("horario", "")
            motivo = request.form.get("motivo", "").strip()
            status = request.form.get("status", "Agendada")
            if all([paciente_id, medico, data, horario, motivo]):
                db.execute("""
                    UPDATE consultas SET paciente_id=?, medico=?, data_consulta=?,
                    horario=?, motivo=?, status=? WHERE id=?
                """, (paciente_id, medico, data, horario, motivo, status, consulta_id))
                flash("Consulta atualizada.", "sucesso")
                return redirect(url_for("consultas"))
            flash("Preencha todos os campos.", "erro")
    return render_template("editar_consulta.html", consulta=consulta, pacientes=pacientes_lista)


@app.route("/consultas/<int:consulta_id>/excluir", methods=["POST"])
def excluir_consulta(consulta_id):
    with conectar() as db:
        db.execute("DELETE FROM consultas WHERE id = ?", (consulta_id,))
    flash("Consulta excluída.", "sucesso")
    return redirect(url_for("consultas"))


@app.route("/api/pacientes")
def api_pacientes():
    lista = buscar_pacientes()
    return jsonify([dict(p) for p in lista])


@app.route("/api/consultas")
def api_consultas():
    with conectar() as db:
        lista = db.execute("""
            SELECT consultas.id, pacientes.nome AS paciente, consultas.medico,
                   consultas.data_consulta, consultas.horario, consultas.motivo, consultas.status
            FROM consultas
            JOIN pacientes ON consultas.paciente_id = pacientes.id
            ORDER BY consultas.data_consulta, consultas.horario
        """).fetchall()
    return jsonify([dict(c) for c in lista])


criar_banco()

if __name__ == "__main__":
    app.run(debug=True)
