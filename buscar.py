import json
import sys

import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

MODELO_EMBEDDING = "gemini-embedding-001"


def carregar_indice(caminho="indice.json"):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def buscar(pergunta, indice, k=3):
    resposta = client.models.embed_content(model=MODELO_EMBEDDING, contents=pergunta)
    q = np.array(resposta.embeddings[0].values)

    matriz = np.array([r["embedding"] for r in indice])
    scores = matriz @ q / (np.linalg.norm(matriz, axis=1) * np.linalg.norm(q))

    melhores = np.argsort(scores)[::-1][:k]
    return [(indice[i], float(scores[i])) for i in melhores]


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:])
    if not pergunta:
        sys.exit('Uso: python buscar.py "sua pergunta"')

    indice = carregar_indice()
    for registro, score in buscar(pergunta, indice):
        print(f"\n[{registro['arquivo']} | chunk {registro['chunk_id']} | similaridade {score:.3f}]")
        print(registro["texto"][:300] + "...")