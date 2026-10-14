import streamlit as st
import joblib
import re
import pandas as pd
import unicodedata
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

st.set_page_config(
    page_title='Copiloto Editorial TJGO (IA Evolutiva)',
    page_icon='⚖️',
    layout='centered'
)

# CSS isolado de forma limpa e segura contra erros decimais
st.markdown('<style>.reportview-container { background: #fafafa; } .feedback-box { background-color: #f0f4f9; padding: 20px; border-radius: 16px; border: 1px solid #d3e3fd; color: #1f1f1f; font-family: sans-serif; line-height: 1.6; } .destaque-erro { background-color: #fde8e8; color: #9b1c1c; padding: 10px 14px; border-radius: 6px; border-left: 6px solid #f05252; margin: 8px 0; } .destaque-correcao { background-color: #def7ec; color: #03543f; padding: 10px 14px; border-radius: 6px; border-left: 6px solid #31c48d; margin: 8px 0; }</style>', unsafe_allow_html=True)

st.title('⚖️ Copiloto Editorial & Revisor Evolutivo')
st.markdown('### Um assistente de redação que aprende com cada matéria inserida no sistema!')

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
        return joblib.load(modelo_path), joblib.load(database_path)
    except Exception as e:
        return None, None

modelo_local, db_sugestoes = carregar_recursos()

if modelo_local is None:
    st.error('❌ Erro de NLP: Não foi possível carregar os arquivos modelo_jornalismo.pkl ou database_sugestoes.pkl. Execute as células de treino do notebook Colab antes.')
else:
    aba_auditoria, aba_alimentar = st.tabs(['🔍 Analisar Rascunho', '📈 Alimentar Inteligência do Sistema'])

    with aba_auditoria:
        tema_escolhido = st.selectbox(
            'Qual é o assunto principal da sua matéria?',
            ['Geral', 'Precatórios', 'Alterações no Projudi', 'Precedentes Judiciais', 'Saúde Técnica', 'Tecnologia', 'Violência contra a Mulher']
        )

        texto_materia = st.text_area('Insira o seu rascunho aqui:', placeholder='Escreva livremente o seu parágrafo ou matéria completa...', height=220)

        if st.button('Revisar com o Copiloto', key='btn_revisar'):
            if not texto_materia.strip():
                st.warning('Por favor, escreva algum rascunho de texto antes de prosseguir.')
            else:
                sentencas = [s.strip() for s in re.split(r'(?<=[.!?])\s+', texto_materia) if len(s.strip()) > 4]
                alertas_detectados = []
                trechos_detalhes = []

                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.45:
                        alertas_detectados.append(s)
                        sugestao_encontrada = None
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty and match.iloc[0]['sugestao'] is not None:
                                sugestao_encontrada = match.iloc[0]['sugestao']

                        trechos_detalhes.append((s, sugestao_encontrada))

                st.markdown('### 🧠 Retorno do Editor Sênior')

                if len(alertas_detectados) == 0:
                    feedback_texto = f"Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.\n\nO tom adotado para tratar sobre **{tema_escolhido}** está perfeitamente neutro, técnico e isento. Você conseguiu transmitir a informação factual de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional.\n\nSua matéria está pronta e totalmente segura para publicação! Parabéns pelo cuidado com a escrita!"
                    st.markdown(f'<div class="feedback-box">{feedback_texto}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f"### 📌 Análise de Sensibilidade ({tema_escolhido})")
                    for original, sugestao in trechos_detalhes:
                        st.markdown("**Original com desvio localizado (vermelho):**")
                        st.markdown(f'<div class="destaque-erro">{original}</div>', unsafe_allow_html=True)
                        if sugestao:
                            st.markdown("**Sugestão de redação polida (verde):**")
                            st.markdown(f'<div class="destaque-correcao">{sugestao}</div>', unsafe_allow_html=True)
                        else:
                            st.info("💡 *Recomendação:* Procure reescrever este período utilizando termos técnicos e neutros, evitando adjetivos pessoais ou tom coloquial.")
                        st.write("---")

    with aba_alimentar:
        st.header('📈 Alimentar Inteligência do Sistema')
        st.markdown('Insira novas sentenças avaliadas para treinar o classificador local de forma ativa. Assim o sistema evolui a cada matéria nova inserida!')

        novo_texto = st.text_area('Frase ou parágrafo novo:', placeholder='Exemplo: O prefeito assinou a portaria municipal ontem de manhã.')
        opcao_classe = st.radio('Classificação técnica da frase:', ('Seguro / Neutro (Classe 0)', 'Sensível / Precisa de Atenção (Classe 1)'))
        nova_sugestao = st.text_input('Sugestão de melhoria (Opcional):', placeholder='Exemplo de reescrita ideal para este caso...')

        if st.button('Gravar e Retreinar Sistema', type='primary'):
            if not novo_texto.strip():
                st.warning('Preencha o campo de texto antes de prosseguir.')
            else:
                classe_num = 1 if 'Classe 1' in opcao_classe else 0
                
                # Adicionar ao banco de dados existente
                nova_linha = pd.DataFrame([{
                    'texto': novo_texto,
                    'sensivel': classe_num,
                    'tema': 'Geral',
                    'sugestao': nova_sugestao if nova_sugestao.strip() else None
                }])
                
                db_atualizado = pd.concat([db_sugestoes, nova_linha], ignore_index=True).drop_duplicates(subset=['texto']).reset_index(drop=True)
                db_atualizado['texto_treino'] = db_atualizado['texto'].apply(normalizar_texto_local)
                
                # Retreinamento dinâmico em tempo de execução
                pipeline_novo = make_pipeline(
                    TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                    LogisticRegression(C=2.5, class_weight='balanced')
                )
                pipeline_novo.fit(db_atualizado['texto_treino'], db_atualizado['sensivel'])
                
                # Salvar arquivos de volta fisicamente
                joblib.dump(pipeline_novo, 'modelo_jornalismo.pkl')
                joblib.dump(db_atualizado, 'database_sugestoes.pkl')
                if os.path.exists('/content/'):
                    joblib.dump(pipeline_novo, '/content/modelo_jornalismo.pkl')
                    joblib.dump(db_atualizado, '/content/database_sugestoes.pkl')
                
                st.success('🎉 Sensacional! O sistema foi alimentado com o novo exemplo, o modelo preditivo foi retreinado e está atualizado com sucesso!')
                st.info('Reinicie a página ou execute uma nova consulta para testar o comportamento aprendido.')
