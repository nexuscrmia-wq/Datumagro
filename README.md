# DatumAgro 🐂

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-5.4-3781A9?style=for-the-badge&logo=celery&logoColor=white)

Uma plataforma completa de Pecuária de Precisão com Inteligência Artificial, desenvolvida pela **Vexus IA**.

## 🎯 Sobre o Projeto

O DatumAgro nasceu da necessidade de modernizar a gestão pecuária, substituindo anotações manuais em cadernetas e planilhas complexas por uma plataforma digital, inteligente e centralizada. O objetivo é transformar dados brutos em decisões estratégicas, aumentando a eficiência e a lucratividade da fazenda.

O sistema é construído sobre uma arquitetura de API RESTful robusta (o "motor"), pronta para ser consumida por múltiplas interfaces, como um aplicativo mobile (Android) e uma plataforma web.

## ✨ Principais Funcionalidades

O motor do DatumAgro é modular e foi dividido em 11 apps, cada um com sua responsabilidade:

* **Gestão de Cadastros:** Controle completo de Clientes, Propriedades e Animais, incluindo um sistema de **Árvore Genealógica** para rastreamento genético.
* **Controle Operacional:** Registro de manejos sanitários, reprodutivos, e gestão de Lotes e Piquetes para pastejo rotacionado.
* **Análise Financeira:** Lançamento de custos e receitas, com ferramentas para análise de fluxo de caixa e lucratividade.
* **IA Zootecnista Virtual:** Um sistema proativo que analisa os dados e gera alertas inteligentes sobre saúde, desempenho (baixo GMD) e manejo.
* **Notificações Ativas:** Alertas enviados automaticamente para o produtor via E-mail e WhatsApp (utilizando Twilio).
* **Rastreabilidade (Selo de Origem):** Geração de uma página pública e um QR Code para cada animal, contando sua história "da fazenda à mesa".
* **Integrações com Hardware (IoT):** API pronta para receber dados de equipamentos de campo, como leitores de RFID e balanças eletrônicas.
* **Gestão de Assinaturas:** Sistema de planos (Digital, Conectado, Elite) com controle de status e vencimento.
* **Geração de Relatórios:** Criação de relatórios em PDF e Excel sob demanda.
* **Autenticação Moderna:** Sistema de usuários customizado com autenticação via Token para a API.

## 🛠️ Tech Stack

* **Back-end:** Python, Django, Django REST Framework
* **Banco de Dados:** PostgreSQL (produção), SQLite (desenvolvimento)
* **Tarefas Assíncronas:** Celery, Redis
* **Servidor de Produção:** Gunicorn, Whitenoise
* **Análise de Dados:** Pandas
* **Outros:** WeasyPrint (PDFs), Pillow (Imagens), Twilio (WhatsApp)

## 🚀 Setup e Instalação Local

Para rodar este projeto em um ambiente de desenvolvimento local:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/victor226942-web/DatumAgro.git](https://github.com/victor226942-web/DatumAgro.git)
    cd DatumAgro
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure as variáveis de ambiente:**
    * Crie uma cópia do arquivo `.env.example` (se houver) para `.env`.
    * Preencha as variáveis como `SECRET_KEY`, `DATABASE_URL` (para dev, pode deixar em branco), e chaves de API.

5.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Crie um superusuário:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Inicie o servidor:**
    ```bash
    python manage.py runserver
    ```
O sistema estará rodando em `http://127.0.0.1:8000/`.

---
