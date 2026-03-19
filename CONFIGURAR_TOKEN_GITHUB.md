# 🔑 GUIA - CONFIGURAR TOKEN GITHUB PARA PUSH

## 📋 PASSO A PASSO PARA CRIAR TOKEN

### 1. ACESSE CONFIGURAÇÕES DO GITHUB
- Vá para: https://github.com/settings/tokens
- Clique em: **"Generate new token (classic)"**

### 2. CONFIGURE O TOKEN
```
Note: DatumAgro Push Token
Expiration: No expiration (ou 90 dias)
```

### 3. MARQUE AS PERMISSÕES
```
✅ repo (Full control of private repositories)
✅ workflow (Update GitHub Action workflows)
✅ packages (Upload packages to GitHub Package Registry)
```

### 4. CLIQUE "GENERATE TOKEN"
- **COPIE O TOKEN** imediatamente (não poderá ver novamente!)

---

## 💻 CONFIGURAR GIT PARA USAR TOKEN

### Método 1: Usar Token na URL (Recomendado)
```bash
# No terminal, execute:
git remote set-url origin https://SEU_USERNAME:SEU_TOKEN@github.com/nexuscrmia-wq/Datumagro.git

# Exemplo (substitua SEU_TOKEN pelo token copiado):
git remote set-url origin https://nexuscrmia-wq:ghp_1234567890abcdef@github.com/nexuscrmia-wq/Datumagro.git
```

### Método 2: Git Credential Manager
```bash
# Instalar credential helper
git config --global credential.helper store

# Fazer push (vai pedir usuário e senha/token)
git push -u origin main
# Usuário: nexuscrmia-wq
# Senha: SEU_TOKEN_AQUI
```

---

## 🚀 FAZER PUSH APÓS CONFIGURAR

```bash
# Verificar configuração
git remote -v

# Fazer push
git push -u origin main
```

---

## 🔍 VERIFICAR SE DEU CERTO

Após o push, acesse: https://github.com/nexuscrmia-wq/Datumagro

Você deve ver:
- ✅ Todos os arquivos do projeto
- ✅ README.md
- ✅ mobile_flutter/
- ✅ datumagro/
- ✅ Scripts de deploy

---

## 🚨 PROBLEMAS COMUNS

### "Support for password authentication was removed"
- Use token ao invés de senha
- Configure a URL com token: `https://USERNAME:TOKEN@github.com/...`

### "Repository not found"
- Verifique se o nome do repo está correto: `Datumagro`
- Confirme que você tem acesso ao repositório

### "Permission denied"
- Certifique-se de usar o token correto
- Verifique se o token tem permissões `repo`

---

## 📞 SUPORTE

Se ainda tiver problemas:
1. Execute: `git remote -v` (verificar URL)
2. Execute: `git config --list` (verificar configurações)
3. Teste: `git ls-remote origin` (testar conexão)

---

**🎯 APÓS CONFIGURAR O TOKEN, EXECUTE:**
```bash
git push -u origin main
```

**E O DATUMAGRO ESTARÁ NO GITHUB! 🚀**