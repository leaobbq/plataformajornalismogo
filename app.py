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

# Estilização CSS limpa e moderna integrada de forma segura
st.markdown("""<style>
.reportview-container {
    background: #fafafa;
}
.feedback-box {
    background-color: #f0f4f9;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #d3e3fd;
    color: #1f1f1f;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
}
.texto-destaque {
    background-color: #e9eef6;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
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
st.markdown('Escreva o rascunho da sua pauta jurídica ou geral. O assistente analisará o contexto completo e trará um feedback dissertativo, didático e amigável de forma 100% online.')

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
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl.')
else:
    aba_auditoria, aba_ajuda = st.tabs(['🔍 Analisar Rascunho', '📚 Guia de Fontes Oficial'])

    with aba_auditoria:
        tema_escolhido = st.selectbox(
            'Qual é o assunto principal da sua matéria?',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        texto_materia = st.text_area('Insira o seu rascunho aqui:', placeholder='Escreva livremente o seu parágrafo ou matéria completa...', height=220)

        if st.button('Revisar com o Copiloto'):
            if not texto_materia.strip():
                st.warning('Por favor, escreva algum rascunho de texto antes de prosseguir.')
            else:
                sentencas = [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto_materia) if len(s.strip()) > 4]

                alertas_detectados = []
                sugestoes_banco = []
                detalhes_erros = []
                sentencas_finais = []

                for s in sentencas:
                     sentenca_limpa = normalizar_texto_local(s)
                     probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                     score_sensibilidade = probabilidades[1]

                     if score_sensibilidade >= 0.45:
                        alertas_detectados.append(s)
                        justificativa_mapeada = None
                        sugestao_mapeada = None

                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao_mapeada = match.iloc[0]['sugestao']
                                if 'erro_identificado' in match.columns:
                                    justificativa_mapeada = match.iloc[0]['erro_identificado']
                                elif 'justificativa' in match.columns:
                                    justificativa_mapeada = match.iloc[0]['justificativa']

                        if not justificativa_mapeada:
                            if tema_escolhido == 'Violência contra a Mulher':
                                justificativa_mapeada = "Uso de terminologia que culpabiliza indiretamente a vítima ou justifica o crime baseado no comportamento ou ciúmes do agressor. Contraria o Manual Universa."
                            elif tema_escolhido == 'Tecnologia':
                                justificativa_mapeada = "Premissa incorreta de que a IA profere sentenças de forma autônoma. No TJGO a tecnologia opera como auxiliar administrativa sob revisão e assinatura obrigatória do magistrado humano."
                            else:
                                justificativa_mapeada = "O trecho apresenta tom opinativo, subjetivo ou com termos tecnicamente desajustados para a cobertura profissional de pautas do TJGO."

                        detalhes_erros.append({
                            'trecho': s,
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
                    feedback_texto = f"""Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.

O tom adotado para tratar sobre **{tema_escolhido}** está perfeitamente neutro, técnico e isento. Você conseguiu transmitir a informação factual de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional.

Sua matéria está pronta e segura para publicação! Não vejo necessidade de alterações técnicas ou éticas. Parabéns pelo cuidado com a escrita!"""
                    st.markdown(f'<div class="feedback-box">{feedback_texto}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="feedback-box">
                    Olá! Analisei com cuidado o seu rascunho sobre <b>{tema_escolhido}</b>.<br><br>
                    A ideia central da sua matéria é ótima, mas reparei em alguns desvios factuais ou de tom que merecem atenção para garantir a blindagem jurídica e a máxima clareza técnica.<br><br>
                    Abaixo separei cada frase crítica para analisarmos de forma transparente:
                    </div>""", unsafe_allow_html=True)

                    for idx, item in enumerate(detalhes_erros):
                        st.markdown(f"### 📌 Ponto {idx+1}: Análise de Sentença")
                        st.warning(f"""{item['trecho']}""")

                        st.markdown("**❌ Onde está o erro:**")
                        st.error(item['erro'])

                        st.markdown("**✨ Minha sugestão de redação:**")
                        if item['sugestao']:
                            st.success(item['sugestao'])
                        else:
                            st.success("Recomenda-se reescrever este período utilizando termos institucionais neutros, focando unicamente em fatos consumados de forma impessoal e removendo adjetivos coloquiais.")
                        st.write('---')

                    st.subheader("📝 Versão Sugerida Completa (Recomposta)")
                    st.info("Aqui está a versão consolidada do seu rascunho com as alterações aplicadas:")
                    texto_recomposto = " ".join(sentencas_finais)
                    st.text_area("Texto completo sugerido para cópia:", value=texto_recomposto, height=180)

    with aba_ajuda:
        st.markdown("""#### 📚 Portais de Apoio Consultivo""")
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
