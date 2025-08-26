#!/bin/bash

# Este script cria a estrutura de diretórios e os arquivos vazios
# para o projeto MedLink, assumindo que __init__.py e requirements.txt já existem.

echo "Iniciando a criação da estrutura de arquivos do projeto..."

# --- 1. Criação da Estrutura de Diretórios ---
echo "--> Criando diretórios necessários (app/templates/medicos, app/templates/tests)..."
mkdir -p app/templates/medicos
mkdir -p app/templates/tests

# --- 2. Criação dos Arquivos Vazios ---
echo "--> Criando arquivos de configuração na raiz..."
touch Dockerfile
touch docker-compose.yml

echo "--> Criando arquivos .py da aplicação..."
touch app/db.py
touch app/schema.sql
touch app/medicos.py
touch app/tests.py

echo "--> Criando arquivos de template (.html)..."
touch app/templates/base.html
touch app/templates/medicos/index.html
touch app/templates/medicos/create.html
touch app/templates/medicos/update.html
touch app/templates/tests/index.html

echo ""
echo "Estrutura de arquivos criada com sucesso!"
echo "Os arquivos estão vazios e prontos para serem preenchidos."