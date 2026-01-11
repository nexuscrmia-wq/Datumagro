# DatumAgro - Sistema de Gestão para Pecuária

O DatumAgro é uma plataforma completa para gestão de propriedades pecuárias, oferecendo recursos de cadastro, rastreabilidade, gestão financeira, e inteligência artificial para otimização do manejo.

## � Guia de Telas do Frontend

### 1. Autenticação e Perfil
- **Login**: Email e senha, botão de recuperação
- **Registro**: Formulário de novo usuário
- **Recuperação de Senha**: Fluxo por email
- **Perfil do Usuário**: Dados pessoais e da empresa
- **Configurações**: Preferências do usuário

### 2. Dashboard Principal
- **Visão Geral**: 
  - Indicadores principais (total de animais, peso médio)
  - Gráfico de evolução do rebanho
  - Alertas ativos
  - Fluxo de caixa resumido

### 3. Gestão de Propriedades
- **Lista de Propriedades**: 
  - Grid com cards de propriedades
  - Indicadores por propriedade
  - Ações rápidas
- **Cadastro/Edição**: 
  - Formulário com dados da propriedade
  - Upload de documentos
  - Mapa para localização

### 4. Gestão de Animais
- **Lista do Rebanho**:
  - Filtros avançados
  - Visualização em lista/grid
  - Status sanitário/reprodutivo
- **Ficha do Animal**:
  - Dados completos
  - Histórico de pesagens
  - Genealogia
  - Registros sanitários
  - Histórico reprodutivo
- **Registro de Pesagem**:
  - Individual ou em lote
  - Integração com balança
  - Gráfico de evolução

### 5. Financeiro
- **Dashboard Financeiro**:
  - Gráficos de receitas/despesas
  - Fluxo de caixa
  - Indicadores principais
- **Transações**:
  - Lista com filtros
  - Categorização
  - Vinculação com animais
- **Categorias**:
  - Gestão de categorias
  - Regras de classificação
- **Formas de Pagamento**:
  - Cadastro de cartões
  - Chaves PIX

### 6. Inteligência
- **Central de Alertas**:
  - Filtros por tipo
  - Priorização
  - Ações rápidas
- **Análise Preditiva**:
  - Projeções de crescimento
  - Indicadores de saúde
  - Recomendações de manejo

### 7. Operacional
- **Manejo Sanitário**:
  - Calendário de vacinação
  - Registro de tratamentos
  - Histórico por animal
- **Reprodução**:
  - Controle de ciclos
  - Registro de coberturas
  - Previsão de partos
- **Gestão de Lotes**:
  - Composição dos lotes
  - Movimentação de animais
  - Histórico de alterações
- **Piquetes**:
  - Mapa de pastagens
  - Rotação de lotes
  - Status de ocupação

### 8. Rastreabilidade
- **Perfis Públicos**:
  - Lista de perfis ativos
  - Geração de QR Code
  - Preview público
- **Página Pública** (consumidor):
  - História do animal
  - Certificações
  - Origem e manejo

### 9. Relatórios
- **Geração de Relatórios**:
  - Seleção de modelos
  - Filtros personalizados
  - Preview e download
- **Histórico**:
  - Relatórios gerados
  - Compartilhamento

### 10. Assinaturas
- **Planos**:
  - Comparativo de planos
  - Recursos inclusos
  - Preços
- **Minha Assinatura**:
  - Status atual
  - Histórico de pagamentos
  - Upgrade/Downgrade

## �🚀 Principais Funcionalidades

### 📝 Cadastros Básicos

#### Propriedades (`/api/cadastros/propriedades/`)
- Cadastro completo de fazendas
- Campos principais:
  - Nome, localização, área total
  - Coordenadas geográficas
  - Capacidade de animais
  - Documentação (Inscrição estadual, etc)
  - Responsável técnico
  - Tipo de produção (Cria, Recria, Engorda)
- Funcionalidades:
  - Upload de documentos
  - Mapa da propriedade
  - Divisão em áreas/piquetes
  - Histórico de ocupação

#### Animais (`/api/cadastros/animais/`)
- Registro individual completo:
  - Identificação (Brinco, Chip RFID)
  - Data nascimento/aquisição
  - Raça e características
  - Genealogia (Pai/Mãe)
  - Proprietário/Parceria
