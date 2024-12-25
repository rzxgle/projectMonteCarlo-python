from jira import JIRA

servidor = ''
usuario = ''
token = ''

def autenticar_jira(servidor, usuario, token):
    opcoes = {'server': servidor}
    return JIRA(opcoes, basic_auth=(usuario, token))