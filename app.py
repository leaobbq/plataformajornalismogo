import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title='Copiloto Editorial TJGO & Gemini',
    page_icon='⚖️',
    layout='centered'
)

# Estilização visual limpa e amigável para leitura
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
div.stButton > button:first-child {
    background-color: #0b57d0;
    color: white;
    border-radius: 20px;
    padding: 8px 24px;
    font-weight: bold;
    border: none;
}
</style>""", unsafe_allow_html=True)

st.title('⚖️ Copiloto Editorial Dinâmico')
st.markdown('### Revisão analítica, crítica e estilística em tempo real com o Google Gemini')
st.markdown('Insira sua matéria para obter uma análise editorial personalizada e uma nova proposta de redação baseada no estado da arte em IA.')

# --- GERENCIAMENTO SEGURO DA API KEY (FALLBACKS) ---
API_KEY_FINAL = ""

# 1. Tenta obter dos Secrets nativos do Streamlit Cloud (Recomendado para Deploy)
if 'GOOGLE_API_KEY' in st.secrets:
    API_KEY_FINAL = st.secrets['GOOGLE_API_KEY']
# 2. Tenta obter das variáveis de ambiente locais do sistema
elif os.environ.get('GOOGLE_API_KEY'):
    API_KEY_FINAL = os.environ.get('GOOGLE_API_KEY')

# Permite inserção manual na barra lateral como contingência ou para substituição
st.sidebar.header('🔑 Configuração de Acesso')
chave_manual = st.sidebar.text_input('Insira sua GOOGLE_API_KEY do Gemini:', type='password', help='Sua chave de API fica salva temporariamente na sessão do seu navegador.')

if chave_manual.strip():
    API_KEY_FINAL = chave_manual.strip()

if not API_KEY_FINAL:
    st.sidebar.warning('👉 Insira sua GOOGLE_API_KEY acima ou configure-a nos Secrets do Streamlit para ativar o Revisor!')
else:
    st.sidebar.success('✅ Conectado ao Gemini!')

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

# Instruções de Sistema Sênior para modelar o comportamento do Gemini de forma didática e isenta
prompt_sistema_editorial = (
    "Você é um Revisor Crítico de Jornalismo e Editor Sênior voltado para coberturas institucionais jurídicas, "
    "diretrizes éticas e de gênero (Manual Universa).\n"
    "Sua função é analisar o rascunho de texto enviado de forma dinâmica, construtiva e totalmente livre de respostas fixas ou prontas.\n\n"
    "Instruções de conduta:\n"
    "1. Avalie o tom e a isenção de forma dissertativa. Se o texto estiver perfeitamente neutro, técnico, correto e justo "
    "(como um comunicado oficial, decisão da Justiça ou sentenças formais), reconheça isso de imediato com um elogio sincero ao estilo profissional do redator.\n"
    "2. Se houver desvios, identifique os trechos exatos (sensacionalismo, opiniões sem fatos, termos desatualizados, "
    "suposições de má-fé contra o tribunal ou culpabilização de vítimas). Critique de forma amigável e didática, "
    "explicando qual princípio de redação jornalística, regra gramatical ou manual de estilo foi violado.\n"
    "3. Forneça sempre uma proposta de reescrita polida, fluida e de tom neutro que mantenha os fatos reais totalmente intactos."
)

tema_pauta = st.selectbox(
    'Assunto principal da reportagem:',
    ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
)

if tema_pauta in referencias_goias:
    st.info(f'📚 **Documentações técnicas e fontes oficiais para apoio:** {referencias_goias[tema_pauta]}')

texto_jornalista = st.text_area('Insira o rascunho da sua matéria:', placeholder='Cole ou escreva o texto para que o Gemini analise e sugira as alterações...', height=220)

if st.button('Revisar com Gemini', type='primary'):
    if not texto_jornalista.strip():
        st.warning('Escreva uma matéria antes de submeter à análise.')
    elif not API_KEY_FINAL:
        st.error('❌ GOOGLE_API_KEY não localizada. Certifique-se de inseri-la na barra lateral para habilitar a consulta ao Gemini.')
    else:
        with st.spinner('O Gemini está lendo, analisando e estruturando o seu feedback...'):
            try:
                client = genai.Client(api_key=API_KEY_FINAL)
                solicitacao = f"Assunto principal: {tema_pauta}\n\nTexto da matéria:\n{texto_jornalista}"

                response = client.models.generate_content(
                    model='gemini-2.5-flash-lite',
                    contents=solicitacao,
                    config=types.GenerateContentConfig(
                        system_instruction=prompt_sistema_editorial,
                        temperature=0.3
                    )
                )

                st.markdown('### 🧠 Retorno do Editor Sênior (Gemini)')
                st.markdown(f'<div class="feedback-box">{response.text}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f'Erro ao se comunicar com o Gemini: {e}')
