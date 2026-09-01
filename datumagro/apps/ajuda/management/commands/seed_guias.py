from django.core.management.base import BaseCommand
from datumagro.apps.ajuda.models import GuiaModulo

E = GuiaModulo.Especie

GUIAS = [
    # ── Dashboard ────────────────────────────────────────────────────────────
    dict(
        modulo_slug="dashboard", especie=E.GLOBAL, ordem=0,
        titulo="Dashboard — Visão Geral da Fazenda",
        como_usar_passo_a_passo=(
            "1. O dashboard mostra os principais indicadores da sua fazenda em tempo real.\n"
            "2. Os cards no topo exibem total de animais, propriedades e alertas ativos.\n"
            "3. Toque em qualquer card para navegar direto ao módulo correspondente.\n"
            "4. Use os ícones no menu inferior para acessar Animais, Financeiro, Alertas e Perfil.\n"
            "5. O botão de ajuda (?) em cada tela abre este guia contextual."
        ),
        dicas_agronomicas_zootecnicas=(
            "Acesse o dashboard diariamente antes de ir ao campo. Ele concentra os alertas "
            "mais urgentes — vacinas vencendo, animais sem pesagem recente e metas financeiras — "
            "permitindo que você priorize as tarefas do dia sem precisar navegar módulo por módulo."
        ),
    ),

    # ── Animais ───────────────────────────────────────────────────────────────
    dict(
        modulo_slug="animals", especie=E.GLOBAL, ordem=0,
        titulo="Cadastro e Gestão de Animais",
        como_usar_passo_a_passo=(
            "1. Toque no + para cadastrar um novo animal.\n"
            "2. Preencha o identificador (brinco RFID, tatuagem ou nome), raça, sexo e data de nascimento.\n"
            "3. Use o filtro de sexo e categoria para localizar animais rapidamente.\n"
            "4. Toque no nome do animal para ver o histórico completo: pesagens, sanitário e reprodutivo.\n"
            "5. O ícone de QR/barcode no topo escaneia brincos diretamente pela câmera."
        ),
        dicas_agronomicas_zootecnicas=(
            "Mantenha o cadastro atualizado com categoria e aptidão corretos — isso permite "
            "que o sistema gere alertas precisos (ex: novilhas em idade de cobertura, "
            "matrizes próximas ao parto) e relatórios de desempenho por grupo de animais."
        ),
    ),
    dict(
        modulo_slug="animals", especie=E.EQUINO, ordem=0,
        titulo="Cadastro de Equinos",
        como_usar_passo_a_passo=(
            "1. Cadastre o animal informando Nome/Registro, raça e data de nascimento.\n"
            "2. Selecione a aptidão: Trabalho, Esporte ou Reprodução.\n"
            "3. Para reprodutores, ative a opção 'É Reprodutor' para rastrear cobertas.\n"
            "4. Acesse o detalhe do animal para ver histórico de casqueamento e vermifugação."
        ),
        dicas_agronomicas_zootecnicas=(
            "Registre o escore de condição corporal (ECC) a cada pesagem. "
            "Mantenha reprodutores entre ECC 5 e 6 para garantir fertilidade adequada "
            "e evitar problemas metabólicos como laminite por excesso de peso."
        ),
    ),
    dict(
        modulo_slug="animals", especie=E.SUINO, ordem=0,
        titulo="Cadastro de Suínos",
        como_usar_passo_a_passo=(
            "1. Identifique o animal por tatuagem ou brinco auricular.\n"
            "2. Registre a fase de produção: Leitão, Crescimento, Terminação ou Reprodução.\n"
            "3. Associe o animal a uma baia ou lote para facilitar o manejo por grupo.\n"
            "4. Registre pesagens regulares para acompanhar a Conversão Alimentar (CA) da baia."
        ),
        dicas_agronomicas_zootecnicas=(
            "Suínos em terminação devem atingir 90–100 kg em 150–170 dias com CA entre 2,4 e 2,8. "
            "Se a CA estiver alta, verifique desperdício nos comedouros automáticos e "
            "a qualidade nutricional da ração (lisina disponível e energia metabolizável)."
        ),
    ),
    dict(
        modulo_slug="animals", especie=E.OVINO_CAPRINO, ordem=0,
        titulo="Cadastro de Ovinos e Caprinos",
        como_usar_passo_a_passo=(
            "1. Identifique o animal por brinco auricular ou colar numerado.\n"
            "2. Informe a raça, sexo e categoria (Cordeiro/Cabrito, Borrego, Ovelha, Cabra, Carneiro, Bode).\n"
            "3. Para matrizes, registre o status reprodutivo (vazia, prenha, em lactação).\n"
            "4. Registre o score FAMACHA na aba sanitária para controle de verminose."
        ),
        dicas_agronomicas_zootecnicas=(
            "O principal problema sanitário em pequenos ruminantes é a verminose por Haemonchus. "
            "Aplique o método FAMACHA quinzenalmente na estação chuvosa e vermifugue seletivamente "
            "apenas os animais com mucosa ocular em escore 3, 4 ou 5 para retardar a resistência anti-helmíntica."
        ),
    ),

    # ── Mapa / GIS ──────────────────────────────────────────────────────────
    dict(
        modulo_slug="mapa", especie=E.GLOBAL, ordem=0,
        titulo="Mapeamento e Piquetes",
        como_usar_passo_a_passo=(
            "1. Acesse a aba Mapeamento no dashboard.\n"
            "2. Toque em Importar CAR e informe o código do imóvel — o polígono oficial "
            "é desenhado automaticamente.\n"
            "3. Toque em + Desenhar Piquete e vá adicionando pontos na tela para fechar "
            "a área. Dê um nome ao pasto ou talhão.\n"
            "4. Alterne para o modo Infraestrutura para marcar bebedouros, cochos e cercas.\n"
            "5. Toque em Salvar para enviar as camadas ao servidor."
        ),
        dicas_agronomicas_zootecnicas=(
            "Pecuária: calcule a lotação real em UA/ha usando apenas a Área Útil "
            "(descontando APP e Reserva Legal) para não sobrecarregar o pasto na seca.\n"
            "Agricultura: ao desenhar linhas de plantio, oriente a semeadura em nível "
            "(perpendicular à declividade) para reduzir erosão e economizar combustível."
        ),
    ),
    dict(
        modulo_slug="mapa", especie=E.TERRA, ordem=0,
        titulo="Mapeamento de Talhões e Linhas de Plantio",
        como_usar_passo_a_passo=(
            "1. Importe o polígono da propriedade pelo CAR ou desenhe os talhões direto "
            "no mapa tocando nos vértices.\n"
            "2. Nomeie cada talhão e registre a cultura plantada.\n"
            "3. Use o modo Infraestrutura para marcar estradas, silos e pivôs."
        ),
        dicas_agronomicas_zootecnicas=(
            "Planeje o rodízio de culturas por talhão — a rotação soja/milho/palhada "
            "melhora a matéria orgânica do solo e reduz a pressão de pragas ao longo "
            "das safras."
        ),
    ),

    # ── Pesagem ──────────────────────────────────────────────────────────────
    dict(
        modulo_slug="pesagem", especie=E.GLOBAL, ordem=0,
        titulo="Pesagem e Ganho de Peso",
        como_usar_passo_a_passo=(
            "1. Acesse Controle de Pesagem → Nova Pesagem.\n"
            "2. Conecte a balança Bluetooth ou informe o peso manualmente.\n"
            "3. Identifique o animal pelo brinco RFID, tatuagem ou número visual.\n"
            "4. Salve — o app calcula o Ganho Médio Diário (GMD) automaticamente "
            "comparando com a pesagem anterior."
        ),
        dicas_agronomicas_zootecnicas=(
            "GMD abaixo de 0,500 kg/dia na terminação de bovinos de corte indica "
            "deficiência nutricional. Avalie reforçar a suplementação proteica/energética "
            "no cocho ou verifique infestação de parasitas."
        ),
    ),
    dict(
        modulo_slug="pesagem", especie=E.SUINO, ordem=0,
        titulo="Pesagem e Conversão Alimentar",
        como_usar_passo_a_passo=(
            "1. Identifique a baia ou lote na tela de Pesagem.\n"
            "2. Registre o peso (balança Bluetooth ou manual) e a ração consumida "
            "no período.\n"
            "3. O app calcula a Conversão Alimentar (CA) da baia automaticamente."
        ),
        dicas_agronomicas_zootecnicas=(
            "Monitore a CA de cada baia. Se ela subir acima de 2,8 na terminação, "
            "verifique desperdício nos comedouros automáticos e qualidade nutricional "
            "da ração."
        ),
    ),
    dict(
        modulo_slug="pesagem", especie=E.EQUINO, ordem=0,
        titulo="Pesagem e Condição Corporal Equina",
        como_usar_passo_a_passo=(
            "1. Acesse Pesagem e selecione o cavalo pelo microchip ou nome.\n"
            "2. Registre o peso e o Escore de Condição Corporal (ECC) de 1 a 9.\n"
            "3. Acompanhe a curva de peso no histórico do animal."
        ),
        dicas_agronomicas_zootecnicas=(
            "O ECC ideal para equinos em trabalho é entre 5 e 6. Abaixo de 4 indica "
            "déficit energético — aumente o fornecimento de volumoso e concentrado. "
            "Acima de 7, reduza a ração e aumente o exercício para evitar laminite."
        ),
    ),

    # ── Sanitário ─────────────────────────────────────────────────────────────
    dict(
        modulo_slug="sanitario", especie=E.GLOBAL, ordem=0,
        titulo="Manejo Sanitário e Vacinação",
        como_usar_passo_a_passo=(
            "1. Acesse Manejo Sanitário → Nova Aplicação.\n"
            "2. Selecione o produto (vacina, vermífugo ou antibiótico), o lote e a "
            "dosagem por cabeça (ml ou mg/kg).\n"
            "3. O app registra o histórico e calcula automaticamente a data de fim "
            "da carência sanitária.\n"
            "4. Um alerta é gerado quando a carência vence ou a próxima dose se aproxima."
        ),
        dicas_agronomicas_zootecnicas=(
            "Respeite o período de carência do medicamento antes de enviar animais "
            "para o abate ou comercializar o leite — a violação gera interdição do lote "
            "e multas junto ao MAPA."
        ),
    ),
    dict(
        modulo_slug="sanitario", especie=E.OVINO_CAPRINO, ordem=0,
        titulo="Manejo Sanitário — Ovinos e Caprinos",
        como_usar_passo_a_passo=(
            "1. Acesse Manejo Sanitário → Nova Aplicação.\n"
            "2. Avalie a mucosa ocular pelo método FAMACHA (1 a 5) antes de vermifugar.\n"
            "3. Registre o escore FAMACHA de cada animal e aplique o vermífugo apenas "
            "nos escores 3, 4 e 5."
        ),
        dicas_agronomicas_zootecnicas=(
            "Vermifugar o rebanho inteiro sem necessidade acelera a resistência "
            "anti-helmíntica dos vermes. Trate seletivamente pelo FAMACHA e faça "
            "coproparasitológico periódico (OPG) para monitorar a eficácia."
        ),
    ),

    # ── Reprodutivo ──────────────────────────────────────────────────────────
    dict(
        modulo_slug="reprodutivo", especie=E.GLOBAL, ordem=0,
        titulo="Controle Reprodutivo",
        como_usar_passo_a_passo=(
            "1. Acesse Controle Reprodutivo → Novo Evento.\n"
            "2. Selecione o animal e o tipo de evento: cobertura, IATF, palpação, "
            "parto ou descarte reprodutivo.\n"
            "3. Registre o touro/sêmen utilizado e a data.\n"
            "4. O app calcula o diagnóstico de gestação esperado (DG) e gera alerta "
            "30 dias antes da data prevista de parto."
        ),
        dicas_agronomicas_zootecnicas=(
            "O intervalo entre partos ideal para bovinos de corte é de 12 meses. "
            "Fêmeas com IEP acima de 14 meses comprometem a eficiência reprodutiva "
            "do rebanho — revise o estado nutricional no pré-parto e o escore "
            "corporal ao parto (ideal: 3,0 a 3,5)."
        ),
    ),

    # ── Financeiro ────────────────────────────────────────────────────────────
    dict(
        modulo_slug="financeiro", especie=E.GLOBAL, ordem=0,
        titulo="Controle Financeiro da Fazenda",
        como_usar_passo_a_passo=(
            "1. Acesse Financeiro → Nova Movimentação.\n"
            "2. Selecione o tipo: Receita (venda de animais, leite, grãos) ou "
            "Despesa (ração, medicamentos, mão de obra).\n"
            "3. Informe o valor, a categoria e a data.\n"
            "4. O dashboard financeiro atualiza o fluxo de caixa e a margem por "
            "atividade automaticamente."
        ),
        dicas_agronomicas_zootecnicas=(
            "Separe os centros de custo por atividade (corte, leite, lavoura) para "
            "saber qual gera mais resultado. O custo com alimentação costuma "
            "representar 60 a 70% do custo total de produção na pecuária de corte — "
            "monitore o custo do arroba produzida mensalmente."
        ),
    ),

    # ── Passaporte Sanitário ──────────────────────────────────────────────────
    dict(
        modulo_slug="passaporte_sanitario", especie=E.GLOBAL, ordem=0,
        titulo="Passaporte Sanitário",
        como_usar_passo_a_passo=(
            "1. Selecione o lote destinado ao abate, venda ou exportação.\n"
            "2. Toque em Gerar Passaporte Sanitário — o app reúne o histórico vacinal "
            "e verifica a conformidade com os protocolos do MAPA.\n"
            "3. Se aprovado, um PDF com QR Code é gerado para apresentar à fiscalização "
            "ou frigorífico."
        ),
        dicas_agronomicas_zootecnicas=(
            "Para exportação, cada país de destino tem exigências vacinais próprias "
            "(CZI). Alguns mercados, como a União Europeia, exigem rastreabilidade "
            "individual do brinco RFID até o frigorífico — certifique-se de que "
            "todos os animais do lote têm o histórico completo registrado no sistema."
        ),
    ),

    # ── Lotes ─────────────────────────────────────────────────────────────────
    dict(
        modulo_slug="lotes", especie=E.GLOBAL, ordem=0,
        titulo="Gestão de Lotes",
        como_usar_passo_a_passo=(
            "1. Acesse Lotes → Novo Lote.\n"
            "2. Nomeie o lote e selecione os animais que o compõem.\n"
            "3. Associe o lote a um piquete ou baia.\n"
            "4. Todos os registros de pesagem, sanitário e reprodutivo podem ser "
            "feitos por lote para agilizar o manejo em campo."
        ),
        dicas_agronomicas_zootecnicas=(
            "Agrupe animais por categoria (bezerros, novilhas, vacas, touros) e fase "
            "de produção. Lotes homogêneos em peso e categoria respondem melhor ao "
            "manejo nutricional e sanitário uniforme."
        ),
    ),
]


class Command(BaseCommand):
    help = "Popula a base de conhecimento com o conteúdo inicial de cada módulo do DatumAgro"

    def handle(self, *args, **options):
        criados, atualizados = 0, 0
        for guia in GUIAS:
            _, created = GuiaModulo.objects.update_or_create(
                modulo_slug=guia["modulo_slug"],
                especie=guia["especie"],
                defaults=guia,
            )
            criados += int(created)
            atualizados += int(not created)
        self.stdout.write(
            self.style.SUCCESS(
                f"Guias processados: {criados} criados, {atualizados} atualizados."
            )
        )
