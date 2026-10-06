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
st.markdown('Esta aplicação realiza a auditoria avançada de rascunhos de matérias dividindo as avaliações de sensibilidade e regras de redação do TJGO.')

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
        # Prioridade para caminhos relativos (raiz do repositório / nuvem)
        modelo_path = 'modelo_jornalismo.pkl'
        database_path = 'database_sugestoes.pkl'

        # Se não encontrar localmente na raiz, faz o fallback para o Colab
        if not os.path.exists(modelo_path):
            modelo_path = '/content/modelo_jornalismo.pkl'
        if not os.path.exists(database_path):
            database_path = '/content/database_sugestoes.pkl'

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
    'Língua Portuguesa': '[Manual de Redação da Presidência da República](https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/manuais) | [Manual de Comunicação do Senado](https://www12.senado.leg.br/manualdecomunicacao) | [Vocabulário Ortográfico da ABL](https://www.academia.org.br/nossa-lingua/busca-no-vocabulario)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

modelos_textos_base = {
    'Precatórios': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) divulgou nesta semana a atualização do cronograma de pagamento de precatórios para o exercício vigente. "
        "Segundo a Diretoria de Precatórios do órgão, os repasses aos credores prioritários (como idosos e pessoas com deficiência) seguem de forma regular, "
        "respeitando rigorosamente a ordem cronológica e os aportes financeiros estabelecidos pelo ente devedor estatal."
    ),
    'Alterações no Projudi': (
        "Devido a uma manutenção corretiva programada nos servidores da Diretoria de Tecnologia da Informação do TJGO, o sistema Projudi registrou períodos de oscilação técnica. "
        "Para mitigar eventuais prejuízos aos prazos processuais da advocacia, o Tribunal emitiu certidão de indisponibilidade oficial e decretou de forma automática a prorrogação dos prazos."
    ),
    'Tecnologia': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) adota modelos de Inteligência Artificial para apoiar a triagem e automação de tarefas administrativas. "
        "Em linha com a Resolução 332 do CNJ e a Estratégia Brasileira de IA, todos os relatórios e minutas gerados passam obrigatoriamente por validação, revisão e assinatura de magistrados humanos."
    ),
    'Língua Portuguesa': (
        "De acordo com o Manual de Redação da Presidência da República, os textos jornalísticos e informativos institucionais devem ser regidos pelos princípios de impessoalidade, clareza e concisão, "
        "evitando expressões ambíguas, preciosismo vocabular ou jargões informais que dificultem a compreensão do cidadão."
    )
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos de Inteligência Artificial (.pkl).')
else:
    aba_auditoria, aba_modelos = st.tabs(['🔍 Auditoria e Revisão de Texto', '💡 Gerador de Sugestões / Textos Base'])

    with aba_auditoria:
        st.header('Auditoria e Feedback Estilo Gemini')
        tema_escolhido = st.selectbox(
            'Selecione a categoria da pauta para direcionar as referências:',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
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
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas += 1
                        risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                        cor = "red" if score_sensibilidade >= 0.65 else "orange"

                        st.markdown(f'<p style="color:{cor}; font-size:18px; font-weight:bold;">{risco} ({score_sensibilidade:.1%}): "{s}"</p>', unsafe_allow_html=True)

                        # Busca de sugestão estruturada
                        sugestao = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao = match.iloc[0]['sugestao']

                        st.markdown("**❌ O que está errado:**")
                        if tema_escolhido == 'Violência contra a Mulher':
                            st.write("O trecho pode ferir as diretrizes do Manual Universa ao utilizar justificativas sentimentais para crimes (como ciúmes), usar termos desatualizados como 'crime passional' ou faltar com a indicação de canais oficiais como o Ligue 180.")
                        elif tema_escolhido == 'Tecnologia':
                            st.write("O texto apresenta risco ao dar a entender que a tecnologia ou algoritmos de IA decidem sentenças de forma isolada, ignorando o papel constitucional exclusivo e a revisão dos magistrados do TJGO ou violando os preceitos éticos da Resolução 332/CNJ.")
                        elif tema_escolhido == 'Língua Portuguesa':
                            st.write("Há forte indício de desvio gramatical (como erros de concordância verbal/nominal, erro na colocação pronominal, uso incorreto de pronomes relativos) ou de estilo prolixo e inadequado segundo o Manual de Redação da Presidência da República.")
                        else: 
                            st.write("O trecho apresenta acusações subjetivas, parcialidade evidente ou falta com o rigor jornalístico de ouvir todas as partes.")

                        if sugestao:
                            st.markdown(f"**✨ Sugestão de Reescrita Correta:** `{sugestao}`")
                        else:
                            st.markdown("**✨ Recomendação Geral:** Readequar a linguagem para termos técnicos-jurídicos neutros de acordo com o Manual de Redação Clara do Senado Federal, removendo adjetivos pessoais ou termos coloquiais.")
                        st.write('---')

                if alertas == 0:
                    st.success('✅ **Excelente!** O rascunho analisado atende perfeitamente ao tom neutro, isento e com a terminologia recomendada de acordo com as regras de redação da editoria e do TJGO.')

    with aba_modelos:
        st.header('💡 Sugestão de Textos e Modelos de Redação')
        st.write('Selecione uma categoria abaixo para obter um texto-modelo estruturado de forma imparcial, clara e perfeitamente ajustada às boas práticas do jornalismo e do TJGO.')

        tema_modelo = st.selectbox(
            'Selecione o tema para gerar a sugestão de redação:',
            ['Precatórios', 'Alterações no Projudi', 'Tecnologia', 'Língua Portuguesa']
        )

        if tema_modelo in modelos_textos_base:
            st.subheader(f'📝 Modelo de Redação Recomendado: {tema_modelo}')
            texto_sugerido = modelos_textos_base[tema_modelo]
            st.text_area('Copie o texto base sugerido abaixo:', value=texto_sugerido, height=180)
            st.info('👉 **Nota para o jornalista:** Lembre-se de substituir ou complementar os detalhes com as informações da sua apuração.')
