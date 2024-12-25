import streamlit as st
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import auth_jira
import main

st.title('Previsão')

if auth_jira.servidor and auth_jira.usuario and auth_jira.token:
    jira = auth_jira.autenticar_jira(auth_jira.servidor, auth_jira.usuario, auth_jira.token)

    lista_projetos = main.listar_projetos_jira(jira)
    escolhas_projeto = [f"{key} - {name}" for key, name in lista_projetos]
    escolha_projeto = st.selectbox("Projeto", escolhas_projeto)
    chave_projeto = escolha_projeto.split(" - ")[0]

    lista_tipos_itens = main.listar_tipos_itens(jira)
    escolhas_tipo_itens = st.multiselect("Tipo de item", lista_tipos_itens)

    st.session_state['chave_projeto'] = chave_projeto
    st.session_state['tipo_itens'] = escolhas_tipo_itens
else:
    st.warning('Sem dados de autenticação do Jira')

projeto = st.session_state.get('chave_projeto')
tipos_itens = st.session_state.get('tipo_itens')
dias = st.number_input('Dias anteriores', min_value=1, max_value=365, value=30)
data_inicio = st.date_input('Data de início', datetime.today())
num_simulacoes = st.number_input('Número de simulações', min_value=1, max_value=10000, value=1000)
num_itens = st.number_input('Número de itens para simular', min_value=1, max_value=1000, value=100)

if st.button('Simular'):
    if not auth_jira.servidor or not auth_jira.usuario or not auth_jira.token or not projeto or not tipos_itens:
        st.error('Preencha todos os campos e selecione projeto/tipos de itens')
    else:
        jira = auth_jira.autenticar_jira(auth_jira.servidor, auth_jira.usuario, auth_jira.token)
        itens = main.obter_itens_jira(jira, projeto, tipos_itens, dias)

        if itens:
            dados = {
                'Chave': [item.key for item in itens],
                'Resumo': [item.fields.summary for item in itens],
                'Resolvido': [item.fields.statuscategorychangedate for item in itens]
            }
            df = pd.DataFrame(dados)

            itens_por_semana = main.calcular_itens_por_semana(df)

            st.dataframe(df)
            st.bar_chart(itens_por_semana.set_index('Semana'))

            entregas_semanais = itens_por_semana['Itens'].tolist()
            semanas = main.simulacao_monte_carlo(entregas_semanais, num_itens, num_simulacoes)

            percentil_85 = np.percentile(semanas, 85)
            semana_percentil_85 = int(percentil_85)
            data_percentil_85 = (datetime.combine(data_inicio, datetime.min.time()) + timedelta(weeks=semana_percentil_85)).strftime('%Y-%m-%d')

            st.write(f"Resultados da Simulação de Monte Carlo para {num_itens} itens:")
            st.write(f"Semanas médias necessárias: {np.mean(semanas):.2f}")
            st.write(f"Semanas mínimas necessárias: {min(semanas)}")
            st.write(f"Semanas máximas necessárias: {max(semanas)}")
            st.write(f"Semanas necessárias no percentil 85: {percentil_85:.2f}")
            st.write(f"Data estimada de conclusão para o percentil 85: {data_percentil_85}")

            hist_values, bin_edges = np.histogram(semanas, bins=range(min(semanas), max(semanas) + 1), density=False)
            hist_df = pd.DataFrame({'Semanas': bin_edges[:-1], 'Frequência': hist_values})
            st.bar_chart(hist_df.set_index('Semanas'))
        else:
            st.write('Nenhum item encontrado')