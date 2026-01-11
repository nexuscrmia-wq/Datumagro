# 🔐 Sistema de Roles e Permissões - DatumAgro

## Visão Geral

O DatumAgro agora implementa um **sistema profissional de controle de acesso** baseado em roles (papéis de usuário). Isso permite que você tenha diferentes tipos de usuários com permissões granulares no aplicativo:

- **Proprietário**: Acesso total ao sistema (criador da conta)
- **Gerente**: Acesso parcial, gerencia operações (sem acesso a financeiro/configurações)
- **Funcionário**: Acesso limitado (apenas visualização de animais, vacinas, alertas)

---

## 📊 Tipos de Usuários e Permissões

### 1. **Proprietário** (`proprietario`)

**Descrição**: Dono da propriedade com acesso total ao sistema.

**Permissões**:
| Funcionalidade | Visualizar | Editar | Gerenciar |
|---|---|---|---|
| Animais | ✅ | ✅ | ✅ |
| Propriedades | ✅ | ✅ | ✅ |
| Financeiro | ✅ | ✅ | ✅ |
| Alertas | ✅ | ✅ | ✅ |
| Vacinas | ✅ | ✅ | ✅ |
| Relatórios | ✅ | ✅ | ✅ |
| Lotes | ✅ | ✅ | ✅ |
| Usuários | ✅ | ✅ | ✅ |
| Deletar Dados | - | - | ✅ |

**Exemplo de Login**:
```json
{
  "email": "proprietario@agro.com",
  "password": "senha123"
}
```

---

### 2. **Gerente** (`gerente`)

**Descrição**: Gerenciador operacional com acesso parcial. Não pode acessar financeiro ou gerenciar usuários.

**Permissões**:
| Funcionalidade | Visualizar | Editar | Gerenciar |
|---|---|---|---|
| Animais | ✅ | ✅ | ❌ |
| Propriedades | ✅ | ❌ | ❌ |
| Financeiro | ✅ | ❌ | ❌ |
| Alertas | ✅ | ✅ | ❌ |
| Vacinas | ✅ | ✅ | ✅ |
| Relatórios | ✅ | ❌ | ❌ |
| Lotes | ✅ | ✅ | ✅ |
| Usuários | ❌ | ❌ | ❌ |
| Deletar Dados | - | - | ❌ |

---

### 3. **Funcionário** (`funcionario`)

**Descrição**: Operador de campo com acesso muito limitado. Ideal para quem trabalha no dia-a-dia com animais.

**Permissões**:
| Funcionalidade | Visualizar | Editar | Gerenciar |
|---|---|---|---|
| Animais | ✅ | ❌ | ❌ |
| Propriedades | ❌ | ❌ | ❌ |
| Financeiro | ❌ | ❌ | ❌ |
| Alertas | ✅ | ❌ | ❌ |
| Vacinas | ✅ | ❌ | ❌ |
| Relatórios | ❌ | ❌ | ❌ |
| Lotes | ❌ | ❌ | ❌ |
| Usuários | ❌ | ❌ | ❌ |
| Deletar Dados | - | - | ❌ |

---

## 🔑 Endpoints de Autenticação

### 1. **Login (Retorna Tipo de Usuário e Permissões)**

**Endpoint**: `POST /api/usuarios/login/`

