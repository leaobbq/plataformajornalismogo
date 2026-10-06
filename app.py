import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata

st.set_page_config(
    page_title='Auditor de Redação TJGO',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Auditor Editorial do TJGO')
st.markdown('Ferramenta analítica de Processamento de Linguagem Natural (NLP) e diretrizes regulatórias para apoiar jornalistas na redação de pautas com máxima clareza, neutralidade e precisão jurídica.')

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
    exceptException as e:
        st.sidebar.error(f"Erro de leitura de dados: {e}")
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Centro de Inovação e Governança de IA do TJGO](https://www.tjgo.jus.br/index.php/centro-de-inteligencia)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos de Inteligência Artificial (.pkl) no servidor de nuvem.')
else:
    tema_escolhido = st.selectbox(
        'Selecione a categoria da pauta a ser analisada:',
        ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
    )

    if tema_escolhido in referencias_goias:
        st.info(f'📚 **Documentações Oficiais e Fontes Oficiais:** {referencias_goias[tema_escolhido]}')

    texto_materia = st.text_area(
        'Rascunho do jornalista para auditoria ética e jurídica:',
        placeholder='Escreva ou cole aqui a matéria jornalística...',
        height=250
    )

    if st.button('Iniciar Auditoria Editorial Avançada', type='primary'):
        if not texto_materia.strip():
            st.warning('Insira o texto para análise.')
        else:
            # Divisão por sentenças respeitando pontuações
            sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

            st.subheader('📋 Diagnóstico Técnico de Sensibilidade e Viés')

            alertas = 0
            for s in sentencas:
                sentenca_limpa = normalizar_texto_local(s)
                probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                score_sensibilidade = probabilidades[1]

                if score_sensibilidade >= 0.40:
                    alertas += 1
                    risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                    cor_markdown = "red" if score_sensibilidade >= 0.65 else "orange"

                    st.markdown(f'<p style="color:{cor_markdown}; font-size:18px; font-weight:bold;">{risco} ({score_sensibilidade:.1%}): "{s}"</p>', unsafe_allow_html=True)

                    # Busca exata ou por fragmento de apoio
                    sugestao = None
                    justificativa = None
                    if db_sugestoes is not None:
                        fragmento = s[:15]
                        match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                        if not match.empty:
                            sugestao = match.iloc[0]['sugestao']
                            justificativa = match.iloc[0]['justificativa']

                    # Feedback enriquecido e didático
                    if justificativa:
                        st.markdown(f"🔍 **Justificativa Editorial:** {justificativa}")
                    else:
                        st.markdown("🔍 **Justificativa Editorial:** O trecho apresenta termos carregados, expressões informais, passíveis de duplo sentido ou acusações subjetivas de parcialidade sem citar fontes oficiais ou dados técnicos concretos.")

                    if sugestao:
                        st.success(f"✨ **Sugestão de Redação Alinhada:** {sugestao}")
                    else:
                        st.warning("💡 **Recomendação de Adequação:** Prefira redações que utilizem terminologia técnica, citem atos oficiais publicados no Diário da Justiça de Goiás e que ouçam com imparcialidade todas as partes envolvidas no processo.")
                    
                    st.write('---')

            if alertas == 0:
                st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta, isenção factual e linguagem recomendada pelo TJGO.')
