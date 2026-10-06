import streamlit as st
import joblib
import re
import pandas as pd

st.set_page_config(
    page_title='Revisor Ultra Assertivo TJGO',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Revisor de Alta Precisão - TJGO')
st.markdown('Utilizando Processamento de Linguagem Natural (NLP) otimizado com N-gramas e normalização de texto para garantir a máxima integridade técnica nas coberturas do TJGO.')

@st.cache_resource
def carregar_recursos():
    try:
        # Leitura puramente relativa voltada exclusivamente para a raiz do repositório no GitHub / Streamlit Cloud
        modelo = joblib.load('modelo_jornalismo.pkl')
        database = joblib.load('database_sugestoes.pkl')
        return modelo, database
    except Exception as e:
        st.sidebar.error(f"Erro de leitura na nuvem: {e}")
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[TJGO - Portal de Precatórios Oficiais](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[TJGO - Sistemas, Manuais e Avisos de Indisponibilidade](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[TJGO - Consulta Unificada de Jurisprudência e Súmulas](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[TJGO - Comitê Estadual de Saúde e Pareceres do NATJUS](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[TJGO - Centro de Inteligência e Projetos de Inovação](https://www.tjgo.jus.br/index.php/centro-de-inteligencia)',
    'Violência contra a Mulher': '[TJGO - Coordenadoria Estadual da Mulher](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl de forma relativa. Verifique se eles estão na raiz do seu repositório no GitHub!')
else:
    tema_escolhido = st.selectbox(
        'Escolha a categoria da matéria jurídica:',
        ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
    )

    if tema_escolhido in referencias_goias:
        st.info(f'📚 **Fonte Técnica de Consulta recomendada para Goiás:** {referencias_goias[tema_escolhido]}')

    texto_materia = st.text_area(
        'Insira a matéria completa ou o rascunho de parágrafo:',
        placeholder='Escreva aqui o rascunho para submeter à auditoria avançada...',
        height=250
    )

    if st.button('Auditar Texto com Alta Precisão', type='primary'):
        if not texto_materia.strip():
            st.warning('Por favor, digite algum texto para análise.')
        else: 
            sentencas = [s.strip() for s in re.split(r'[.!?\n]+', texto_materia) if len(s.strip()) > 5]

            st.subheader('📊 Relatório de Auditoria de Linguagem')

            alertas_detectados = 0
            for s in sentencas:
                probabilidades = modelo_local.predict_proba([s])[0]
                percentual_sensibilidade = probabilidades[1]

                if percentual_sensibilidade >= 0.65:
                    alertas_detectados += 1
                    st.error(f'🚨 **RISCO CRÍTICO ({percentual_sensibilidade:.1%}):** {s}')

                    sugestao = None
                    if db_sugestoes is not None:
                        snippet = s[:15]
                        match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(snippet), na=False, case=False)]
                        if not match.empty and match.iloc[0]['sugestao'] is not None:
                            sugestao = match.iloc[0]['sugestao']

                    if sugestao:
                        st.success(f'💡 **Sugestão de Reescrita Recomendada:** {sugestao}')
                    else:
                        st.info('💡 **Recomendação:** Remova julgamentos de valor, evite culpar partes e apoie-se estritamente na redação processual do TJGO.')
                    st.write('---')

                elif percentual_sensibilidade >= 0.45:
                    alertas_detectados += 1
                    st.warning(f'⚠️ **RISCO MODERADO ({percentual_sensibilidade:.1%}):** {s}')
                    st.info('💡 **Aviso:** O texto está próximo da linha da parcialidade ou utiliza termos vagos. Certifique-se de citar as fontes oficiais e o andamento processual correto do tribunal.')
                    st.write('---')

            if alertas_detectados == 0:
                st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta e linguagem ética recomendada pelo TJGO.')
