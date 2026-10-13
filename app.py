import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Copiloto Editorial TJGO',
    page_icon='⚖️',
    layout='wide' 
)

# Estilização CSS para aproximar ao layout limpo do Gemini usando aspas simples triplas para evitar colisão
st.markdown('''<style>
.reportview-container {
    background: #fafafa;
}
.stAlert {
    border-radius: 8px;
}
div.stButton > button:first-child {
    background-color: #0b57d0;
    color: white;
    border-radius: 20px;
    padding: 8px 24px;
}
</style>''', unsafe_allow_html=True)

st.title('⚖️ Copiloto Editorial do TJGO')
st.markdown('### Auditoria Editorial Didática — Estilo Gemini')
st.markdown('Este assistente ajuda jornalistas do Tribunal de Justiça de Goiás a revisarem seus rascunhos de forma clara, didática e direta, apontando precisamente os desvios de linguagem e sugerindo reescritas imediatas.')

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
        modelo_path = 'modelo_jornalismo.pkl'
        database_path = 'database_sugestoes.pkl'

        if not os.path.exists(modelo_path):
            modelo_path = '/content/modelo_jornalismo.pkl'
        if not os.path.exists(database_path):
            database_path = '/content/database_sugestoes.pkl'

        modelo = joblib.load(modelo_path)
        database = joblib.load(database_path)
        return modelo, database
    except Exception as e:
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Língua Portuguesa': '[Manual de Redação da Presidência da República](https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/manuais) | [Manual de Comunicação do Senado](https://www12.senado.leg.br/manualdecomunicacao)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Componentes de IA (.pkl) ausentes. Execute as células de treinamento do Colab.')
else:
    aba_auditoria, aba_ajuda = st.tabs(['🔍 Analisar Rascunho', '📚 Guia de Fontes Oficial'])

    with aba_auditoria:
        st.markdown('#### Digite ou cole o seu rascunho de reportagem abaixo:')
        tema_escolhido = st.selectbox(
            'Pauta da matéria:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
        )

        texto_materia = st.text_area('', placeholder='Comece a escrever sua reportagem aqui para que eu revise...', height=200)

        if st.button('Analisar Matéria', type='primary'):
            if not texto_materia.strip():
                st.warning('Escreva um rascunho de texto antes de analisar.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]
                st.markdown('### 📋 Análise e Propostas de Ajustes')

                alertas = 0
                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas += 1
                        risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                        cor = "#EA4335" if score_sensibilidade >= 0.65 else "#FBBC05"

                        st.markdown(f'''
                        <div style="padding:10px; margin-top:15px; border-left: 5px solid {cor}; background-color:#1e1e1e; border-radius:4px;">
                            <span style="color:{cor}; font-weight:bold; font-size:15px;">{risco} (Sensibilidade: {score_sensibilidade:.1%})</span><br>
                            <span style="color:#ffffff; font-style:italic;">"{s}"</span>
                        </div>
                        ''', unsafe_allow_html=True)

                        # Procura no banco de dados a justificativa e correção pré-mapeada
                        sugestao = None
                        justificativa_erro = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao = match.iloc[0]['sugestao']
                                if 'justificativa' in match.columns:
                                    justificativa_erro = match.iloc[0]['justificativa']
                                elif 'erro_identificado' in match.columns:
                                    justificativa_erro = match.iloc[0]['erro_identificado']

                        # Apresentação lado a lado (Estilo Colunas Gemini)
                        col_erro, col_correcao = st.columns(2)

                        with col_erro:
                            st.markdown("**❌ O que está errado:**")
                            if justificativa_erro:
                                st.info(justificativa_erro)
                            else:
                                if tema_escolhido == 'Violência contra a Mulher':
                                    st.info("Violação das regras éticas. O trecho pode atenuar a gravidade do crime de gênero justificando a conduta do agressor ou transferindo culpa à vítima, infringindo as orientações do Manual Universa.")
                                elif tema_escolhido == 'Tecnologia':
                                    st.info("Desinformação de governança. Sugerir que a Inteligência Artificial julga autonomamente processos fere os preceitos éticos da Resolução 332 do CNJ.")
                                elif tema_escolhido == 'Língua Portuguesa':
                                    st.info("Inadequação gramatical. O trecho apresenta desvios explícitos de concordância ou regência conforme as normas formais de escrita oficial.")
                                else:
                                    st.info("Uso de adjetivação desnecessária ou julgamento prévio sem isenção editorial técnica.")

                        with col_correcao:
                            st.markdown("**✨ Como corrigir (Versão Sugerida):**")
                            if sugestao:
                                st.success(sugestao)
                            else:
                                st.warning("Reescreva de forma objetiva na ordem direta, evitando adjetivos pessoais, jargões excessivos e mantendo o tom estritamente impessoal.")
                        st.markdown("--- ")

                if alertas == 0:
                    st.success('✅ **Excelente!** O texto analisado atende integralmente ao tom impessoal, técnico e isento exigido para coberturas institucionais.')

    with aba_ajuda:
        st.markdown('#### 📚 Portais de Referência e Manuais do Judiciário')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
