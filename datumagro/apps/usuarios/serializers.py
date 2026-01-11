from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'telefone', 'data_nascimento', 'foto_perfil',
            'password', 'password2',
        )
        read_only_fields = ('id',)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        user = Usuario.objects.create_user(password=password, **validated_data)
        return user


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError({"new_password": "As senhas não coincidem."})
        return attrs