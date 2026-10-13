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

# Estilização CSS limpa e moderna integrada de forma segura
st.markdown("""<style>
.reportview-container {
    background: #fafafa;
}
.feedback-box {
    background-color: #f0f4f9;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #d3e3fd;
    color: #1f1f1f;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
}
.texto-destaque {
    background-color: #e9eef6;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: monospace;
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
st.markdown('### Uma conversa de redator para redator, inspirada no Gemini')
st.markdown('Escreva o rascunho da sua pauta jurídica ou geral. O assistente analisará o contexto completo e trará um feedback dissertativo, didático e amigável.')

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

modelos_textos_base = {
    'Precatórios': (
        "O Tribunal de Justiça do Estado de Goiás (TJGO) divulgou nesta semana a atualização do cronograma de pagamento de precatórios para o exercício vigente. "
        "Segundo a Diretoria de Precatórios do órgão, os repasses aos credores prioritários (como idosos e pessoas com deficiência) seguem de forma regular, "
        "respeitando rigorosamente a ordem cronológica e os antes financeiros estabelecidos pelo ente devedor estatal."
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
    'Violência contra a Mulher': (
        "O Ministério Público de Goiás, em atuação conjunta com a Coordenadoria Estadual da Mulher do TJGO, formalizou a denúncia contra o suspeito de agressão na comarca de [Cidade]. "
        "O juízo deferiu de imediato medidas protetivas de urgência previstas na Lei Maria da Penha para afastar o agressor e garantir a integridade da vítima. "
        "---\n📞 Se você ou alguém próximo vivencia situações de violência doméstica, denuncie: ligue de forma gratuita e anônima para o Ligue 180 ou acione a Polícia Militar pelo 190."
    )
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
                sugestoes_banco = []

                for s in sentencas:
                    sentenca_limpa = normalizar_texto_local(s)
                    probabilidades = modelo_local.predict_proba([sentenca_limpa])[0]
                    score_sensibilidade = probabilidades[1]

                    if score_sensibilidade >= 0.45:
                        alertas_detectados.append(s)
                        if db_sugestoes is not None:
                            fragmento = s[:15]
                            match = db_sugestoes[db_sugestoes["texto"].str.contains(re.escape(fragmento), na=False, case=False)]
                            if not match.empty and match.iloc[0]['sugestao'] is not None:
                                sugestoes_banco.append(match.iloc[0]['sugestao'])

                st.markdown('### 🧠 Retorno do Editor Sênior')

                if len(alertas_detectados) == 0:
                    feedback_texto = f"Olá! Li o seu texto com bastante atenção e achei a estrutura excelente.\n\nO tom adotado para tratar sobre **{tema_escolhido}** está perfeitamente neutro, técnico e isento. Você conseguiu transmitir a informação factual de maneira direta, sem dar espaço a ambiguidades ou adjetivações excessivas, o que é fundamental no jornalismo profissional.\n\nSua matéria está pronta e segura para publicação! Não vejo necessidade de alterações técnica ou éticas. Parabéns pelo cuidado com a escrita!"
                else:
                    introducao = f"Olá! Analisei com cuidado o seu rascunho sobre **{tema_escolhido}**.\n\nA ideia central da sua matéria é ótima, mas reparei em alguns pontos pontuais que nós, como jornalistas, precisamos tomar cuidado para evitar repercussões negativas ou desvios em relação aos manuais éticos e técnicos.\n\n"
                    diretrizes = ""
                    if tema_escolhido == 'Violência contra a Mulher':
                        diretrizes = f"* **Sobre a abordagem ética de gênero:** Notei que há trechos que podem soar como justificativa sentimental para as ações do agressor ou que de alguma forma transferem peso sobre o comportamento da vítima (por exemplo, ao mencionar rotinas, locais ou trajes). O *Manual Universa* orienta que reportagens de feminicídio ou agressão evitem termos passionais e foquem na conduta ilícita sob um tom técnico-jurídico neutro, amparando a narrativa com canais de acolhimento (como o Ligue 180).\n\n"
                    elif tema_escolhido == 'Tecnologia':
                        diretrizes = f"* **Sobre a precisão e inovação no Judiciário:** No campo da tecnologia, é muito comum darmos a entender de forma entusiasmada (ou alarmista) que os algoritmos de Inteligência Artificial estão 'julgando sozinhos' ou substituindo o crivo humano. Segundo as diretrizes da Resolução 332 do CNJ, as ferramentas operam estritamente como copilotos de organização de arquivos. Deixar claro que o magistrado é quem revisa e assina a decisão é essencial para não confundir o leitor.\n\n"
                    elif tema_escolhido == 'Língua Portuguesa':
                        diretrizes = f"* **Sobre a estrutura e concordância:** Observei detalhes no fluxo das orações que fogem um pouco do padrão culto da Língua Portuguesa (como concordâncias verbais ou nominais frágeis). Para mantermos o prestígio editorial, vale a pena priorizar a ordem direta na construção das frases (sujeito + verbo + predicado), simplificando a jornada do leitor e evitando termos de duplo sentido.\n\n"
                    else:
                        diretrizes = f"* **Sobre o tom institucional e neutralidade:** Em matérias jurídicas ou gerais, o uso de expressões com forte carga opinativa ou especulações sem o respaldo de documentos formais ou laudos técnicos do tribunal abre margem para contestações. O ideal é darmos espaço às decisões documentadas de forma impessoal.\n\n"

                    detalhe_trechos = "Veja, por exemplo, o impacto que esses pontos causam na fluidez destas partes que destaquei:\n"
                    for trecho_alerta in alertas_detectados:
                        detalhe_trechos += f"* *\"{trecho_alerta}\"*\n"

                    reescrita_sugerida = "\n### ✨ Minha proposta de reescrita:\nPara deixar o texto impecável e transparente, sugiro ajustarmos para uma redação mais direta. Veja se esta opção abaixo mantém a alma da sua apuração de forma segura:\n\n"
                    if sugestoes_banco:
                        reescrita_sugerida += f"\"{' '.join(sugestoes_banco)}\"\n\n"
                    else:
                        reescrita_sugerida += "*\"[Foque na ordem direta, cite as decisões institucionais de forma impessoal e remova termos que denotem sentimentos ou prejulgamentos de valor]\"*\n\n"

                    reescrita_sugerida += "O que acha de adotar esse formato? O jornalista ganha em blindagem jurídica e o leitor em clareza factual. Conte comigo se quiser ajustar outros detalhes!"
                    feedback_texto = introducao + diretrizes + detalhe_trechos + reescrita_sugerida

                st.markdown(f'<div class="feedback-box">{feedback_texto}</div>', unsafe_allow_html=True)

    with aba_ajuda:
        st.markdown('#### 📚 Portais de Apoio Consultivo')
        for k, v in referencias_goias.items():
            st.markdown(f'* **{k}**: {v}')
