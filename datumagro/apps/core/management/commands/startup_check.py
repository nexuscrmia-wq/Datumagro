"""
Roda antes do gunicorn no Railway. Verifica pré-condições críticas e loga
avisos sem travar o processo — falhas de banco são esperadas em cold-start
e resolvidas pelo retry do Railway.
"""
import os
import sys
import logging

logger = logging.getLogger('datumagro.startup')


class Command:
    pass


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Valida ambiente de produção e loga avisos sem travar o startup.'

    def handle(self, *args, **options):
        warnings = []

        if os.getenv('SECRET_KEY', '').startswith('django-insecure-'):
            warnings.append('SECRET_KEY usando fallback inseguro — defina no Railway Variables.')

        if not os.getenv('DATABASE_URL'):
            warnings.append('DATABASE_URL não definida — usando SQLite local.')

        if not os.getenv('DEFAULT_FROM_EMAIL') and not os.getenv('SENDGRID_API_KEY'):
            warnings.append('E-mail não configurado — convites não serão enviados.')

        for w in warnings:
            self.stdout.write(self.style.WARNING(f'[startup_check] AVISO: {w}'))

        if not warnings:
            self.stdout.write(self.style.SUCCESS('[startup_check] Ambiente OK.'))
