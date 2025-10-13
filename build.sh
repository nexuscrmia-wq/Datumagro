#!/usr/bin/env bash
# exit on error
set -o errexit

# Instala todas as dependências do requirements.txt
pip install -r requirements.txt

# Coleta todos os arquivos estáticos para um único lugar
python manage.py collectstatic --no-input

# Aplica as migrações do banco de dados para criar/atualizar as tabelas
python manage.py migrate