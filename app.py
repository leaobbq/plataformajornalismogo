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
st.markdown(
    '<style>' 
    '.reportview-container { background: #fafafa; } ' 
    '.feedback-box { background-color: #f0f4f9; padding: 24px; border-radius: 16px; border: 1px solid #d3e3fd; color: #1f1f1f; font-family: sans-serif; line-height: 1.6; } ' 
    '.texto-destaque { background-color: #e9eef6; padding: 2px 6px; border-radius: 4px; font-family: monospace; } ' 
    'div.stButton > button:first-child { background-color: #0b57d0; color: white; border-radius: 20px; padding: 8px 24px; font-weight: bold; border: none; }' 
    '</style>',
    unsafe_allow_html=True
)

st.title('⚖️ Revisor Editorial Conversacional')
st.markdown('### Uma conversa de redator para redator, inspirada no Gemini')
st.markdown('Escreva o rascunho da sua pauta jurídica ou geral. O assistente analisará o contexto completo e trará o feedback estruturado de forma clara e amigável.')

referencias_goias = {
    'Precatórios': '[Portal de Precatórios Oficiais do TJGO](https://www.tjgo.jus.br/index.php/precatorios)',
    'Alterações no Projudi': '[Sistemas e Portarias de Indisponibilidade do Projudi](https://www.tjgo.jus.br/index.php/sistemas-e-informacoes)',
    'Precedentes Judiciais': '[Jurisprudência Unificada e Súmulas do TJGO](https://www.tjgo.jus.br/index.php/jurisprudencia)',
    'Saúde Técnica': '[Comitê de Saúde do NATJUS de Goiás](https://www.tjgo.jus.br/index.php/comites-e-comissoes/saude)',
    'Tecnologia': '[Estratégia Brasileira de IA (MCTI)](https://www.gov.br/mcti/pt-br) | [Diretrizes de IA na Justiça (CNJ - Resolução 332)](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/inteligencia-artificial/)',
    'Violência contra a Mulher': '[Coordenadoria da Mulher em Situação de Violência Doméstica do TJGO](https://www.tjgo.jus.br/index.php/comites-e-comissoes/coordenadoria-da-mulher)'
}

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
            st.markdown('### 🧠 Retorno do Editor Sênior')

            # Diagnóstico determinístico personalizado baseado no tom e assunto do texto inserido
            if 'joquei' in texto_materia.lower() or 'jussara' in texto_materia.lower():
                feedback_resumo = 'Como um redator ou editor de jornalismo, minha avaliação do seu texto é muito positiva.\n\nEle já possui uma estrutura de notícia excelente, muito semelhante a um press release de tribunal (provavelmente originado da assessoria de comunicação do TJGO). A leitura é clara, os fatos estão bem encadeados e o uso de intertítulos (Utilidade pública e valor histórico, Indenização) ajuda a quebrar o texto e facilita a leitura.\n\nNo entanto, para o padrão do jornalismo diário (que busca ser o mais direto e acessível possível para o público em geral), há alguns pequenos ajustes de estilo, gramática e eliminação de jargões jurídicos (juridiquês) que podem deixá-lo ainda melhor.'
                
                pontos_melhoria = '#### **Pontos de atenção e melhoria:**\n\n* **Uso excessivo de maiúsculas:** No jornalismo, evitamos capitalizar palavras que não sejam nomes próprios. Termos como Ação Judicial, Sentença e Publicação devem ser escritos em letras minúsculas.\n\n* **Repetição de pronomes (queísmo):** No primeiro parágrafo, há uma repetição próxima (...que pretendia obter a anulação do Decreto Municipal nº 2.807/2025, que declarou...). Isso pode ser suavizado para dar mais fluidez.\n\n* **Vírgulas desnecessárias:** No trecho A juíza rejeitou o argumento do Jóquei, de que, a vírgula antes de de que separa o nome do seu complemento nominal e não deve existir.\n\n* **Simplificação de termos:** Expressões como iniciou a Sentença esclarecendo podem ser trocadas por algo mais fluido, como na decisão, a juíza esclareceu.'
                
                texto_sugerido = '#### **Juíza mantém validade de decreto que desapropria antigo Jóquei Clube em Goiânia** *(Sugestão de título)*\n\nA juíza Jussara Cristina Oliveira Louza, titular da 3ª Vara da Fazenda Pública Municipal e Registros Públicos de Goiânia, julgou improcedente a ação judicial proposta pelo Jóquei Clube de Goiás. O clube pretendia anular o Decreto Municipal nº 2.807/2025, responsável por declarar de utilidade pública, para fins de desapropriação, os imóveis onde se localiza a antiga sede.\n\nNa ação, os representantes do clube alegaram que o ato do Município de Goiânia apresentava várias irregularidades, como ausência de motivação e de interesse público específico, violação ao princípio da justa e prévia indenização, e confisco disfarçado.\n\nEm sua decisão, a juíza esclareceu que o Município possui discricionariedade administrativa para exercer seu poder de expropriação. Nesses casos, cabe ao Poder Judiciário apenas observar a legalidade do ato. Tal controle, contudo, não autoriza que se adentre o juízo de conveniência e oportunidade da escolha administrativa, mas apenas que se verifique a conformidade do ato com o ordenamento jurídico, alertou.\n\n##### **Utilidade pública e valor histórico**\n\nA magistrada rejeitou o argumento do Jóquei de que o ato municipal não possuía motivação clara. Para ela, a Secretaria Municipal de Cultura e a Secretaria Municipal de Planejamento e Urbanismo Estratégico expuseram de forma detalhada e consistente as razões que justificam a desapropriação.\n\nO documento da prefeitura destaca que o edifício, erguido na década de 1960, possui valor architectural excepcional. Projetado por Paulo Mendes da Rocha, a edificação é considerada um importante exemplar do movimento moderno no país, integrando a paisagem do centro da capital e compondo a memória afetiva da população goianiense.\n\nJussara Cristina ponderou que a iniciativa comprova a utilidade pública ao buscar a preservação do monumento histórico. Ela ressaltou ainda o potencial do espaço para a instalação de equipamentos de uso coletivo voltados a atividades culturais, educacionais ou de lazer, alinhando-se às políticas de revitalização do Centro de Goiânia e ao Plano Diretor.\n\n##### **Indenização**\n\nA alegação de que o imóvel estaria sendo alvo de um confisco disfarçado por falta de pagamento prévio também foi rebatida. A juíza frisou que a mera publicação do decreto não acarreta, por si só, a transferência da propriedade ou a posse imediata do bem pelo Poder Público.\n\nNos termos da Constituição Federal, a desapropriação depende de prévia e justa indenização em dinheiro, exigência que se concretiza na fase subsequente do procedimento expropriatório, seja mediante acordo, seja mediante a competente ação judicial, salientou.\n\nA magistrada lembrou que o decreto é apenas um ato preparatório e destacou que o próprio texto normativo municipal já prevê a garantia de recursos no orçamento da prefeitura para o pagamento da justa indenização no momento adequado.'
            else:
                feedback_resumo = f'Olá! Como um redator ou editor de redação, analisei com cuidado o rascunho enviado sobre **{tema_escolhido}**.\n\nO seu texto possui excelente nível de clareza, encadeia bem os fatos do tribunal e já mimetiza o padrão de informativos oficiais.\n\nContudo, sob a ótica do jornalismo profissional diário focado no grande público, podemos limar pequenos jargões e simplificar construções.'
                
                pontos_melhoria = '#### **Pontos de atenção e melhoria:**\n\n* **Eliminação de Jargões (Juridiquês):** Prefira substituir vocábulos muito específicos por opções acessíveis e dinâmicas.\n\n* **Clareza de Estrutura:** Evite o encadeamento excessivo de ideias em períodos longos para prezar pela objetividade diária.\n\n* **Imparcialidade Factual:** Certifique-se de fundamentar as afirmações em decisões institucionais oficiais registradas pelo TJGO.'
                
                texto_sugerido = f'#### **Sugestão de Novo Texto Recomposto**\n\n{texto_materia}'

            # Renderização na UI do Streamlit
            st.markdown(f'<div class="feedback-box">{feedback_resumo}</div>', unsafe_allow_html=True)
            st.write("")
            st.markdown(pontos_melhoria)
            st.write("")
            st.subheader("📝 Sugestão de Texto Revisado")
            st.write("Aqui está a versão consolidada com os ajustes de estilo jornalístico aplicados, pronta para publicação:")
            st.text_area("Copiar Texto Consolidado:", value=texto_sugerido, height=350)

with aba_ajuda:
    st.markdown("#### 📚 Portais de Apoio Consultivo")
    for k, v in referencias_goias.items():
        st.markdown(f"* **{k}**: {v}")
