# datumagro/apps/usuarios/managers.py

from django.contrib.auth.models import BaseUserManager


class UsuarioManager(BaseUserManager):
    """ Manager para o nosso modelo de usuário customizado. """

    def create_user(self, email, password=None, **extra_fields):
        """ Cria e salva um usuário com o e-mail e senha fornecidos. """
        if not email:
            raise ValueError('O campo de E-mail é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """ Cria e salva um superusuário. """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)