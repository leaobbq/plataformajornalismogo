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
.destaque-erro {
    background-color: #fde8e8;
    color: #9b1c1c;
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 6px solid #f05252;
    margin: 8px 0;
    font-weight: bold;
}
.destaque-correcao {
    background-color: #def7ec;
    color: #03543f;
    padding: 12px 16px;
    border-radius: 8px;
    border-left: 6px solid #31c48d;
    margin: 8px 0;
    font-weight: bold;
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
st.markdown('Escreva o rascunho da sua pauta jurídica ou geral. O assistente analisará o contexto completo e trará um feedback dissertativo, apontando os erros de forma clara antes de sugerir a versão corrigida.')

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
    except:
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
                detalhes_analise = []
                sentencas_finais = []

                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.45:
                        alertas_detectados.append(s)
                        sugestao_mapeada = None
                        justificativa_mapeada = None

                        if db_sugestoes is not None:
                            db_sugestoes['texto_normalizado'] = db_sugestoes['texto'].apply(normalizar_texto_local)
                            match = db_sugestoes[db_sugestoes["texto_normalizado"] == sentenca_limpa]
                            if not match.empty:
                                sugestao_mapeada = match.iloc[0]['sugestao']
                                if 'erro_identificado' in match.columns:
                                    justificativa_mapeada = match.iloc[0]['erro_identificado']
                                elif 'justificativa' in match.columns:
                                    justificativa_mapeada = match.iloc[0]['justificativa']

                        if not justificativa_mapeada:
                            if tema_escolhido == 'Violência contra a Mulher':
                                justificativa_mapeada = 'Uso de expressões sentimentais ou passionalidade que podem de alguma forma culpar a conduta da vítima ou atenuar o ato do agressor de gênero, infringindo as diretrizes do Manual Universa.'
                            elif tema_escolhido == 'Tecnologia':
                                justificativa_mapeada = 'O período apresenta vulnerabilidade técnica ao insinuar que a IA profere julgamentos de forma isolada, infringindo os limites éticos de governança da Resolução 332 do CNJ.'
                            else:
                                justificativa_mapeada = 'O trecho apresenta adjetivos de teor subjetivo ou termos coloquiais desajustados para a cobertura técnica e impessoal de processos jurídicos.'

                        detalhes_analise.append({
                            'original': s,
                            'erro': justificativa_mapeada,
                            'sugestao': sugestao_mapeada
                        })

                        if sugestao_mapeada:
                            sentencas_finais.append(sugestao_mapeada)
                        else:
                            sentencas_finais.append(s)
                    else:
                        sentencas_finais.append(s)

                st.markdown('### 🧠 Retorno do Editor Sênior')

                if len(alertas_detectados) == 0:
                    feedback_texto = f"Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.\\n\\nO tom adotado para tratar sobre **{tema_escolhido}** está perfeitamente neutro, técnico e isento. Você conseguiu transmitir a informação factual de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional de tribunais.\\n\\nSua matéria está impecável e totalmente segura para publicação! Parabéns pelo excelente trabalho de escrita!"
                    st.markdown(f'<div class="feedback-box">{feedback_texto}</div>', unsafe_allow_html=True)
                else:
                    introducao_texto = f"Olá! Analisei com cuidado o seu rascunho sobre **{tema_escolhido}**.\\n\\nA ideia central do seu texto está ótima, mas identifiquei alguns pontos de atenção que merecem cuidado para evitar desvios em relação aos manuais de redação, estilo e diretrizes éticas.\\n\\nAbaixo listo de forma transparente o impacto que esses pontos causam na fluidez do seu rascunho:"
                    st.markdown(f'<div class="feedback-box">{introducao_texto}</div>', unsafe_allow_html=True)
                    st.write("")

                    # EXPOSIÇÃO DINÂMICA DE ERROS E SUGESTÕES
                    st.markdown('### 🔍 Mapeamento e Destaques de Alterações')
                    for idx, item in enumerate(detalhes_analise):
                        st.markdown(f"#### 📌 Parágrafo/Período {idx+1}")
                        st.markdown("**Original com desvio localizado (vermelho):**")
                        st.markdown(f'<div class="destaque-erro">{item["original"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown("**❌ Onde está o erro:**")
                        st.error(item['erro'])

                        if item['sugestao']:
                            st.markdown("**✨ Minha sugestão de novo texto para esta sentença (verde):**")
                            st.markdown(f'<div class="destaque-correcao">{item["sugestao"]}</div>', unsafe_allow_html=True)
                        else:
                            st.info("💡 *Recomendação:* Procure reescrever este trecho priorizando termos técnicos institucionais e mantendo a neutralidade do texto sem julgamento de valor.")
                        st.write("---")

                    # PROPOSTA RECOMPOSTA INTEGRADA PARA CÓPIA DIRETA
                    st.subheader('📝 Proposta de Versão Recomposta')
                    st.info('Aqui está a cópia integral do seu rascunho com os devidos ajustes recomendados aplicados:')
                    texto_final_recomposto = " ".join(sentencas_finais)
                    st.text_area('Copiar texto corrigido:', value=texto_final_recomposto, height=180)

    with aba_ajuda:
        st.markdown('#### 📚 Portais de Apoio Consultivo')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
