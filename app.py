import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Copiloto Editorial TJGO - Estilo Gemini',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Revisor Analítico TJGO')
st.markdown('### Auditoria Avançada com Diagnósticos Detalhados e Reescrita Dirigida')
st.markdown('Esta aplicação utiliza Processamento de Linguagem Natural (NLP) e engenharia de regras para analisar rascunhos de matérias jornalísticas de forma extremamente didática e detalhada.')

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
    'Precedentes Judiciais': (
        "Em decisão recente proferida pela Seção Cível do Tribunal de Justiça de Goiás (TJGO), fixou-se tese em sede de Incidente de Resolução de Demandas Repetitivas (IRDR). "
        "O entendimento uniformiza as decisões de primeira instância no estado de Goiás e servirá como precedente obrigatório para os casos análogos."
    ),
    'Saúde Técnica': (
        "O Poder Judiciário goiano acolheu, em caráter liminar, o pedido para fornecimento de tratamento de saúde especializado na comarca de Goiânia. "
        "Na decisão, o magistrado fundamentou a necessidade do fornecimento com base no parecer técnico favorável emitido pelo Núcleo de Apoio Técnico do Judiciário (NATJUS), garantindo segurança baseada em evidência científica."
    ),
    'Tecnologia': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) adota modelos de Inteligência Artificial para apoiar a triagem e automação de tarefas administrativas. "
        "Em linha com a Resolução 332 do CNJ e a Estratégia Brasileira de IA, todos os relatórios e minutas gerados passam obrigatoriamente por validação, revisão e assinatura de magistrados humanos."
    ),
    'Língua Portuguesa': (
        "De acordo com o Manual de Redação da Presidência da República, os textos jornalísticos e informativos institucionais devem ser regidos pelos princípios de impessoalidade, clareza e concisão, "
        "evitando expressões ambíguas, preciosismo vocabular ou jargões informais que dificultem a compreensão do cidadão."
    ),
    'Violência contra a Mulher': (
        "A polícia civil abriu inquérito para investigar o crime sob a tipificação penal de feminicídio. Ligue 180 para apoio e denúncias de violência doméstica."
    )
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos de Inteligência Artificial (.pkl).')
else:
    aba_auditoria, aba_modelos = st.tabs(['🔍 Auditoria Avançada & Revisão Estilo Gemini', '💡 Gerador de Textos Base'])

    with aba_auditoria:
        tema_escolhido = st.selectbox(
            'Selecione a pauta da sua matéria:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
        )

        if tema_escolhido in referencias_goias:
            st.info(f'📚 **Documentações e Fontes Oficiais recomendadas:** {referencias_goias[tema_escolhido]}')

        texto_materia = st.text_area(
            'Cole o seu rascunho de matéria jornalística aqui para auditoria de linguagem:',
            placeholder='Insira o rascunho da sua reportagem...',
            height=220
        )

        if st.button('Iniciar Auditoria e Gerar Relatório Detalhado', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite ou cole um texto antes de analisar.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

                st.subheader('📋 Diagnóstico Crítico de Linguagem e Termos Sensíveis')

                alertas = 0
                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.40:
                        alertas += 1
                        risco = "🚨 RISCO CRÍTICO" if score_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                        cor = "red" if score_sensibilidade >= 0.65 else "orange"

                        # Exibe a sentença com caixa de atenção estilizada
                        st.markdown(f'''
                        <div style="padding:12px; border-left: 6px solid {cor}; background-color:#111111; border-radius: 4px; margin-bottom: 12px;">
                            <span style="color:{cor}; font-weight:bold; font-size:15px;">{risco} (Sensibilidade: {score_sensibilidade:.1%})</span><br>
                            <span style="font-style:italic; font-size:14px; color:#eeeeee;">"{s}"</span>
                        </div>
                        ''', unsafe_allow_html=True)

                        # Busca dados mapeados de forma exata ou aproximada no database para preencher o relatório
                        sugestao = None
                        justificativa_erro = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty:
                                sugestao = match.iloc[0]['sugestao']
                                if 'erro_identificado' in match.columns:
                                    justificativa_erro = match.iloc[0]['erro_identificado']

                        # Montando o relatório estruturado e explicativo no Estilo Gemini
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### ❌ O que está errado:")
                            if justificativa_erro:
                                st.error(justificativa_erro)
                            else:
                                if tema_escolhido == 'Violência contra a Mulher':
                                    st.error("Uso de terminologia prejudicial ou inadequada. Evite adjetivos que justifiquem o agressor, termos sentimentais antigos como 'crime passional' ou culpabilização indireta da vítima. Recomenda-se adicionar a indicação do Ligue 180.")
                                elif tema_escolhido == 'Tecnologia':
                                    st.error("Falta de rigor factual. O trecho sugere que sistemas automatizados ou algoritmos decidem processos sozinhos sem a revisão e autoridade exclusiva de magistrados do TJGO.")
                                elif tema_escolhido == 'Língua Portuguesa':
                                    st.error("Presença de desvios gramaticais evidentes (como concordância verbal/nominal incorreta ou erro no uso de pronomes) ou estilo excessivamente prolixo.")
                                else:
                                    st.error("Presença de adjetivos de teor opinativo ou acusações unilaterais que violam o tom neutro de jornalismo técnico judiciário.")
                        
                        with col2:
                            st.markdown("### ✨ Como corrigir (Versão Sugerida):")
                            if sugestao:
                                st.success(sugestao)
                            else:
                                st.warning("Prefira reescrever o período na ordem direta, focando apenas nos fatos processuais formais de maneira impessoal e neutra.")
                        st.write('---')

                if alertas == 0:
                    st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta, isenção factual e linguagem recomendada pelo TJGO.')

    with aba_modelos:
        st.header('💡 Sugestão de Textos e Modelos de Redação')
        st.write('Selecione uma categoria abaixo para obter um texto-modelo estruturado de forma imparcial, clara e perfeitamente ajustada às boas práticas do jornalismo.')

        tema_modelo = st.selectbox(
            'Selecione o tema para gerar a sugestão de redação:',
            ['Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Língua Portuguesa', 'Violência contra a Mulher']
        )

        if tema_modelo in modelos_textos_base:
            st.subheader(f'📝 Modelo de Redação Recomendado: {tema_modelo}')
            texto_sugerido = modelos_textos_base[tema_modelo]
            st.text_area('Copie o texto base sugerido abaixo:', value=texto_sugerido, height=180)
            st.info('👉 **Nota para o jornalista:** Lembre-se de substituir ou complementar os detalhes com as informações reais da sua apuração.')
