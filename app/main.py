from flask import Flask, render_template, request, jsonify, abort
import pandas as pd

app = Flask(__name__)

# Caminho para os arquivos Excel
excel_file_novos = r'C:\Users\benve\Documents\sistema-LEADS EXCEL\novos.xlsx'
excel_file_seminovos = r'C:\Users\benve\Documents\sistema-LEADS EXCEL\seminovos.xlsx'


# Função utilitária para carregar um DataFrame com validações
def carregar_dataframe(tipo):
    caminho = excel_file_novos if tipo == 'novos' else excel_file_seminovos
    try:
        df = pd.read_excel(caminho, dtype={'Telefone': str})
        return df
    except Exception as e:
        abort(500, f"Erro ao carregar o arquivo Excel ({tipo}): {e}")


# Rota principal
@app.route('/')
def home():
    return render_template('index.html')


# Rota para leads de "novos"
@app.route('/novos')
def novos():
    df = carregar_dataframe('novos')
    leads_novos = df[['Cliente', 'Telefone', 'Status']].fillna("").values.tolist()
    return render_template('index-novos.html', leads=leads_novos)


# Rota para leads de "seminovos"
@app.route('/seminovos')
def seminovos():
    df = carregar_dataframe('seminovos')
    leads_seminovos = df[['Cliente', 'Telefone', 'Modelo', 'Status']].fillna("").values.tolist()
    return render_template('index-seminovos.html', leads=leads_seminovos)


# Rota para atualizar status
@app.route('/atualizar_status', methods=['POST'])
def atualizar_status():
    try:
        lead_id = int(request.form['lead_id'])
        status = request.form['status']
        tipo = request.form['tipo']

        # Validar tipo
        if tipo not in ['novos', 'seminovos']:
            abort(400, "Tipo inválido.")

        # Carregar DataFrame
        df = carregar_dataframe(tipo)

        # Validar ID
        if lead_id < 0 or lead_id >= len(df):
            abort(400, "Lead ID inválido.")

        # Atualizar status
        df.at[lead_id, 'Status'] = status
        caminho = excel_file_novos if tipo == 'novos' else excel_file_seminovos
        df.to_excel(caminho, index=False)

        return jsonify({'message': f"Status atualizado com sucesso para {tipo}!"}), 200

    except Exception as e:
        return jsonify({'error': f"Erro ao atualizar status: {e}"}), 500


# Rota para salvar observação
@app.route('/salvar_observacao', methods=['POST'])
def salvar_observacao():
    try:
        lead_id = int(request.form['lead_id'])
        observacao = request.form['observacao']
        tipo = request.form.get('tipo', 'novos')

        # Validar tipo
        if tipo not in ['novos', 'seminovos']:
            abort(400, "Tipo inválido.")

        # Carregar DataFrame
        df = carregar_dataframe(tipo)

        # Validar ID
        if lead_id < 0 or lead_id >= len(df):
            abort(400, "Lead ID inválido.")

        # Adicionar coluna "Observação" caso não exista
        if 'Observacao' not in df.columns:
            df['Observacao'] = ""

        # Atualizar observacao
        df.at[lead_id, 'Observacao'] = observacao
        caminho = excel_file_novos if tipo == 'novos' else excel_file_seminovos
        df.to_excel(caminho, index=False)

        return jsonify({'message': f"Observacao salva com sucesso para {tipo}!"}), 200

    except Exception as e:
        return jsonify({'error': f"Erro ao salvar observacao: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
