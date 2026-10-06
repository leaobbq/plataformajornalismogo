import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Revisor Analítico TJGO - Padrão Gemini',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto Analítico de Redação - Padrão Gemini (TJGO)')
st.markdown('Esta aplicação realiza a auditoria avançada de rascunhos de matérias dividindo as avaliações de sensibilidade, justificativas e regras de redação do TJGO.')

# Função local de normalização que limpa a frase antes de enviar ao modelo preditor
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
        modelo_path = '/content/modelo_jornalismo.pkl'
        database_path = '/content/database_sugestoes.pkl'

        if not os.path.exists(modelo_path):
            modelo_path = 'modelo_jornalismo.pkl'
        if not os.path.exists(database_path):
            database_path = 'database_sugestoes.pkl'

        modelo = joblib.load(modelo_path)
        database = joblib.load(database_path)
        return modelo, database
    except Exception as e:
        st.sidebar.error(f"Erro de leitura de dados: {e}")
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnico': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Língua Portuguesa': '[Manual de Redação da Presidência da República](https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/manuais) | [Manual de Comunicação do Senado](https://www12.senado.leg.br/manualdecomunicacao) | [Vocabulário Ortográfico da ABL](https://www.academia.org.br/nossa-lingua/busca-no-vocabulario)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos de Inteligência Artificial (.pkl).')
else:
    aba_auditoria, aba_modelos = st.tabs(['🔍 Auditoria e Revisão de Texto', '💡 Gerador de Sugestões / Textos Base'])

    with aba_auditoria:
        st.header('Auditoria e Feedback Estilo Gemini')
        tema_escolhido = st.selectbox(
            'Selecione a categoria da pauta para direcionar as referências:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnico', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
        )

        if tema_escolhido in referencias_goias:
            st.info(f'📚 **Documentações Oficiais de Apoio para {tema_escolhido}:** {referencias_goias[tema_escolhido]}')

        texto_materia = st.text_area(
            'Cole o seu rascunho de matéria jornalística aqui:',
            placeholder='Insira o rascunho da sua reportagem...',
            height=250
        )

        if st.button('Iniciar Auditoria de Risco e Linguagem', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite ou cole um texto antes de analisar.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

                st.subheader('📋 Relatório Analítico de Redação')

                alertas = 0
                for s in sentencas:
                    # 1. Normalizar o input antes de passar para o predict do Vectorizer do pipeline
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas += 1
                        risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                        cor = "red" if score_sensibilidade >= 0.65 else "orange"

                        st.markdown(f'<p style="color:{cor}; font-size:18px; font-weight:bold;">{risco} ({score_sensibilidade:.1%}): "{s}"</p>', unsafe_allow_html=True)

                        # Busca exata ou aproximada por sugestões no database
                        sugestao = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao = match.iloc[0]['sugestao']

                        # Retorno estruturado imitando o Gemini (Problema + Correção)
                        st.markdown("**❌ O que está errado:**")
                        if tema_escolhido == 'Violência contra a Mulher':
                            st.write("O trecho pode ferir as diretrizes do Manual Universa ao utilizar justificativas sentimentais para crimes (como ciúmes), usar termos desatualizados como 'crime passional' ou faltar a indicação do Ligue 180.")
                        elif tema_escolhido == 'Tecnologia':
                            st.write("O texto apresenta risco ao dar a entender que a tecnologia ou algoritmos de IA decidem sentenças de forma isolada, ignorando o papel constitucional exclusivo e a revisão dos magistrados do TJGO.")
                        else:
                            st.write("O trecho apresenta acusações subjetivas, parcialidade evidente ou falta com o rigor jornalístico de ouvir todas as partes.")

                        if sugestao:
                            st.markdown(f"**✨ Sugestão de Reescrita Correta:** `{sugestao}`")
                        else:
                            st.markdown("**✨ Recomendação Geral:** Readequar a linguagem para termos técnicos-jurídicos neutros, removendo adjetivos pessoais ou termos coloquiais.")
                        st.write('---')

                if alertas == 0:
                    st.success('✅ **Excelente!** O rascunho analisado atende perfeitamente ao tom neutro, isento e com a terminologia recomendada de acordo com as regras de redação da editoria e do TJGO.')
