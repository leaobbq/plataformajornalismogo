import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os

st.set_page_config(
    page_title='Revisor Editorial Conversacional',
    page_icon='⚖️',
    layout='centered'
)

# Estilização CSS limpa e moderna para emular o design de chat rico
st.markdown('''<style>
.reportview-container {
    background: #fafafa;
}
.feedback-box {
    background-color: #f0f4f9;
    padding: 24px;
    border-radius: 16px;
    border: 1px solid #d3e3fd;
    color: #1f1f1f;
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.7;
    margin-bottom: 20px;
}
.card-erro {
    background-color: #fff5f5;
    border: 1px solid #feb2b2;
    border-left: 6px solid #e53e3e;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 12px;
}
.card-sugestao {
    background-color: #f0fff4;
    border: 1px solid #9ae6b4;
    border-left: 6px solid #38a169;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.sub-titulo {
    font-weight: bold;
    font-size: 15px;
    margin-bottom: 6px;
}
</style>''', unsafe_allow_html=True)

st.title('⚖️ Revisor Editorial Conversacional')
st.markdown('### Uma análise detalhada e construtiva, período por período')
st.markdown('Escreva o rascunho da sua pauta. O sistema avaliará cada sentença de acordo com as regras de redação e ética do tribunal de forma 100% local.')

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
        modelo_path = '/content/modelo_jornalismo.pkl' if os.path.exists('/content/modelo_jornalismo.pkl') else 'modelo_jornalismo.pkl'
        database_path = '/content/database_sugestoes.pkl' if os.path.exists('/content/database_sugestoes.pkl') else 'database_sugestoes.pkl'
        return joblib.load(modelo_path), joblib.load(database_path)
    except:
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

if modelo_local is None:
    st.error('❌ Não foi possível carregar os artefatos (.pkl). Certifique-se de executar as células de treino.')
else:
    tema_escolhido = st.selectbox(
        'Escolha o tema principal do texto:',
        ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
    )

    if tema_escolhido in referencias_goias:
        st.info(f'📚 **Links e Referências recomendadas para o tema:** {referencias_goias[tema_escolhido]}')

    texto_materia = st.text_area('Insira o seu rascunho de texto aqui:', height=200)

    if st.button('Iniciar Revisão Conversal', type='primary'):
        if not texto_materia.strip():
            st.warning('Escreva uma pauta jurídica antes de analisar.')
        else:
            # Divide o rascunho por sentenças de forma limpa
            sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]

            alertas_detectados = []
            sentencas_finais = []

            for s in sentencas:
                sentenca_limpa = normalizar_texto_local(s)
                probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                score_sensibilidade = probabilidades[1]

                # Se o modelo ou banco de dados identificou sensibilidade
                if score_sensibilidade >= 0.45:
                    sugestao_mapeada = None
                    justificativa_mapeada = None

                    if db_sugestoes is not None:
                        db_sugestoes['texto_normalizado'] = db_sugestoes['texto'].apply(normalizar_texto_local)
                        match = db_sugestoes[db_sugestoes['texto_normalizado'].str.contains(re.escape(sentenca_limpa[:15]), na=False)]
                        if not match.empty:
                            sugestao_mapeada = match.iloc[0]['sugestao']
                            if 'erro_identificado' in match.columns:
                                justificativa_mapeada = match.iloc[0]['erro_identificado']

                    if not justificativa_mapeada:
                        if tema_escolhido == 'Violência contra a Mulher':
                            justificativa_mapeada = 'Este trecho pode ferir as regras do Manual Universa por conter termos desatualizados (como crime passional) ou transferir culpa à conduta da vítima.'
                        elif tema_escolhido == 'Tecnologia':
                            justificativa_mapeada = 'O trecho apresenta sensibilidade ao dar a entender que decisões judiciais são tomadas autonomamente por inteligência artificial, contrariando a Resolução 332 do CNJ.'
                        else:
                            justificativa_mapeada = 'O período apresenta adjetivos de teor opinativo ou coloquial que comprometem o princípio de imparcialidade editorial.'

                    alertas_detectados.append({
                        'sentenca': s,
                        'erro': justificativa_mapeada,
                        'sugestao': sugestao_mapeada
                    })

                    if sugestao_mapeada:
                        sentencas_finais.append(sugestao_mapeada)
                    else:
                        sentencas_finais.append(s)
                else:
                    sentencas_finais.append(s)

            st.markdown('### 🧠 Retorno do Editor Conversacional')

            if not alertas_detectados:
                feedback_seguro = f'''Olá! Analisei com cuidado o seu rascunho de texto sobre **{tema_escolhido}**.

Fico muito feliz em informar que a sua matéria está excelente! O tom adotado está perfeitamente isento, neutro e em plena conformidade com as exigências técnicas e éticas recomendadas.

O texto está seguro e 100% pronto para publicação!'''
                st.markdown(f'<div class="feedback-box">{feedback_seguro}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'''<div class="feedback-box">
                Olá! Li o seu texto de forma atenta. A estrutura geral está ótima, mas identifiquei alguns períodos que merecem pequenos ajustes éticos ou de técnica jurídica para garantir a blindagem total da matéria.<br><br>
                Abaixo listo detalhadamente os pontos analisados de cada sentença:
                </div>''', unsafe_allow_html=True)

                for idx, item in enumerate(alertas_detectados):
                    st.markdown(f'#### 📌 Sentença Analisada {idx+1}')
                    st.warning(f'"{item["sentenca"]}"')

                    # Caixa Vermelha do Erro
                    st.markdown(f'''<div class="card-erro">
                        <div class="sub-titulo">❌ O que está errado neste trecho:</div>
                        {item["erro"]}
                    </div>''', unsafe_allow_html=True)

                    # Caixa Verde da Correção
                    if item["sugestao"]:
                        st.markdown(f'''<div class="card-sugestao">
                            <div class="sub-titulo">✨ Minha sugestão de novo texto:</div>
                            {item["sugestao"]}
                        </div>''', unsafe_allow_html=True)
                    else:
                        st.markdown('''<div class="card-sugestao">
                            <div class="sub-titulo">✨ Recomendação Geral:</div>
                            Sugiro reescrever este período utilizando a ordem direta do português, citando decisões judiciais institucionais de forma impessoal e neutra.
                        </div>''', unsafe_allow_html=True)
                    st.write('---')

                # Entrega do texto completo reescrito consolidado para cópia direta
                st.subheader('📝 Proposta de Versão Recomposta')
                st.info('Aqui está a cópia integral do seu rascunho com os devidos ajustes recomendados aplicados:')
                texto_final_recomposto = " ".join(sentencas_finais)
                st.text_area('Copiar texto corrigido:', value=texto_final_recomposto, height=180)