- Sistema de pesagem:
  - Registro periódico
  - Cálculo GMD (Ganho Médio Diário)
  - Projeções de crescimento
  - Integração com balanças
- Reprodução:
  - Status reprodutivo
  - Histórico de partos
  - Eficiência reprodutiva
- Sanidade:
  - Calendário sanitário
  - Histórico de vacinas
  - Tratamentos realizados

#### Registros de Pesagem (`/api/cadastros/pesagens/`)
- Pesagem individual ou em lote
- Dados registrados:
  - Peso atual
  - Data/hora
  - Local/balança
  - Responsável
  - Condição corporal
- Análises automáticas:
  - Cálculo de ganho diário
  - Comparativo com média do lote
  - Alertas de desempenho
  - Projeções de abate

#### Clientes (`/api/cadastros/clientes/`)
- Gestão de produtores/empresas
- Dados cadastrais:
  - Razão social/Nome
  - CNPJ/CPF
  - Endereço completo
  - Contatos principais
  - Documentação fiscal
- Controle de acesso:
  - Múltiplos usuários
  - Níveis de permissão
  - Histórico de acessos

### 💰 Gestão Financeira

#### Categorias (`/api/financeiro/categorias/`)
- Estrutura hierárquica:
  - Tipo (Receita/Despesa)
  - Categoria pai/filha
  - Status ativo/inativo
- Categorias padrão:
  - Custos operacionais
  - Insumos e medicamentos
  - Mão de obra
  - Manutenção
  - Vendas de animais
  - Arrendamentos
- Personalização:
  - Categorias customizadas
  - Regras de classificação
  - Orçamentos por categoria

#### Transações (`/api/financeiro/transacoes/`)
- Registro detalhado:
  - Valor e data
  - Categoria
  - Forma de pagamento
  - Centro de custo
  - Anexos/comprovantes
- Vinculações:
  - Animal específico
  - Lote de animais
  - Propriedade
  - Fornecedor/Cliente
- Recorrência:
  - Transações agendadas
  - Parcelamentos
  - Frequência personalizada

#### Fluxo de Caixa (`/api/financeiro/transacoes/fluxo_caixa_mensal/`)
- Visualizações:
  - Diário/Semanal/Mensal/Anual
  - Por categoria
  - Por propriedade
  - Por centro de custo
- Análises:
  - Projeções futuras
  - Comparativos períodos
  - Indicadores financeiros
  - DRE simplificado

#### Formas de Pagamento (`/api/financeiro/formas-pagamento/`)
- Tipos suportados:
  - Cartão de crédito
  - Cartão de débito
  - PIX
  - Transferência
  - Dinheiro
- Gestão cartões:
  - Múltiplos cartões
  - Dados tokenizados
  - Renovação automática
- Chaves PIX:
  - Múltiplas chaves
  - QR Code dinâmico
  - Conciliação automática

### 🧠 Inteligência Artificial (`/api/inteligencia/`)

#### Sistema de Alertas Inteligentes (`/api/inteligencia/alertas/`)
- **Alertas Sanitários**:
  - Previsão de vacinações
  - Vermifugações pendentes
  - Tratamentos em andamento
  - Riscos sanitários detectados
  - Surtos na região

- **Alertas Reprodutivos**:
  - Previsão de cios
  - Diagnóstico de gestação
  - Previsão de partos
  - Eficiência reprodutiva
  - Problemas de fertilidade

- **Alertas de Desempenho**:
  - Ganho de peso abaixo da meta
  - Comparativo com lote
  - Projeções de abate
  - Custos por animal
  - ROI projetado

- **Alertas de Manejo**:
  - Rotação de pastagens
  - Superlotação
  - Degradação de pasto
  - Necessidade de suplementação
  - Previsão climática

- **Alertas Genéticos**:
  - Cruzamentos recomendados
  - Riscos de endogamia
  - Potencial genético
  - Melhoramento direcionado
  - Tendências de mercado

#### Machine Learning
- **Modelos Preditivos**:
  - Previsão de peso
  - Probabilidade de prenhez
  - Risco sanitário
  - Valor de mercado
  - Custo projetado

