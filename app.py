import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Revisor Anal&iacute;tico TJGO - Padr&atilde;o Gemini',
    page_icon='⚖&ufe0f',
    layout='wide'
)

st.title('⚖&ufe0f Copiloto Anal&iacute;tico de Reda&ccedil;&atilde;o - Padr&atilde;o Gemini (TJGO)')
st.markdown('Esta aplica&ccedil;&atilde;o realiza a auditoria avan&ccedil;ada de rascunhos de mat&eacute;rias dividindo as avalia&ccedil;&otilde;es de sensibilidade, justificativas e regras de reda&ccedil;&atilde;o do TJGO.')

# Fun&ccedil;&atilde;o local do app que normaliza o texto antes de passar para o TfidfVectorizer
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
        # Prioridade absoluta para caminhos do Google Colab para evitar falhas de carregamento em segundo plano
        modelo_path = '/content/modelo_jornalismo.pkl'
        database_path = '/content/database_sugestoes.pkl'

        # Fallback para caminhos relativos em ambientes externos (como GitHub/Streamlit Cloud)
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
    'Precat&oacute;rios': '[Portal de Precat&oacute;rios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Altera&ccedil;&otilde;es no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprud&ecirc;ncia Unificada e S&uacute;mulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Sa&uacute;de T&eacute;cnica': '[Comit&ecirc; de Sa&uacute;de do NATJUS de Goi&aacute;s](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estrat&eacute;gia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justi&ccedil;a (CNJ - Resolu&ccedil;&atilde;o 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'L&iacute;ngua Portuguesa': '[Manual de Reda&ccedil;&atilde;o da Presid&ecirc;ncia da Rep&uacute;blica](https://www.gov.br/planalto/pt-br/acompanhe-o-planalto/manuais) | [Manual de Comunica&ccedil;&atilde;o do Senado](https://www12.senado.leg.br/manualdecomunicacao) | [Vocabul&aacute;rio Ortogr&aacute;fico da ABL](https://www.academia.org.br/nossa-lingua/busca-no-vocabulario)',
    'Viol&ecirc;ncia contra a Mulher': '[Coordenadoria da Mulher em Situa&ccedil;&atilde;o de Viol&ecirc;ncia Dom&eacute;stica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

modelos_textos_base = {
    'Precat&oacute;rios': (
        "O Tribunal de Justi&ccedil;a do Estado de Goi&aacute;s (TJGO) divulgou nesta semana a atualiza&ccedil;&atilde;o do cronograma de pagamento de precat&oacute;rios para o exerc&iacute;cio vigente. "
        "Segundo a Diretoria de Precat&oacute;rios do &oacute;rg&atilde;o, os repasses aos credores priorit&aacute;rios (como idosos e pessoas com defici&ecirc;ncia) seguem de forma regular, "
        "respeitando rigorosamente a ordem cronol&oacute;gica e os aportes financeiros estabelecidos pelo ente devedor estatal."
    ),
    'Altera&ccedil;&otilde;es no Projudi': (
        "Devido a uma manuten&ccedil;&atilde;o corretiva programada nos servidores da Diretoria de Tecnologia da Informa&ccedil;&atilde;o do TJGO, o sistema Projudi registrou per&iacute;odos de oscila&ccedil;&atilde;o t&eacute;cnica. "
        "Para mitigar eventuais preju&iacute;zos aos prazos processuais da advocacia, o Tribunal emitiu certid&atilde;o de indisponibilidade oficial e decretou de forma autom&aacute;tica a prorroga&ccedil;&atilde;o dos prazos."
    ),
    'Precedentes Judiciais': (
        "Em decis&atilde;o recente proferida pela Se&ccedil;&atilde;o C&iacute;vel do Tribunal de Justi&ccedil;a de Goi&aacute;s (TJGO), fixou-se tese em sede de Incidente de Resolu&ccedil;&atilde;o de Demandas Repetitivas (IRDR). "
        "O entendimento uniformiza as decis&otilde;es de primeira inst&acirc;ncia no estado de Goi&aacute;s e servir&aacute; como precedente obrigat&oacute;rio para os casos an&aacute;logos."
    ),
    'Sa&uacute;de T&eacute;cnica': (
        "O Poder Judici&aacute;rio goiano acolheu, em car&aacute;ter liminar, o pedido para fornecimento de tratamento de sa&uacute;de especializado na comarca de Goi&acirc;nia. "
        "Na decis&atilde;o, o magistrado fundamentou a necessidade do fornecimento com base no parecer t&eacute;cnico favor&aacute;vel emitido pelo N&uacute;cleo de Apoio T&eacute;cnico do Judici&aacute;rio (NATJUS), garantindo seguran&ccedil;a baseada em evid&ecirc;ncia cient&iacute;fica."
    ),
    'Tecnologia': (
        "O Tribunal de Justi&ccedil;a do Estado de Goi&aacute;s (TJGO) adota modelos de Intelig&ecirc;ncia Artificial para apoiar a triagem e automa&ccedil;&atilde;o de tarefas administrativas. "
        "Em linha com a Resolu&ccedil;&atilde;o 332 do CNJ e a Estrat&eacute;gia Brasileira de IA, todos os relat&oacute;rios e minutas gerados passam obrigatoriamente por valida&ccedil;&atilde;o, revis&atilde;o e assinatura de magistrados humanos."
    ),
    'L&iacute;ngua Portuguesa': (
        "De acordo com o Manual de Reda&ccedil;&atilde;o da Presid&ecirc;ncia da Rep&uacute;blica, os textos jornal&iacute;sticos e informativos institucionais devem ser regidos pelos princ&iacute;pios de impessoalidade, clareza e concis&atilde;o, "
        "evitando express&otilde;es amb&iacute;guas, preciosismo vocabular ou jarg&otilde;es informais que dificultem a compreens&atilde;o do cidad&atilde;o."
    ),
    'Viol&ecirc;ncia contra a Mulher': (
        "A pol&iacute;cia civil abriu inqu&eacute;rito para investigar o crime sob a tipifica&ccedil;&atilde;o penal de feminic&iacute;dio. Ligue 180 para apoio e den&uacute;ncias de viol&ecirc;ncia dom&eacute;stica."
    )
}

if modelo_local is None:
    st.error('❄&ufe0f N&atilde;o foi poss&iacute;vel carregar os artefatos de Intelig&ecirc;ncia Artificial (.pkl).')
else:
    aba_auditoria, aba_modelos = st.tabs(['☒ Auditoria e Revis&atilde;o de Texto', '&#128161; Gerador de Sugest&otilde;es / Textos Base'])

    with aba_auditoria:
        st.header('Auditoria e Feedback Estilo Gemini')
        tema_escolhido = st.selectbox(
            'Selecione a categoria da pauta para direcionar as refer&ecirc;ncias:',
            ['Precat&oacute;rios', 'Altera&ccedil;&otilde;es no Projudi', 'Precedentes Judiciais', 'Sa&uacute;de T&eacute;cnica', 'Tecnologia', 'L&iacute;ngua Portuguesa', 'Viol&ecirc;ncia contra a Mulher']
        )

        if tema_escolhido in referencias_goias:
            st.info(f'&#128214; **Documenta&ccedil;&otilde;es Oficiais de Apoio para {tema_escolhido}:** {referencias_goias[tema_escolhido]}')

        texto_materia = st.text_area(
            'Cole o seu rascunho de mat&eacute;ria jornal&iacute;stica aqui:',
            placeholder='Insira o rascunho da sua reportagem...',
            height=250
        )

        if st.button('Iniciar Auditoria de Risco e Linguagem', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite ou cole um texto antes de analisar.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

                st.subheader('&#128203; Relat&oacute;rio Anal&iacute;tico de Reda&ccedil;&atilde;o')

                alertas = 0
                for s in sentencas:
                    # NORMALIZA LOCALMENTE
                    sentenca_limpa = normalizar_texto_local(s)
                    
                    # Envia a senten&ccedil;a limpa para o preditor
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas += 1
                        risco = "&#128680; RISCO CR&Iacute;TICO" if score_sensibilidade >= 0.65 else "&#128162; RISCO MODERADO"
                        cor = "red" if score_sensibilidade >= 0.65 else "orange"

                        st.markdown(f'<p style="color:{cor}; font-size:18px; font-weight:bold;">{risco} ({score_sensibilidade:.1%}): "{s}"</p>', unsafe_allow_html=True)

                        # Busca exata ou aproximada por sugest&otilde;es no database
                        sugestao = None
                        justificativa = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao = match.iloc[0]['sugestao']
                                if 'justificativa' in match.columns:
                                    justificativa = match.iloc[0]['justificativa']

                        # Retorno estruturado imitando o Gemini (Problema + Corre&ccedil;&atilde;o)
                        st.markdown("**❄&ufe0f O que est&aacute; errado:**")
                        if justificativa:
                            st.write(justificativa)
                        else:
                            if tema_escolhido == 'Viol&ecirc;ncia contra a Mulher':
                                st.write("O trecho pode ferir as diretrizes do Manual Universa ao utilizar justificativas sentimentais para crimes (como ci&uacute;mes), usar termos desatualizados ou faltar a indica&ccedil;&atilde;o do Ligue 180.")
                            elif tema_escolhido == 'Tecnologia':
                                st.write("O texto apresenta risco ao sugerir que a tecnologia decide senten&ccedil;as de forma isolada, violando as regras &eacute;ticas da Resolu&ccedil;&atilde;o 332 do CNJ.")
                            elif tema_escolhido == 'L&iacute;ngua Portuguesa':
                                st.write("H&aacute; forte ind&iacute;cio de desvios gramaticais de concord&acirc;ncia, reg&ecirc;ncia ou de estilo prolixo inadequado para reda&ccedil;&otilde;es jornal&iacute;sticas ou oficiais.")
                            else: 
                                st.write("O trecho apresenta termos sensacionalistas, falta de neutralidade ou acusa&ccedil;&otilde;es sem apresenta&ccedil;&atilde;o de provas factuais.")

                        if sugestao:
                            st.markdown(f"**✨ Sugest&atilde;o de Reescrita Correta:** `{sugestao}`")
                        else:
                            st.markdown("**✨ Recomenda&ccedil;&atilde;o Geral:** Readequar a linguagem para termos t&eacute;cnicos-jur&iacute;dicos neutros de acordo com o Manual do Senado Federal, removendo adjetivos pessoais ou termos coloquiais.")
                        st.write('---')

                if alertas == 0:
                    st.success('✅ **Excelente!** O rascunho analisado atende perfeitamente ao tom neutro, isento e com a terminologia recomendada de acordo com as regras de reda&ccedil;&atilde;o da editoria e do TJGO.')

    with aba_modelos:
        st.header('&#128161; Sugest&otilde;es de Textos e Modelos de Reda&ccedil;&atilde;o')
        st.write('Selecione uma categoria abaixo para obter um texto-modelo estruturado de forma imparcial, clara e perfeitamente ajustada &agrave;s boas pr&aacute;ticas do jornalismo.')

        tema_modelo = st.selectbox(
            'Selecione o tema para gerar a sugest&atilde;o de reda&ccedil;&atilde;o:',
            ['Precat&oacute;rios', 'Altera&ccedil;&otilde;es no Projudi', 'Precedentes Judiciais', 'Sa&uacute;de T&eacute;cnica', 'Tecnologia', 'L&iacute;ngua Portuguesa', 'Viol&ecirc;ncia contra a Mulher']
        )

        if tema_modelo in modelos_textos_base:
            st.subheader(f'&#128205; Modelo de Reda&ccedil;&atilde;o Recomendado: {tema_modelo}')
            texto_sugerido = modelos_textos_base[tema_modelo]
            st.text_area('Copie o texto base sugerido abaixo:', value=texto_sugerido, height=180)
            st.info('&#128073; **Nota para o jornalista:** Lembre-se de substituir ou complementar os detalhes com as informa&ccedil;&otilde;es da sua apura&ccedil;&atilde;o.')