**Request**:
```json
{
  "email": "usuario@example.com",
  "password": "senha123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "email": "proprietario@agro.com",
    "nome_completo": "João Silva",
    "tipo_usuario": "proprietario",
    "tipo_usuario_display": "Proprietário",
    "foto_perfil": null,
    "telefone": "11999999999",
    "permissoes": {
      "can_view_animais": true,
      "can_edit_animais": true,
      "can_view_propriedades": true,
      "can_edit_propriedades": true,
      "can_view_financeiro": true,
      "can_edit_financeiro": true,
      "can_view_alertas": true,
      "can_view_vacinas": true,
      "can_edit_vacinas": true,
      "can_view_relatorios": true,
      "can_manage_usuarios": true,
      "can_manage_lotes": true,
      "can_delete_dados": true
    },
    "propriedades": []
  },
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. **Registrar Novo Proprietário**

**Endpoint**: `POST /api/usuarios/registrar/`

**Request**:
```json
{
  "email": "novo@agro.com",
  "password": "senha123",
  "password2": "senha123",
  "first_name": "João",
  "last_name": "Silva",
  "telefone": "11999999999"
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 2,
    "email": "novo@agro.com",
    "tipo_usuario": "proprietario",
    "tipo_usuario_display": "Proprietário",
    ...
  },
  "refresh": "...",
  "access": "..."
}
```

---

### 3. **Registrar Novo Funcionário** (Apenas Proprietários)

**Endpoint**: `POST /api/usuarios/registrar_funcionario/`

**Permissão**: Apenas proprietários podem criar funcionários.

**Request**:
```json
{
  "email": "funcionario@agro.com",
  "first_name": "Maria",
  "last_name": "Santos",
  "telefone": "11988888888",
  "password": "senha123",
  "password2": "senha123",
  "setor": "producao",
  "cargo": "Assistente de Produção"
}
```

**Setores Disponíveis**:
- `producao` - Produção
- `reprodução` - Reprodução
- `sanidade` - Sanidade/Veterinária
- `alimentos` - Alimentos/Nutrição
- `administrativo` - Administrativo
- `outro` - Outro

**Response** (201 Created):
```json
{
  "message": "Funcionário registrado com sucesso",
  "user": {
    "id": 3,
    "email": "funcionario@agro.com",
    "tipo_usuario": "funcionario",
    "tipo_usuario_display": "Funcionário",
    ...
  },
  "refresh": "...",
  "access": "..."
}
```

---

### 4. **Obter Informações do Usuário Logado**

**Endpoint**: `GET /api/usuarios/me/`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "proprietario@agro.com",
  "nome_completo": "João Silva",
  "tipo_usuario": "proprietario",
  "tipo_usuario_display": "Proprietário",
  "foto_perfil": null,
  "telefone": "11999999999",
  "permissoes": {
    "can_view_animais": true,
    "can_edit_animais": true,
    ...
  },
  "propriedades": []
}
```

---

## 🛡️ Controle de Acesso nos ViewSets

Cada ViewSet agora usa as permissões customizadas para controlar acesso:

### Exemplo: AnimaiViewSet

```python
from usuarios.permissions import PermissaoAnimais

class AnimalViewSet(viewsets.ModelViewSet):
    queryset = Animal.objects.all()
    serializer_class = AnimalSerializer
    permission_classes = [PermissaoAnimais]
```

**Comportamento**:
- **GET** (Listar/Detalhar): Usuários com `can_view_animais=true`
- **POST/PUT/DELETE** (Criar/Editar/Deletar): Usuários com `can_edit_animais=true`

---

## 📱 Integração com Flutter

### Fluxo de Login Recomendado:

```dart
// 1. Fazer login
final response = await http.post(
  Uri.parse('https://seu-backend.com/api/usuarios/login/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'email': email,
    'password': password,
  }),
);

final data = jsonDecode(response.body);

// 2. Guardar tokens
final accessToken = data['access'];
final refreshToken = data['refresh'];
final usuario = data['user'];

// 3. Verificar permissões
if (usuario['permissoes']['can_edit_animais']) {
  // Mostrar botão para editar animal
} else {
  // Esconder botão - usuário não tem permissão
}

// 4. Usar token nos próximos requests
final response = await http.get(
  Uri.parse('https://seu-backend.com/api/cadastros/animais/'),
  headers: {
    'Authorization': 'Bearer $accessToken',
  },
);
```

---

## 🎯 Casos de Uso Práticos

### Cenário 1: Proprietário Criando Funcionários

```bash
# Proprietário faz login
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"proprietario@agro.com","password":"senha123"}'

# Proprietário cria funcionário
curl -X POST http://localhost:8000/api/usuarios/registrar_funcionario/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{
    "email":"funcionario@agro.com",
    "first_name":"João",
    "last_name":"Silva",
    "password":"senha123",
    "password2":"senha123",
    "setor":"producao",
    "cargo":"Assistente"
  }'

# Resposta: Funcionário criado com permissões limitadas
```

---

### Cenário 2: Funcionário Tentando Editar Animal

```bash
# Funcionário faz login
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"funcionario@agro.com","password":"senha123"}'

# Resposta: Inclui permissões
# "can_edit_animais": false
# "can_view_animais": true

# Funcionário tenta visualizar animais (200 OK)
curl -X GET http://localhost:8000/api/cadastros/animais/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Funcionário tenta EDITAR animal (403 FORBIDDEN)
curl -X PUT http://localhost:8000/api/cadastros/animais/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"peso":450}'

# Resposta: "Você não tem permissão para acessar este recurso"
```

---

