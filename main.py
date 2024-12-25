import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def listar_projetos_jira(jira):
    projetos = jira.projects()
    lista_projetos = [(projeto.key, projeto.name) for projeto in projetos]
    return lista_projetos

def listar_tipos_itens(jira):
    tipos_itens = jira.issue_types()
    lista_tipos_itens = [tipo_item.name for tipo_item in tipos_itens]
    return lista_tipos_itens

def obter_itens_jira(jira, projeto, tipos_itens, dias):
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=dias)

    tipo_item_jql = ' OR '.join([f'issuetype = "{tipo_item}"' for tipo_item in tipos_itens])
    jql_query = f'project = {projeto} AND ({tipo_item_jql}) AND statusCategory = Done AND statusCategoryChangedDate >= "{data_inicio.strftime("%Y-%m-%d")}" AND status not in (Cancelado, Cancelados, Canceled, Cancelled)'
    itens = jira.search_issues(jql_query, maxResults=False)

    return itens

def calcular_itens_por_semana(df):
    df['Resolvido'] = pd.to_datetime(df['Resolvido'])
    df['Semana'] = df['Resolvido'].dt.isocalendar().week
    itens_por_semana = df.groupby('Semana').size().reset_index(name='Itens')
    return itens_por_semana

def simulacao_monte_carlo(entregas_semanais, num_itens, num_simulacoes):
    semanas = []
    for _ in range(num_simulacoes):
        semanas_simulacao = 0
        itens_restantes = num_itens
        while itens_restantes > 0:
            entregas = np.random.choice(entregas_semanais)
            itens_restantes -= entregas
            semanas_simulacao += 1
        semanas.append(semanas_simulacao)
    return semanas