from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Usuario, PerfilUsuario, TipoUsuario


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o perfil adicional do usuário."""
    class Meta:
        model = PerfilUsuario
        fields = (
            'bio', 'endereco', 'cidade', 'estado', 'cargo', 'setor',
            'data_admissao', 'ativo'
        )


class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    perfilusuario = PerfilUsuarioSerializer(read_only=True)
    tipo_usuario_display = serializers.CharField(source='get_tipo_usuario_display', read_only=True)
    nome_completo = serializers.CharField(required=False, allow_blank=True)
    permissoes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Usuario
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'nome_completo', 'telefone', 'data_nascimento', 'foto_perfil',
            'tipo_usuario', 'tipo_usuario_display',
            'password', 'password2', 'perfilusuario', 'permissoes',
        )
        read_only_fields = ('id',)

    def get_permissoes(self, obj):
        return obj.get_permissoes()

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        # Limite de funcionários só se aplica ao criar (não em PATCH de perfil)
        if self.instance is not None:
            return attrs
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request and hasattr(request, 'user'):
            owner = request.user
            owner_perfil = getattr(owner, 'perfilusuario', None)
            cliente = getattr(owner_perfil, 'cliente', None) if owner_perfil else None
            if cliente:
                assinatura = getattr(cliente, 'assinatura', None)
                plano = getattr(assinatura, 'plano', None) if assinatura else None
                if plano is not None:
                    max_func = getattr(plano, 'max_funcionarios', 0)
                    from datumagro.apps.usuarios.models import Usuario as UsuarioModel
                    current_count = UsuarioModel.objects.filter(
                        tipo_usuario='funcionario',
                        propriedades__cliente=cliente
                    ).distinct().count()
                    if current_count >= max_func:
                        raise serializers.ValidationError({
                            'detail': f"Limite de funcionários atingido para o plano atual ({max_func})."
                        })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        try:
            user = Usuario.objects.create_user(password=password, **validated_data)
            # Criar perfil padrão (usar get_or_create para evitar conflitos)
            PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={
                    'bio': '',
                    'endereco': '',
                    'cidade': '',
                    'estado': '',
                    'cargo': '',
                    'setor': '',
                    'ativo': True
                }
            )
            return user
        except Exception as e:
            # Se houver erro na criação, tentar limpar o usuário se foi criado
            if 'user' in locals():
                try:
                    user.delete()
                except:
                    pass
            raise serializers.ValidationError(f"Erro ao criar usuário: {str(e)}")


class UsuarioLoginSerializer(serializers.Serializer):
    """Serializer para login com informações de tipo de usuário e permissões."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    # Campos de resposta
    id = serializers.IntegerField(read_only=True)
    email_response = serializers.SerializerMethodField(read_only=True)
    nome_completo = serializers.CharField(read_only=True)
    tipo_usuario = serializers.CharField(read_only=True)
    tipo_usuario_display = serializers.SerializerMethodField(read_only=True)
    foto_perfil = serializers.ImageField(read_only=True)
    telefone = serializers.CharField(read_only=True)
    permissoes = serializers.SerializerMethodField(read_only=True)
    propriedades = serializers.SerializerMethodField(read_only=True)

    def get_email_response(self, obj):
        return obj.get('email')

    def get_tipo_usuario_display(self, obj):
        tipo = obj.get('tipo_usuario')
        return dict(TipoUsuario.choices).get(tipo, tipo)

    def get_permissoes(self, obj):
        """Retorna as permissões do usuário logado."""
        usuario = obj.get('usuario_obj')
        if usuario:
            return usuario.get_permissoes()
        return {}

    def get_propriedades(self, obj):
        """Retorna as propriedades que o usuário tem acesso."""
        usuario = obj.get('usuario_obj')
        if usuario:
            return [
                {'id': p.id, 'nome': p.nome_propriedade}
                for p in usuario.propriedades.all()
            ] if usuario.tipo_usuario != TipoUsuario.PROPRIETARIO else []
        return []


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('new_password2'):
            raise serializers.ValidationError({"new_password": "As senhas não coincidem."})
        return attrs


class FuncionarioRegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de funcionário (apenas para proprietários/gerentes)."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    setor = serializers.CharField(source='perfilusuario.setor', required=False)
    cargo = serializers.CharField(source='perfilusuario.cargo', required=False)

    class Meta:
        model = Usuario
        fields = (
            'email', 'first_name', 'last_name', 'telefone',
            'password', 'password2', 'setor', 'cargo'
        )

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "As senhas não coincidem."})
        request = self.context.get('request') if hasattr(self, 'context') else None
        if request and hasattr(request, 'user'):
            owner = request.user
            prop = owner.propriedades.select_related('cliente').first()
            cliente = prop.cliente if prop else None
            if cliente:
                assinatura = getattr(cliente, 'assinatura', None)
                plano = getattr(assinatura, 'plano', None) if assinatura else None
                if plano is not None:
                    max_func = getattr(plano, 'max_funcionarios', 0)
                    from django.contrib.auth import get_user_model
                    UsuarioModel = get_user_model()
                    current_count = UsuarioModel.objects.filter(
                        tipo_usuario='funcionario',
                        propriedades__cliente=cliente
                    ).distinct().count()
                    if current_count >= max_func:
                        raise serializers.ValidationError({
                            'detail': f"Limite de funcionários atingido para o plano atual ({max_func})."
                        })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2', None)
        password = validated_data.pop('password')
        setor = self.initial_data.get('setor')
        cargo = self.initial_data.get('cargo')
        
        user = Usuario.objects.create_user(
            password=password,
            tipo_usuario=TipoUsuario.FUNCIONARIO,
            **validated_data
        )
        # Criar perfil com informações específicas
        perfil = PerfilUsuario.objects.create(usuario=user, setor=setor, cargo=cargo)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = Usuario.USERNAME_FIELD