- **Análise de Padrões**:
  - Comportamento animal
  - Eficiência alimentar
  - Indicadores de saúde
  - Performance reprodutiva
  - Qualidade da carcaça

#### Dashboard Inteligente
- **Indicadores em Tempo Real**:
  - KPIs personalizados
  - Tendências e projeções
  - Comparativos históricos
  - Benchmarks do setor
  - Recomendações automáticas

### 🔄 Operacional

#### Manejo Sanitário (`/api/operacional/manejos-sanitarios/`)
- **Produtos Sanitários**:
  - Cadastro de medicamentos
  - Controle de estoque
  - Período de carência
  - Dosagens recomendadas
  - Fornecedores

- **Protocolos Sanitários**:
  - Calendário de vacinação
  - Vermifugação estratégica
  - Tratamentos preventivos
  - Exames periódicos
  - Certificações sanitárias

#### Reprodução (`/api/operacional/registros-reprodutivos/`)
- **Controle Reprodutivo**:
  - Registro de cios
  - Inseminações
  - Diagnóstico gestação
  - Partos
  - Desmame

- **Estatísticas**:
  - Taxa de prenhez
  - Intervalo entre partos
  - Eficiência reprodutiva
  - Histórico por matriz
  - Desempenho reprodutores

#### Gestão de Lotes (`/api/operacional/lotes/`)
- **Formação de Lotes**:
  - Critérios de agrupamento
  - Capacidade ideal
  - Homogeneidade
  - Objetivos específicos
  - Rastreabilidade

- **Movimentação**:
  - Entrada/Saída
  - Transferências
  - Histórico completo
  - Motivos de movimentação
  - Quarentena

#### Sistema de Piquetes (`/api/operacional/piquetes/`)
- **Gestão de Pastagens**:
  - Mapeamento áreas
  - Capacidade suporte
  - Tipos de forragem
  - Estado conservação
  - Infraestrutura

- **Rotação Inteligente**:
  - Períodos ocupação
  - Tempo descanso
  - Carga animal ideal
  - Disponibilidade forragem
  - Previsão climática

### 📊 Relatórios
- Geração de relatórios customizados
- Análises de desempenho
- Exportação em PDF

### 🔍 Rastreabilidade (`/api/rastreabilidade/`)

#### Perfis Públicos (`/api/rastreabilidade/gerenciar-perfis/`)
- **Configuração do Perfil**:
  - Informações públicas
  - História do animal
  - Fotos e vídeos
  - Certificações
  - Prêmios/Destaques

- **QR Code Personalizado**:
  - Geração automática
  - Design customizado
  - Link permanente
  - Estatísticas de acesso
  - Integração marketing

#### Página Pública (`/api/rastreabilidade/publico/{slug}/`)
- **Informações do Animal**:
  - Origem e nascimento
  - Raça e linhagem
  - Sistema de criação
  - Alimentação natural
  - Bem-estar animal

- **Histórico Completo**:
  - Crescimento/Desenvolvimento
  - Manejo sanitário
  - Certificações obtidas
  - Propriedades/Criadores
  - Prêmios e destaques

#### Sistema SISBOV/TRACES
- **Conformidade**:
  - Documentação oficial
  - Registros obrigatórios
  - Auditorias/Vistorias
  - Certificações exportação
  - Rastreabilidade completa

#### Marketing Digital
- **Divulgação**:
  - Redes sociais
  - Website próprio
  - Material promocional
  - Eventos/Exposições
  - Parcerias comerciais

### 👥 Gestão de Usuários (`/api/usuarios/`)

#### Autenticação
- **Sistema JWT**:
  - Login seguro
  - Tokens de acesso/refresh
  - Expiração configurável
  - Blacklist de tokens
  - Multi-dispositivo

#### Perfis de Usuário (`/api/usuarios/me/`)
- **Dados Pessoais**:
  - Nome completo
  - Email verificado
  - Telefone
  - Foto perfil
  - Dados profissionais

- **Níveis de Acesso**:
  - Administrador
  - Gerente
  - Técnico
  - Operador
  - Consulta

