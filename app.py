import json
import os
from flask import Flask, render_template, request, redirect, url_for # Aqui chamamos a ferramenta
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__) # Aqui criamos o "aplicativo"

UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
#Isso garante que o Python ache o arquivo JSON nao importa onde ele esteja no servidor
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'aniversarios.json')

def carregar_dados():
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return{} #retorna um dicionario vazio
    
def salvar_dados(dados_completos):
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados_completos, f, indent=4, ensure_ascii=False)

def calcular_dias_faltantes(data_aniversario):
    hoje = datetime.now() #pega a data e hora de agora
    dia, mes = map(int, data_aniversario.split('/'))
    data_este_ano = datetime(hoje.year,mes,dia)
    
    if data_este_ano < hoje:  #se o aniversário já passou este ano...
        data_proximo = datetime(hoje.year+1,mes,dia) #...olhamos para o ano que vem!
    else:
        data_proximo = data_este_ano

    diferenca = data_proximo - hoje
    return diferenca.days #retorna apenas o numero de dias

@app.route('/<usuario>') # Isso diz: "Quando eu acessar a página inicial..."
def home(usuario):
    todos_os_dados = carregar_dados()

    lista_do_usuario = todos_os_dados.get(usuario,[])

    for pessoa in lista_do_usuario:
        #chamamos a lógica de cálculo para cada um
        dias = calcular_dias_faltantes(pessoa['data'])
        pessoa['dias_que_faltam']= dias #criamos uma chave nova na hora!
        if dias <= 30:
            pessoa['status'] = "URGENTE: Preparar presente!"
        else:
            pessoa['status'] = "Traquilo como um grilo"
    
    lista_do_usuario.sort(key=lambda x: x['dias_que_faltam'])
    return render_template('index.html', lista=lista_do_usuario, usuario=usuario)

    #Isso ordena a lista baseada na chave 'dias_que_faltam'

@app.route('/adicionar/<usuario>',methods=['POST'])
def adicionar(usuario):
    todos_os_dados = carregar_dados()
    
    # O 'request.form' pega o que você escreveu no 'name' lá no HTML
    nome_recebido = request.form.get('nome')
    data_recebida = request.form.get('data')
    presente_recebido = request.form.get('presente')

    fotos_caminhos = []
    for i in range(1, 5):
        arquivo = request.files.get(f'foto{i}')

        if arquivo and arquivo.filename != '':
            estensao = arquivo.filename.rsplit('.', 1)[1].lower()
            nome_arquivo = f"{usuario}_{nome_recebido}_{i}.{estensao}"
            caminho_pasta = os.path.join('static/uploads', nome_arquivo)

            arquivo.save(caminho_pasta)

            fotos_caminhos.append(f"/{caminho_pasta}")
        else:
            fotos_caminhos.append("")

    novo_amigo = {
        "Nome": nome_recebido,
        "data": data_recebida,
        "presente": presente_recebido,
        "foto1": fotos_caminhos[0],
        "foto2": fotos_caminhos[1],
        "foto3": fotos_caminhos[2],
        "foto4": fotos_caminhos[3]
    }

    if usuario not in todos_os_dados:
         todos_os_dados[usuario]=[]

    todos_os_dados[usuario].append(novo_amigo)
    salvar_dados(todos_os_dados)

    # Redireciona de volta para a página inicial para vermos a lista atualizada
    return redirect(f'/{usuario}')
@app.route('/deletar/<usuario>/<nome_da_pessoa>')
def deletar(usuario,nome_da_pessoa):
    todos_os_dados = carregar_dados()

    if usuario in todos_os_dados:
         todos_os_dados[usuario] = [p for p in todos_os_dados[usuario]if p['Nome'] != nome_da_pessoa]
    salvar_dados(todos_os_dados)

    return redirect(f'/{usuario}')

if __name__ == "__main__":
     app.run(debug=True) # Isso liga o motor do site