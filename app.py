import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata

st.set_page_config(
    page_title='Revisor Ultra Assertivo TJGO',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Revisor de Alta Precisão - TJGO')
st.markdown('Utilizando Processamento de Linguagem Natural (NLP) otimizado para garantir a máxima integridade técnica nas coberturas do TJGO.')

def normalizar_texto_local(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = re.sub(r'[^a-zA-Z0-9\s]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

@st.cache_resource
def carregar_recursos():
    try:
        modelo = joblib.load('modelo_jornalismo.pkl')
        database = joblib.load('database_sugestoes.pkl')
        return modelo, database
    except Exception as e:
        st.sidebar.error(f"Erro de leitura na nuvem: {e}")
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[TJGO - Portal de Precatórios Oficiais](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[TJGO - Sistemas, Manuais e Avisos de Indisponibilidade](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[TJGO - Consulta Unificada de Jurisprudência e Súmulas](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[TJGO - Comitê Estadual de Saúde e Pareceres do NATJUS](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[TJGO - Centro de Inteligência e Projetos de Inovação](https://www.tjgo.jus.br/index.php/centro-de-inteligencia)',
    'Violência contra a Mulher': '[TJGO - Coordenadoria Estadual da Mulher](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

modelos_textos_base = {
    'Precatórios': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) divulgou nesta semana a atualização do cronograma de pagamento de precatórios para o exercício vigente. "
        "Segundo a Diretoria de Precatórios do órgão, os repasses aos credores prioritários (como idosos e pessoas com deficiência) seguem de forma regular, "
        "respeitando rigorosamente a ordem cronológica e os aportes financeiros estabelecidos pelo ente devedor estatal."
    ),
    'Alterações no Projudi': (
        "Devido a uma manutenção corretiva programada nos servidores da Diretoria de Tecnologia da Informação do TJGO, o sistema Projudi registrou períodos de oscilação técnica. "
        "Para mitigar eventuais prejuízos aos prazos processuais da advocacia, o Tribunal emitiu certidão de indisponibilidade oficial e decretou de forma automática a prorrogação dos prazos."
    ),
    'Precedentes Judiciais': (
        "Em decisão recente proferida pela Seção Cível do Tribunal de Justiça de Goiás (TJGO), fixou-se tese em sede de Incidente de Resolução de Demandas Repetitivas (IRDR). "
        "O entendimento uniformiza as decisões de primeira instância no estado de Goiás sobre [inserir tema específico do processo] e servirá como precedente obrigatório para casos análogos."
    ),
    'Saúde Técnica': (
        "O Poder Judiciário goiano acolheu, em caráter liminar, o pedido para fornecimento de tratamento de saúde especializado na comarca de Goiânia. "
        "Na decisão, o magistrado fundamentou a necessidade do fornecimento com base no parecer técnico favorável emitido pelo Núcleo de Apoio Técnico do Judiciário (NATJUS), garantindo segurança baseada em evidência científica."
    ),
    'Tecnologia': (
        "O Centro de Inteligência do TJGO iniciou o piloto de uma nova ferramenta de automação por Inteligência Artificial voltada à triagem prévia de processos em massa. "
        "A tecnologia funciona de forma estritamente auxiliar ao fluxo de trabalho, mantendo todas as etapas de julgamento sob supervisão, revisão direta e assinatura do magistrado competente."
    ),
    'Violência contra a Mulher': (
        "O Ministério Público de Goiás, em atuação conjunta com a Coordenadoria Estadual da Mulher do TJGO, formalizou a denúncia contra o suspeito de agressão na comarca de [Cidade]. "
        "O juízo deferiu de imediato medidas protetivas de urgência previstas na Lei Maria da Penha para afastar o agressor e garantir a integridade da vítima. "
        "---\n📞 Se você ou alguém próximo vivencia situações de violência doméstica, denuncie: ligue de forma gratuita e anônima para o Ligue 180 ou acione a Polícia Militar pelo 190."
    )
}

if modelo_local is None:
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl.')
else:
    aba_auditoria, aba_modelagem = st.tabs(['🔍 Auditoria e Revisão de Texto', '💡 Gerador de Sugestões / Textos Base'])

    with aba_auditoria:
        st.header('Revisão e Análise Automática de Parágrafos')
        tema_escolhido = st.selectbox(
            'Escolha a categoria da matéria jurídica para auditar:',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        if tema_escolhido in referencias_goias:
            st.info(f'📚 **Fonte Técnica de Consulta recomendada para Goiás:** {referencias_goias[tema_escolhido]}')

        texto_materia = st.text_area(
            'Insira a matéria completa ou o rascunho de parágrafo:',
            placeholder='Escreva aqui o rascunho para submeter à auditoria avançada...',
            height=250
        )

        if st.button('Auditar Texto com Alta Precisão', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite algum texto para análise.')
            else:
                sentencas = [s.strip() for s in re.split(r'[.!?\n]+', texto_materia) if len(s.strip()) > 5]

                st.subheader('📊 Relatório de Auditoria de Linguagem')

                alertas_detectados = 0
                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    percentual_sensibilidade = probabilidades[1]

                    if percentual_sensibilidade >= 0.65:
                        alertas_detectados += 1
                        st.error(f'🚨 **RISCO CRÍTICO ({percentual_sensibilidade:.1%}):** {s}')

                        sugestao = None
                        if db_sugestoes is not None:
                            snippet = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(snippet), na=False, case=False)]
                            if not match.empty and match.iloc[0]['sugestao'] is not None:
                                sugestao = match.iloc[0]['sugestao']

                        if sugestao:
                            st.success(f'💡 **Sugestão de Reescrita Recomendada:** {sugestao}')
                        else:
                            st.info('💡 **Recomendação:** Remova julgamentos de valor, evite culpar partes e apoie-se estritamente na redação processual do TJGO.')
                        st.write('---')

                    elif percentual_sensibilidade >= 0.45:
                        alertas_detectados += 1
                        st.warning(f'⚠️ **RISCO MODERADO ({percentual_sensibilidade:.1%}):** {s}')
                        st.info('💡 **Aviso:** O texto está próximo da linha da parcialidade ou utiliza termos vagos. Certifique-se de citar as fontes oficiais e o andamento processual correto do tribunal.')
                        st.write('---')

                if alertas_detectados == 0:
                    st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta e linguagem ética recomendada pelo TJGO.')

    with aba_modelagem:
        st.header('💡 Sugestão de Textos e Modelos de Redação')
        st.write('Selecione uma categoria abaixo para obter um texto-modelo estruturado de forma imparcial, clara e perfeitamente ajustada às boas práticas do jornalismo e do TJGO.')

        tema_modelo = st.selectbox(
            'Selecione o tema para gerar a sugestão de redação:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        if tema_modelo in modelos_textos_base:
            st.subheader(f'📝 Modelo de Redação Recomendado: {tema_modelo}')
            texto_sugerido = modelos_textos_base[tema_modelo]
            st.text_area('Copie o texto base sugerido abaixo:', value=texto_sugerido, height=180)
            st.info('👉 **Nota para o jornalista:** Lembre-se de substituir os dados genéricos pelos fatos reais apurados.')
