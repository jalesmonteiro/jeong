#!/bin/bash

# Ativa o ambiente virtual
source venv/bin/activate

# Aplica as migrações do banco de dados
#python manage.py migrate

# Executa o servidor Django
python manage.py runserver