#### Recuperação de Senha
- **Processo Seguro**:
  - Solicitação por email
  - Token temporário
  - Link único
  - Validação dupla
  - Notificações

#### Auditoria
- **Logs de Acesso**:
  - Data/hora
  - IP/Dispositivo
  - Ações realizadas
  - Alterações feitas
  - Tentativas falhas

### 💼 Assinaturas (`/api/assinaturas/`)

#### Planos
- **Níveis Disponíveis**:
  - Básico (até 100 animais)
  - Profissional (até 500 animais)
  - Enterprise (ilimitado)
  - Personalizado

- **Recursos por Plano**:
  - Módulos inclusos
  - Limites de uso
  - Suporte técnico
  - API access
  - Integrações

#### Gestão de Assinaturas
- **Controle**:
  - Status atual
  - Data renovação
  - Histórico pagamentos
  - Faturas pendentes
  - Upgrade/Downgrade

- **Faturamento**:
  - Cobrança automática
  - Múltiplos cartões
  - Nota fiscal
  - Comprovantes
  - Histórico completo

#### Suporte Premium
- **Canais**:
  - Chat 24/7
  - Suporte telefônico
  - Email prioritário
  - Visitas técnicas
  - Treinamentos

## 🛠️ Endpoints da API

### Autenticação
- `POST /api/token/`: Obter token JWT
- `POST /api/token/refresh/`: Renovar token JWT

### Usuários
- `POST /api/usuarios/registrar/`: Registro de novo usuário
- `POST /api/usuarios/login/`: Login
- `POST /api/usuarios/reset_password/`: Solicitar redefinição de senha
- `GET /api/usuarios/me/`: Dados do perfil do usuário

### Cadastros
- `GET/POST /api/cadastros/propriedades/`: Gerenciar propriedades
- `GET/POST /api/cadastros/animais/`: Gerenciar rebanho
- `GET/POST /api/cadastros/pesagens/`: Registros de peso
- `POST /api/cadastros/sync/`: Sincronização de dados offline

### Financeiro
- `GET/POST /api/financeiro/categorias/`: Categorias financeiras
- `GET/POST /api/financeiro/transacoes/`: Transações
- `GET /api/financeiro/transacoes/fluxo_caixa_mensal/`: Relatório mensal
- `GET/POST /api/financeiro/formas-pagamento/`: Métodos de pagamento

### Inteligência
- `GET /api/inteligencia/alertas/`: Listar alertas
- `POST /api/inteligencia/alertas/{id}/marcar_como_resolvido/`: Resolver alerta

### Operacional
- `GET/POST /api/operacional/manejos-sanitarios/`: Registro sanitário
- `GET/POST /api/operacional/registros-reprodutivos/`: Manejo reprodutivo
- `GET/POST /api/operacional/lotes/`: Gestão de lotes
- `GET/POST /api/operacional/piquetes/`: Controle de pastagens

### Rastreabilidade
- `GET/POST /api/rastreabilidade/gerenciar-perfis/`: Perfis públicos
- `GET /api/rastreabilidade/publico/{slug}/`: Visualizar perfil público
- `POST /api/rastreabilidade/gerenciar-perfis/{id}/gerar_qrcode/`: Gerar QR Code

## 🔒 Segurança
- Autenticação via JWT (JSON Web Tokens)
- Permissões baseadas em perfil de usuário
- Segregação de dados por cliente
- Validação de propriedade em todas as operações

## 🤖 Integração com Hardware
- Suporte a leitores RFID
- Balanças eletrônicas
- Sincronização offline-first

## 📋 Requisitos
- Python 3.8+
- Django 4.2+
- PostgreSQL
- Redis (para tarefas assíncronas)

## 📦 Instalação
1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente: `source .venv/bin/activate`
4. Instale as dependências: `pip install -r requirements.txt`
5. Configure as variáveis de ambiente
6. Execute as migrações: `python manage.py migrate`
7. Inicie o servidor: `python manage.py runserver`

## 🌟 Contribuindo
1. Faça um fork do projeto
2. Crie uma branch para sua feature: `git checkout -b feature/nova-feature`
3. Commit suas mudanças: `git commit -m 'Adiciona nova feature'`
4. Push para a branch: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença
Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.