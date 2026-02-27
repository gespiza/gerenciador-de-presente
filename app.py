import json
import os
from flask import Flask, render_template, request, redirect # Aqui chamamos a ferramenta
from datetime import datetime

app = Flask(__name__) # Aqui criamos o "aplicativo"

#Isso garante que o Python ache o arquivo JSON nao importa onde ele esteja no servidor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'aniversarios.json')

def carregar_dados():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return[]
    
def salvar_dados(lista):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

#Agora a nossa lista oficial comeca lendo o que está no arquivo!
aniversarios = carregar_dados()

def calcular_dias_faltantes(data_aniversario):
    hoje = datetime.now() #pega a data e hora de agora
    dia, mes = map(int, data_aniversario.split('/'))

    data_este_ano = datetime(hoje.year,mes,dia)
    
    #se o aniversário já passou este ano...
    if data_este_ano < hoje:
        #...olhamos para o ano que vem!
        data_proximo = datetime(hoje.year+1,mes,dia)
    else:
        data_proximo = data_este_ano
    diferenca = data_proximo - hoje
    return diferenca.days #retorna apenas o numero de dias

@app.route('/') # Isso diz: "Quando eu acessar a página inicial..."
def home():
    for pessoa in aniversarios:
        #chamamos a lógica de cálculo para cada um
        dias = calcular_dias_faltantes(pessoa['data'])
        pessoa['dias_que_faltam']= dias #criamos uma chave nova na hora!

        #Lógica do "presente elaborado"
        if dias <= 30:
            pessoa['status'] = "URGENTE: Preparar presente!"
        else:
            pessoa['status'] = "Traquilo como um grilo"

    #Isso ordena a lista baseada na chave 'dias_que_faltam'
    aniversarios.sort(key=lambda x: x['dias_que_faltam'])

    return render_template('index.html', lista=aniversarios)

@app.route('/adicionar',methods=['POST'])
def adicionar():
    # O 'request.form' pega o que você escreveu no 'name' lá no HTML
    nome_digitado = request.form.get('nome')
    data_digitada = request.form.get('data')
    presente_digitado = request.form.get('presente')

    # Criamos um novo dicionário com esses dados
    novo_amigo = {
        "Nome": nome_digitado,
        "data": data_digitada,
        "Presente": presente_digitado
    }
    # Adicionamos na nossa lista oficial
    aniversarios.append(novo_amigo)

    salvar_dados(aniversarios) #magica acontece aqui

    # Redireciona de volta para a página inicial para vermos a lista atualizada
    return redirect('/')
@app.route('/deletar/<nome_da_pessoa>')
def deletar(nome_da_pessoa):
    global aniversarios #avisa que vamos mexer na lista principal

    #cria uma nova lista sem a pessoa que queremos deletar
    aniversarios = [p for p in aniversarios if p['Nome'] != nome_da_pessoa]

    salvar_dados(aniversarios) #salva a lista limpa no JSON
    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True) # Isso liga o motor do site