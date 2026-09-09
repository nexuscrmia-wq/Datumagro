from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = 'Remove tokens expirados da blacklist JWT para reduzir overhead no banco.'

    def handle(self, *args, **options):
        try:
            from rest_framework_simplejwt.token_blacklist.models import (
                BlacklistedToken,
                OutstandingToken,
            )
        except ImportError:
            self.stderr.write('rest_framework_simplejwt.token_blacklist não instalado.')
            return

        now = timezone.now()

        # Remove tokens blacklistados cujo outstanding já expirou
        deleted_blacklisted, _ = BlacklistedToken.objects.filter(
            token__expires_at__lt=now
        ).delete()

        # Remove outstanding tokens expirados que não foram blacklistados
        deleted_outstanding, _ = OutstandingToken.objects.filter(
            expires_at__lt=now,
            blacklistedtoken__isnull=True,
        ).delete()

        total = deleted_blacklisted + deleted_outstanding
        self.stdout.write(
            self.style.SUCCESS(
                f'flush_tokens: {deleted_blacklisted} blacklisted + '
                f'{deleted_outstanding} outstanding removidos ({total} total).'
            )
        )
