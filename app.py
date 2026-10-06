import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title='Copiloto Editorial TJGO & Gemini',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Revisor de Alta Precisão (TJGO + Gemini Pro)')
st.markdown('Esta aplicação une a velocidade de um classificador de Machine Learning local à inteligência analítica profunda do **Google Gemini** para auditar e reescrever matérias jornalísticas.')

# Barra lateral para configuração segura da API Key pelo próprio usuário
st.sidebar.header('🔑 Configuração da API do Gemini')
api_key_input = st.sidebar.text_input('Insira sua GOOGLE_API_KEY:', type='password', help='Sua chave de API fica salva apenas na sessão do seu navegador e não é compartilhada.')

# Função local de normalização para o classificador leve
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

# 1. Prompt de Instrução de Sistema avançada para moldar a IA como Editor Sênior
prompt_sistema_editorial = (
    "Você é um Editor de Redação Sênior e Revisor de Ética Jornalística com vasta experiência em coberturas institucionais, "
    "diretrizes de gênero do Manual Universa e regulação do Tribunal de Justiça de Goiás (TJGO).\n"
    "Sua tarefa é analisar o rascunho de texto jornalístico fornecido pelo usuário e entregar uma avaliação técnica extremamente didática, ricas em detalhes, que melhore a escrita do jornalista.\n\n"
    "Para o texto fornecido, estruture sua resposta exatamente com os seguintes tópicos bem definidos:\n"
    "1. 🔴 **Trechos Inadequados ou Sensíveis**: Identifique frases exatas do texto que contenham problemas (sensacionalismo, acusações sem provas, culpabilização da vítima no caso de violência de gênero, preconceitos sobre inteligência artificial no judiciário, jargões excessivos ou erros de concordância). Justifique o porquê de cada um.\n"
    "2. 📚 **Alinhamento com Diretrizes**: Explique quais regras de redação (do TJGO, do CNJ, do Manual de Redação Oficial ou do Manual Universa) devem ser aplicadas para resolver o impasse do trecho.\n"
    "3. ✨ **Versão Sugerida de Redação**: Apresente uma reescrita polida, fluida, perfeitamente clara, de tom totalmente profissional, imparcial e neutro, mantendo os fatos originais e o rigor técnico jurídico."
)

if modelo_local is None:
    st.error('❌ Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl.')
else:
    aba_auditoria, aba_ajuda = st.tabs(['🔍 Auditoria Completa', '📚 Fontes & Referências'])

    with aba_auditoria:
        tema_escolhido = st.selectbox(
            'Selecione a categoria da pauta para direcionar as referências:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
        )

        texto_materia = st.text_area(
            'Insira o rascunho da notícia para revisão:',
            placeholder='Cole o parágrafo ou texto completo da reportagem...',
            height=200
        )

        if st.button('Iniciar Auditoria Inteligente', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite ou cole um texto antes de analisar.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]
                st.subheader('📊 Diagnóstico de Entrada')

                # Primeiro Passo: O Classificador Estatístico Local busca riscos rápidos
                alertas_locais = 0
                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.50:
                        alertas_locais += 1
                        st.warning(f'⚠️ **Possível Viés/Sensibilidade Localizada:** "{s}"')

                if alertas_locais > 0:
                    st.info('💡 *Nosso classificador estatístico local detectou frases sensíveis. Vamos acionar a inteligência analítica profunda do Gemini para detalhar cada caso.*')
                
                # Segundo Passo: Se houver Chave de API, acionamos a revisão avançada gerada pelo Gemini
                if api_key_input:
                    with st.spinner('Acionando o editor sênior do Gemini para construir feedbacks ricos de linguagem...'):
                        try:
                            client = genai.Client(api_key=api_key_input)
                            
                            input_gemini = f"Tema da Matéria: {tema_escolhido}\nTexto para Auditoria: {texto_materia}"
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash-lite',
                                contents=input_gemini,
                                config=types.GenerateContentConfig(
                                    system_instruction=prompt_sistema_editorial,
                                    temperature=0.3
                                )
                            )
                            
                            st.markdown('---')
                            st.markdown('### 🧠 Feedback e Análise Crítica do Gemini')
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f'Erro na integração com a API do Gemini: {e}')
                else:
                    st.info('👉 **Para obter explicações detalhadas estilo Gemini (O que está errado + Dicas de Manuais + Redação Sugerida), insira sua GOOGLE_API_KEY na barra lateral!**')

    with aba_ajuda:
        st.header('Portais e Fontes Oficiais do Judiciário')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