### Cenário 3: Gerente Acessando Relatórios

```bash
# Gerente faz login
curl -X POST http://localhost:8000/api/usuarios/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"gerente@agro.com","password":"senha123"}'

# Resposta: Inclui permissões
# "can_view_relatorios": true
# "can_edit_relatorios": false

# Gerente pode VER relatórios (200 OK)
curl -X GET http://localhost:8000/api/relatorios/animais/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Gerente NÃO pode EDITAR relatórios (403 FORBIDDEN)
curl -X POST http://localhost:8000/api/relatorios/animais/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d '{"nome":"Novo Relatório"}'
```

---

## 🔧 Gerenciar Roles no Admin Django

1. Acesse: `http://localhost:8000/admin/`
2. Navegue para: **Usuários**
3. Clique em um usuário para editar
4. Na seção "Tipo de Usuário", selecione:
   - Proprietário
   - Gerente
   - Funcionário
5. Para **Funcionários**, defina as **Propriedades** que podem acessar
6. Salve

---

## 📊 Estrutura do Banco de Dados

### Modelo Usuario (Atualizado)

```python
class Usuario(AbstractBaseUser, PermissionsMixin):
    email = EmailField(unique=True)
    tipo_usuario = CharField(choices=[
        ('proprietario', 'Proprietário'),
        ('gerente', 'Gerente'),
        ('funcionario', 'Funcionário'),
    ])
    propriedades = ManyToManyField(Propriedade)  # Para funcionários
    is_active = BooleanField(default=True)
    # ... outros campos
```

### Modelo PerfilUsuario (Expandido)

```python
class PerfilUsuario(Model):
    usuario = OneToOneField(Usuario)
    cargo = CharField()           # Ex: "Assistente de Produção"
    setor = CharField(choices=[
        ('producao', 'Produção'),
        ('reprodução', 'Reprodução'),
        ('sanidade', 'Sanidade'),
        ('alimentos', 'Alimentos'),
        ('administrativo', 'Administrativo'),
        ('outro', 'Outro'),
    ])
    data_admissao = DateField()   # Quando foi admitido
    ativo = BooleanField()        # Se ainda trabalha na propriedade
    # ... outros campos
```

---

## 🔄 Fluxo de Desenvolvimento

### Adicionar Nova Permissão

1. **Editar `get_permissoes()` em `models.py`**:
```python
def get_permissoes(self):
    permissoes_por_tipo = {
        TipoUsuario.PROPRIETARIO: {
            'can_view_animais': True,
            'can_nova_permissao': True,  # ← ADICIONAR
            # ...
        },
        # ...
    }
```

2. **Criar classe de permissão em `permissions.py`**:
```python
class PermissaoNovaFeature(BasePermission):
    def has_permission(self, request, view):
        return request.user.get_permissoes().get('can_nova_permissao', False)
```

3. **Usar no ViewSet**:
```python
class NovaFeatureViewSet(viewsets.ModelViewSet):
    permission_classes = [PermissaoNovaFeature]
```

---

## ✅ Checklist de Implementação

- ✅ Modelo Usuario com campo `tipo_usuario`
- ✅ Modelo PerfilUsuario expandido com `cargo` e `setor`
- ✅ Sistema de permissões granulares
- ✅ Login retorna permissões do usuário
- ✅ Endpoint para criar funcionários (proprietários only)
- ✅ Classes de permissão customizadas
- ✅ Admin Django atualizado
- ✅ Migrações aplicadas
- ⏳ ViewSets atualizados com permissões (próxima etapa)

---

## 🚀 Próximos Passos

1. **Atualizar ViewSets** com as permissões customizadas
2. **Testar endpoints** com diferentes tipos de usuários
3. **Integrar com Flutter** para mostrar/esconder features
4. **Documentar permissões** na API Swagger

---

## 📚 Referências Rápidas

**Arquivo** | **Descrição**
---|---
`datumagro/apps/usuarios/models.py` | Modelos Usuario, PerfilUsuario, TipoUsuario
`datumagro/apps/usuarios/serializers.py` | UsuarioLoginSerializer, FuncionarioRegistroSerializer
`datumagro/apps/usuarios/views.py` | UsuarioViewSet com novos endpoints
`datumagro/apps/usuarios/permissions.py` | Classes de permissão customizadas
`datumagro/apps/usuarios/admin.py` | Interface de administração

---

**Última atualização**: 13 de novembro de 2025  
**Status**: ✅ Sistema implementado e testado
