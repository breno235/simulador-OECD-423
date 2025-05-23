from flask import Flask, request, jsonify, render_template, send_file
from math import exp
import os
import json

app = Flask(__name__)

HISTORICO_ARQUIVO = "resultados_teste.txt"
USADOS_ARQUIVO = "ratos_usados.json"

if os.path.exists(USADOS_ARQUIVO):
    with open(USADOS_ARQUIVO, "r") as f:
        USADOS = set(json.load(f))
else:
    USADOS = set()

def define_substances():
    return {
        "Paracetamol": {"dl50": 338, "slope": 6, "cid": 1983},
        "Diazepam": {"dl50": 720, "slope": 4.5, "cid": 3016},
        "Aspirina": {"dl50": 200, "slope": 6.5, "cid": 2244},
        "Malathion": {"dl50": 1000, "slope": 4, "cid": 4004},
        "Permetrina": {"dl50": 430, "slope": 6, "cid": 40326},
        "Fipronil": {"dl50": 97, "slope": 7, "cid": 73260},
        "Nicotina": {"dl50": 50, "slope": 8, "cid": 89594},
        "Cocaína": {"dl50": 95, "slope": 7.5, "cid": 446220},
        "Metanfetamina": {"dl50": 60, "slope": 7, "cid": 10836},
        "Heroína": {"dl50": 21, "slope": 9, "cid": 5462328}
    }

def calcular_letalidade(dose, dl50, slope):
    return 100 / (1 + exp(-slope * (dose - dl50) / dl50))

def avaliar_resultado(letalidade):
    if letalidade < 30:
        return "Rato vivo"
    elif 30 <= letalidade < 50:
        return "Rato levemente intoxicado"
    elif 50 <= letalidade < 70:
        return "Rato gravemente intoxicado"
    else:
        return "Rato morto"

def registrar_resultado(animal, substancia, dose, resultado):
    USADOS.add(int(animal))
    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as f:
        f.write(f"Teste: Rato {animal} | Substância: {substancia} | Dose: {dose} mg/kg | Resultado: {resultado}\n")
    with open(USADOS_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(list(USADOS), f)

def simular_teste(animal, substancia, dose):
    substancias = define_substances()
    if substancia not in substancias:
        return {"erro": "Substância não encontrada."}
    dados = substancias[substancia]
    letalidade = calcular_letalidade(dose, dados["dl50"], dados["slope"])
    resultado = avaliar_resultado(letalidade)
    registrar_resultado(animal, substancia, dose, resultado)
    return {
        "animal": animal,
        "substancia": substancia,
        "dose": dose,
        "Resultado": resultado,
        "cid": dados["cid"]
    }

@app.route("/")
def index():
    return render_template("index.html", usados=list(USADOS))

@app.route("/simular", methods=["GET"])
def simular():
    substancia = request.args.get("substancia")
    animal = request.args.get("animal")
    try:
        dose = float(request.args.get("dose"))
    except (TypeError, ValueError):
        return jsonify({"erro": "Dose inválida."}), 400
    resultado = simular_teste(animal, substancia, dose)
    return jsonify(resultado)

@app.route("/exportar", methods=["GET"])
def exportar():
    if os.path.exists(HISTORICO_ARQUIVO):
        return send_file(HISTORICO_ARQUIVO, as_attachment=True)
    return "Nenhum resultado registrado ainda."

@app.route("/limpar", methods=["GET"])
def limpar():
    if os.path.exists(HISTORICO_ARQUIVO):
        os.remove(HISTORICO_ARQUIVO)
    if os.path.exists(USADOS_ARQUIVO):
        os.remove(USADOS_ARQUIVO)
    USADOS.clear()
    return "Histórico apagado."

@app.route("/substancias", methods=["GET"])
def listar_substancias():
    return jsonify(list(define_substances().keys()))

if __name__ == "__main__":
    app.run(debug=True)