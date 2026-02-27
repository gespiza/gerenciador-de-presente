from flask import Flask # Aqui chamamos a ferramenta

app = Flask(__name__) # Aqui criamos o "aplicativo"

@app.route('/') # Isso diz: "Quando eu acessar a página inicial..."
def home():
    return "<h1>Gerenciador de Presentes</h1><p>Em breve, a lista de aniversários aqui!</p>"

if __name__ == '__main__':
    app.run(debug=True) # Isso liga o motor do site