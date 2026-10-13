import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Copiloto Editorial TJGO',
    page_icon='⚖️',
    layout='centered'
)

# Estilização CSS limpa e moderna para criar uma caixa de feedback harmoniosa
st.markdown("""<style>
.reportview-container {
    background: #fafafa;
}
.feedback-box {
    background-color: #f0f4f9;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #d3e3fd;
    color: #1f1f1f;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.7;
}
input, textarea, [data-baseweb="select"] {
    background-color: #ffffff !important;
}
div.stButton > button:first-child {
    background-color: #0b57d0;
    color: white;
    border-radius: 20px;
    padding: 8px 24px;
    font-weight: bold;
    border: none;
}
</style>""", unsafe_allow_html=True)

st.title('⚖️ Revisor Editorial Conversacional')
st.markdown('### Uma conversa de redator para redator, inspirada no Gemini')
st.markdown('Escreva o rascunho da sua pauta jurídica ou geral. O assistente analisará o contexto completo e trará um feedback dissertativo, didático e amigável.')

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
        return joblib.load(modelo_path), joblib.load(database_path)
    except Exception as e:
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos de IA (.pkl). Pratique o retreinamento no notebook.')
else: 
    aba_auditoria, aba_ajuda = st.tabs(['🔍 Analisar Rascunho', '📚 Guia de Fontes Oficiais'])

    with aba_auditoria:
        tema_escolhido = st.selectbox(
            'Qual é o assunto principal da sua matéria?',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        texto_materia = st.text_area('Insira o seu rascunho aqui:', placeholder='Escreva ou cole aqui a pauta para revisão...', height=220)

        if st.button('Revisar com o Copiloto'):
            if not texto_materia.strip():
                st.warning('Por favor, escreva algum rascunho de texto antes de prosseguir.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

                alertas_detectados = []
                sugestoes_banco = []
                sentencas_finais = []

                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.45:
                        alertas_detectados.append(s)
                        # Procura a reescrita mapeada correspondente no pkl de suporte
                        sugestao_mapeada = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty and match.iloc[0]['sugestao'] is not None:
                                sugestao_mapeada = match.iloc[0]['sugestao']

                        if sugestao_mapeada:
                            sugestoes_banco.append(sugestao_mapeada)
                            sentencas_finais.append(sugestao_mapeada)
                        else:
                            sentencas_finais.append(s)
                    else:
                        sentencas_finais.append(s)

                st.markdown('### 🧠 Retorno do Editor Sênior')

                if len(alertas_detectados) == 0:
                    feedback_texto = f"Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.\n\nO tom adotado para tratar sobre **{tema_escolhido}** está perfeitamente neutro, técnico e isento. Você conseguiu transmitir a informação de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional.\n\nSua matéria está pronta e totalmente segura para publicação! Não há necessidade de alterações técnicas ou éticas. Parabéns pelo cuidado com a escrita!"
                else:
                    introducao = f"Olá! Analisei com cuidado o seu rascunho sobre **{tema_escolhido}**.\n\nA ideia central do seu texto está ótima, mas identifiquei alguns pontos de atenção que merecem cuidado para evitar desvios em relação aos manuais de redação, estilo e diretrizes éticas.\n\n"

                    diretrizes = ""
                    if tema_escolhido == 'Violência contra a Mulher':
                        diretrizes = "* **Sobre a abordagem de gênero:** Notei o uso de expressões passionais ou justificativas emocionais ligadas à atitude do agressor (como crises de ciúmes) ou termos antigos como 'crime passional'. O *Manual Universa* orienta que reportagens sobre agressões e feminicídios foquem estritamente na conduta jurídica de forma impessoal e neutra, além de exigir a indicação de canais de socorro (como o Ligue 180).\n\n"
                    elif tema_escolhido == 'Tecnologia':
                        diretrizes = "* **Sobre a precisão e governança algorítmica:** O trecho passa a impressão de que ferramentas de inteligência artificial proferem decisões e assinam julgamentos sozinhas. Conforme a Resolução 332 do CNJ, esses modelos operam puramente como copilotos administrativos para triagem de petições, e a responsabilidade de assinatura reside exclusivamente no magistrado humano.\n\n"
                    elif tema_escolhido == 'Língua Portuguesa':
                        diretrizes = "* **Sobre a estrutura e concordância:** Observei trechos com concordância nominal e verbal vulneráveis, além de construções com pronomes relativos de forma incorreta (como 'cujo o'). Recomendo prezar pela ordem direta na oração para polir a legibilidade e manter o prestígio editorial da redação.\n\n"
                    else:
                        diretrizes = "* **Sobre a neutralidade e isenção de valor:** O texto utiliza jargões informais, juízos de valor opinativos ou faz acusações contra partes sem embasar o andamento do processo técnico correspondente no tribunal.\n\n"

                    detalhe_trechos = "Veja onde esses desvios factuais ou de estilo enfraquecem a neutralidade da pauta:\n"
                    for trecho_alerta in alertas_detectados:
                        # Resolvido o erro de escape de aspas de forma definitiva
                        detalhe_trechos += f"* *'{trecho_alerta}'*\n"

                    reescrita_sugerida = "\n### ✨ Minha proposta de redação corrigida:\nPara deixar o seu texto impecável, isento e com máxima precisão jurídica, sugiro unificar a redação das sentenças sob este formato:\n\n"

                    texto_recomposto_final = " ".join(sentencas_finais)
                    reescrita_sugerida += f"`{texto_recomposto_final}`\n\n"
                    reescrita_sugerida += "O que acha de adotar essa versão? O veículo de imprensa ganha em precisão e o leitor em integridade factual. Estou à disposição para debatermos outros trechos!"

                    feedback_texto = introducao + diretrizes + detalhe_trechos + reescrita_sugerida

                st.markdown(f'<div class="feedback-box">{feedback_texto}</div>', unsafe_allow_html=True)

    with aba_ajuda:
        st.markdown('#### 📚 Portais de Apoio Consultivo')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
