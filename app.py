import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata

st.set_page_config(
    page_title='Revisor Avançado de Tecnologia TJGO',
    page_icon='⚖️',
    layout='wide'
)

st.title('⚖️ Copiloto de Redação & Revisor de Alta Precisão - TJGO')
st.markdown('Utilizando Processamento de Linguagem Natural (NLP) otimizado para garantir integridade ética e precisão técnica em pautas do TJGO.')

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
    except Exception as e:
        st.sidebar.error(f"Erro de leitura na nuvem: {e}")
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[TJGO - Portal de Precatórios Oficiais](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[TJGO - Sistemas, Manuais e Avisos de Indisponibilidade](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[TJGO - Consulta Unificada de Jurisprudência e Súmulas](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[TJGO - Comitê Estadual de Saúde e Pareceres do NATJUS](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[TJGO - Centro de Inteligência, Projetos de Inovação e uso Ético de IA](https://www.tjgo.jus.br/index.php/centro-de-inteligencia)',
    'Violência contra a Mulher': '[TJGO - Coordenadoria Estadual da Mulher](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

modelos_textos_base = {
    'Precatórios': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) divulgou nesta semana a atualização do cronograma de pagamento de precatórios para o exercício vigente. "
        "Segundo a Diretoria de Precatórios do órgão, os repasses aos credores prioritários seguem de forma regular."
    ),
    'Alterações no Projudi': (
        "Devido a uma manutenção corretiva programada nos servidores da Diretoria de Tecnologia da Informação do TJGO, o sistema Projudi registrou períodos de oscilação técnica."
    ),
    'Tecnologia': (
        "O Tribunal de Justiça de Goiás (TJGO) expandiu o uso de modelos auxiliares de Inteligência Artificial para otimizar o fluxo de triagem e indexação de novas ações distribuídas. "
        "De acordo com o tribunal, as automações atuam estritamente como ferramentas de apoio operacional para servidores, preservando a assinatura, a revisão e a autoridade decisória final de forma exclusiva para os magistrados titulares."
    )
}

if modelo_local is None:
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos do modelo.')
else: 
    aba_auditoria, aba_modelagem = st.tabs(['🔍 Auditoria e Revisão de Texto', '💡 Gerador de Sugestões / Textos Base'])

    with aba_auditoria:
        st.header('Revisão de Redação e Tecnologia TJGO')
        tema_escolhido = st.selectbox(
            'Escolha a categoria da matéria jurídica para auditar:',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        if tema_escolhido in referencias_goias:
            st.info(f'📚 **Fonte Técnica Oficial de Consulta para Goiás:** {referencias_goias[tema_escolhido]}')

        texto_materia = st.text_area(
            'Insira a matéria completa ou o rascunho de parágrafo:',
            placeholder='Escreva aqui o rascunho sobre tecnologia judiciária ou outros temas...',
            height=250
        )

        if st.button('Auditar Texto com Alta Precisão', type='primary'):
            if not texto_materia.strip():
                st.warning('Por favor, digite algum texto para análise.')
            else:
                sentencas_originais = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 3]

                st.subheader('📊 Relatório de Auditoria de Linguagem')
                alertas_detectados = 0
                sentencas_sugeridas = []

                for s in sentencas_originais:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    percentual_sensibilidade = probabilidades[1]

                    if percentual_sensibilidade >= 0.45:
                        alertas_detectados += 1
                        tipo_risco = "🚨 RISCO CRÍTICO" if percentual_sensibilidade >= 0.65 else "⚠️ RISCO MODERADO"
                        
                        if percentual_sensibilidade >= 0.65:
                            st.error(f'**{tipo_risco} ({percentual_sensibilidade:.1%}):** {s}')
                        else:
                            st.warning(f'**{tipo_risco} ({percentual_sensibilidade:.1%}):** {s}')

                        # Dicas específicas para o tema Tecnologia
                        if tema_escolhido == 'Tecnologia':
                            st.caption("💡 **Diretriz de Tecnologia e IA no Judiciário:** Evite termos que sugiram que decisões judiciais são tomadas de forma 100% autônoma por robôs ou máquinas. Deixe claro o caráter de 'copiloto', 'suporte', 'ferramenta de auxílio técnico' ou 'automação de tarefas burocráticas repetitivas', sempre sob supervisão humana.")

                        # Busca de sugestão estruturada
                        sugestao = None
                        if db_sugestoes is not None:
                            snippet = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(snippet), na=False, case=False)]
                            if not match.empty and match.iloc[0]['sugestao'] is not None:
                                sugestao = match.iloc[0]['sugestao']

                        if sugestao:
                            st.success(f'✨ **Sugestão de Reescrita Técnica:** {sugestao}')
                            sentencas_sugeridas.append(sugestao)
                        else:
                            sentencas_sugeridas.append(s)
                        st.write('---')
                    else:
                        sentencas_sugeridas.append(s)

                if alertas_detectados > 0:
                    st.subheader('📝 Versão Sugerida de Texto Alterado')
                    texto_alterado_completo = " ".join(sentencas_sugeridas)
                    st.text_area('Copie a matéria ajustada abaixo:', value=texto_alterado_completo, height=200)
                else:
                    st.success('✅ **Excelente!** O texto passou na nossa auditoria avançada. Mantém integridade técnica absoluta e linguagem ética recomendada pelo TJGO.')

    with aba_modelagem:
        st.header('💡 Sugestão de Textos e Modelos de Redação')
        st.write('Selecione uma categoria abaixo para obter um texto-modelo estruturado de forma imparcial e clara.')

        tema_modelo = st.selectbox(
            'Selecione o tema para gerar a sugestão de redação:',
            ['Precatórios', 'Alterações no Projudi', 'Tecnologia']
        )

        if tema_modelo in modelos_textos_base:
            st.subheader(f'📝 Modelo de Redação Recomendado: {tema_modelo}')
            st.text_area('Copie o texto base sugerido abaixo:', value=modelos_textos_base[tema_modelo], height=180)
