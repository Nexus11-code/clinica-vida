# Clínica Vida

## Sobre o projeto

A Clínica Vida é um sistema simples que fiz para organizar as informações de um consultório fictício. A ideia é facilitar o cadastro de pacientes e o controle das consultas, sem precisar deixar essas informações espalhadas.

O sistema foi desenvolvido com Python, Flask, HTML, CSS e SQLite.

## O que dá para fazer

- Cadastrar pacientes e consultar a lista.
- Procurar um paciente pelo nome.
- Alterar ou excluir os dados de um paciente.
- Marcar consultas para os pacientes cadastrados.
- Alterar o horário, o profissional, o motivo e o status de uma consulta.
- Consultar os dados pelas rotas da API, que retornam JSON.

## Como executar no computador

1. Instale o Python.
2. Abra a pasta do projeto no VS Code.
3. Abra o terminal dentro do VS Code.
4. Instale as bibliotecas necessárias:

   ```bash
   pip install -r requirements.txt
   ```

5. Inicie o programa:

   ```bash
   python app.py
   ```

6. No navegador, entre em `http://127.0.0.1:5000`.

O banco `clinica.db` é criado automaticamente quando o programa inicia.

## Como o banco foi organizado

O banco tem duas tabelas principais:

- `pacientes`: guarda nome, telefone, e-mail e data de nascimento.
- `consultas`: guarda o paciente relacionado, o profissional, a data, o horário, o motivo e o status.

A coluna `paciente_id` da tabela `consultas` aponta para o `id` da tabela `pacientes`. Assim, uma pessoa pode ter mais de uma consulta.

## Rotas da API

- `/api/pacientes` mostra os pacientes em JSON.
- `/api/consultas` mostra as consultas em JSON.

## Publicação

O projeto tem um `Procfile` e um `render.yaml` para ajudar na publicação pelo Render. Depois de conectar o repositório do GitHub, confira se o comando de instalação é `pip install -r requirements.txt` e se o comando de inicialização é `gunicorn app:app`.

**Atenção:** este projeto é apenas para fins de estudo. Use somente dados fictícios. O armazenamento SQLite local do Render pode não ser permanente em todas as configurações; para manter os dados de forma confiável, é necessário configurar um disco persistente ou outro banco de dados.

## Antes de entregar

- [ ] Testei cadastrar, editar e excluir pacientes.
- [ ] Testei cadastrar, editar e excluir consultas.
- [ ] Abri as rotas da API.
- [ ] Testei o site pelo celular ou diminuí a largura do navegador.
- [ ] Publiquei o projeto no GitHub e no Render.
- [ ] Escrevi o relatório com minhas próprias palavras e com exemplos do que eu fiz.
