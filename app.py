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

# Estilização CSS inspirada na interface limpa do Gemini
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
    line-height: 1.6;
    margin-bottom: 20px;
}
.error-badge {
    background-color: #fce8e6;
    color: #c5221f;
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    display: inline-block;
    margin-bottom: 8px;
}
.success-badge {
    background-color: #e6f4ea;
    color: #137333;
    padding: 6px 12px;
    border-radius: 8px;
    font-weight: bold;
    font-size: 14px;
    display: inline-block;
    margin-bottom: 8px;
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
st.markdown('### Auditoria Crítica de Textos de Alta Especificidade')
st.markdown('Escreva o rascunho da sua matéria jurídica ou geral. O assistente analisará o contexto completo de forma profunda, explicando os erros técnicos e de estilo e sugerindo a reescrita adequada.')

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
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl de forma relativa. Verifique se eles estão na raiz do seu repositório no GitHub!')
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
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

                alertas_detectados = []
                relatorio_detalhado = []

                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas_detectados.append(s)

                        # Busca profunda por justificativas personalizadas de erro no database consolidado
                        justificativa_mapeada = None
                        sugestao_mapeada = None

                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao_mapeada = match.iloc[0]['sugestao']
                                if 'justificativa' in match.columns:
                                    justificativa_mapeada = match.iloc[0]['justificativa']

                        # Fallback inteligente se o erro não estiver mapeado de forma exata no banco de dados
                        if not justificativa_mapeada:
                            if tema_escolhido == 'Precatórios':
                                justificativa_mapeada = "Acusação informal ou prejulgamento sobre pagamentos. Precatórios constitucionais obedecem a cronogramas de repasses orçamentários sob regulação rígida do CNJ, e não a atos discricionários do TJGO."
                            elif tema_escolhido == 'Alterações no Projudi':
                                justificativa_mapeada = "Tom ofensivo ou informal para retratar instabilidades técnicas do sistema processual do Projudi. Falhas técnicas geram prorrogações legais devidamente certificadas por portaria."
                            elif tema_escolhido == 'Precedentes Judiciais':
                                justificativa_mapeada = "Equívoco de técnica jurídica. Decisões singulares de primeira instância não criam efeito vinculante generalizado imediato para outros processos antes da consolidação por colegiado."
                            elif tema_escolhido == 'Saúde Técnica':
                                justificativa_mapeada = "Alegação infundada sobre a motivação da concessão do medicamento. Demandas de saúde no tribunal passam pelo crivo de notas técnicas do NATJUS de caráter estritamente científico."
                            elif tema_escolhido == 'Tecnologia':
                                justificativa_mapeada = "Exagero tecnológico (desinformação). A Inteligência Artificial em tribunais atua como copiloto de automação e triagem, sendo a atividade de julgar exclusiva de magistrados humanos (Resolução 332/CNJ)."
                            elif tema_escolhido == 'Violência contra a Mulher':
                                justificativa_mapeada = "Violação grave das diretrizes éticas do Manual Universa. Culpabilizar a vítima por seus trajes, horários ou comportamentos ou justificar o agressor por ciúmes/descontrole é inaceitável."
                            else:
                                justificativa_mapeada = "Linguagem subjetiva, opinativa ou adjetivação desnecessária que prejudica a isenção editorial técnica esperada para a pauta judiciária."

                        relatorio_detalhado.append({
                            'frase_original': s,
                            'justificativa': justificativa_mapeada,
                            'reescrita': sugestao_mapeada
                        })

                st.markdown('### 🧠 Relatório e Diagnóstico Técnico do Revisor')

                if len(alertas_detectados) == 0:
                    st.markdown(f"""<div class="feedback-box">
                        <span class="success-badge">✅ TEXTO SEGURO E NEUTRO</span><br>
                        Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.<br><br>
                        O tom adotado para tratar sobre <b>{tema_escolhido}</b> está perfeitamente neutro, técnico e isento. 
                        Você conseguiu transmitir a informação factual de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional.<br><br>
                        Sua matéria está pronta e segura para publicação! Parabéns pelo rigor ético e precisão técnica.
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="feedback-box">
                        <span class="error-badge">⚠️ ALERTAS ENCONTRADOS</span><br>
                        Olá! Analisei com cuidado o seu rascunho de texto sobre <b>{tema_escolhido}</b>.<br><br>
                        A ideia central da sua matéria é importante, contudo identificamos trechos com problemas técnicos de precisão, linguagem informal ou desvios éticos em relação aos manuais recomendados. Veja abaixo o diagnóstico detalhado para cada trecho:
                    </div>""", unsafe_allow_html=True)

                    for item in relatorio_detalhado:
                        st.markdown(f"**Frase Analisada:**")
                        st.warning(f""{item['frase_original']}"")
                        
                        st.markdown(f"**❌ O que está errado (Justificativa Técnica):**")
                        st.info(item['justificativa'])

                        st.markdown(f"**✨ Como corrigir (Sugestão de Redação):**")
                        if item['reescrita']:
                            st.success(item['reescrita'])
                        else:
                            st.success("Sugestão Geral: Reescreva o trecho na ordem direta da língua portuguesa, utilizando vocabulário técnico impessoal, baseando-se estritamente em fatos documentados e citando canais oficiais (como Ligue 180 para violência doméstica).")
                        
                        st.markdown("--- ")

    with aba_ajuda:
        st.markdown('#### 📚 Portais de Apoio Consultivo')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
