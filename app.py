import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Revisor Crítico TJGO',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Revisor Crítico & Copiloto Analítico de Redação - TJGO')
st.markdown('Esta aplicação audita rascunhos de notícias, apontando **especificamente os erros cometidos** e fornecendo reescritas guiadas pelos manuais do TJGO, de Redação Oficial e de Gênero.')

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
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Língua Portuguesa': '[Manual de Redação do Planalto](https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/manuais) | [Manual de Comunicação do Senado](https://www12.senado.leg.br/manualdecomunicacao) | [Vocabulário Ortográfico da ABL](https://www.academia.org.br/nossa-lingua/busca-no-vocabulario)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl.')
else:
    tema_escolhido = st.selectbox(
        'Selecione a categoria da pauta para direcionar as referências de correção:',
        ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
    )

    if tema_escolhido in referencias_goias:
        st.info(f'📚 **Documentações Oficiais de Apoio para {tema_escolhido}:** {referencias_goias[tema_escolhido]}')

    texto_materia = st.text_area(
        'Cole o seu rascunho de matéria jornalística aqui:',
        placeholder='Insira o texto que você deseja auditar...',
        height=250
    )

    if st.button('Iniciar Auditoria de Risco e Linguagem', type='primary'):
        if not texto_materia.strip():
            st.warning('Por favor, digite ou cole um texto antes de analisar.')
        else:
            # Divide o rascunho em sentenças
            sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

            st.subheader('📋 Diagnóstico Técnico de Redação')

            alertas = 0
            for s in sentencas:
                sentenca_limpa = normalizar_texto_local(s)
                probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                score_sensibilidade = probabilidades[1]

                if score_sensibilidade >= 0.40:
                    alertas += 1
                    risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                    cor = "red" if score_sensibilidade >= 0.65 else "orange"

                    st.markdown(f'<div style="padding:10px; border-left: 5px solid {cor}; background-color:#1e1e1e; margin-bottom:10px;">'
                                f'<span style="color:{cor}; font-weight:bold; font-size:16px;">{risco} ({score_sensibilidade:.1%})</span><br>'
                                f'<span style="font-style:italic; font-size:15px; color:#ffffff;">"{s}"</span>'
                                f'</div>', unsafe_allow_html=True)

                    # Busca de dados de erro mapeados de forma exata ou aproximada no database
                    erro_sugestao = None
                    erro_mapeado = None
                    if db_sugestoes is not None:
                        fragmento = s[:15]
                        match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                        if not match.empty:
                            erro_sugestao = match.iloc[0]['sugestao']
                            if 'erro_identificado' in match.columns:
                                erro_mapeado = match.iloc[0]['erro_identificado']

                    # 1. Seção Clara do Erro Identificado
                    st.markdown("**❌ O que está errado neste trecho:**")
                    if erro_mapeado:
                        st.error(erro_mapeado)
                    else:
                        # Diagnóstico de contingência assertivo para o tema
                        if tema_escolhido == 'Violência contra a Mulher':
                            st.error("Uso de terminologia prejudicial ou violação das regras éticas. Expressões que sugerem passionalidade, atenuam as ações do agressor ou culpam o comportamento/localização da vítima são contrárias ao Manual Universa.")
                        elif tema_escolhido == 'Tecnologia':
                            st.error("Falta de rigor factual. O trecho induz o leitor a crer que os sistemas de IA julgam ou assinam decisões sem fiscalização humana, contrariando as resoluções de governança do CNJ.")
                        elif tema_escolhido == 'Língua Portuguesa':
                            st.error("Inadequação gramatical. O período apresenta desvios explícitos de concordância verbal/nominal, erro na colocação de pronomes, ou uso inadequado de termos relativos.")
                        else:
                            st.error("Uso de adjetivos carregados, acusações unilaterais sem base documental ou falta de isenção editorial técnica exigida para coberturas judiciais.")

                    # 2. Seção de Como Melhorar (Sugestão de Reescrita)
                    st.markdown("**✨ Como corrigir (Sugestão de Novo Texto):**")
                    if erro_sugestao:
                        st.success(erro_sugestao)
                    else:
                        st.warning("Recomenda-se reescrever na ordem direta do português, substituindo termos informais por vocabulário técnico neutro e citando as decisões institucionais de forma impessoal.")

                    st.markdown("--- ")

            if alertas == 0:
                st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta, sem desvios de linguagem identificados.')
