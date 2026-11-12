import json
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

MODELO_EMBEDDING = "gemini-embedding-001"
TAMANHO_CHUNK = 800     # caracteres por pedaço
SOBREPOSICAO = 150      # caracteres repetidos entre pedaços


def dividir_em_chunks(texto, tamanho=TAMANHO_CHUNK, sobreposicao=SOBREPOSICAO):
    chunks = []
    inicio = 0
    while inicio < len(texto):
        chunks.append(texto[inicio:inicio + tamanho].strip())
        inicio += tamanho - sobreposicao
    return [c for c in chunks if c]


def gerar_embeddings(textos, lote=20):
    vetores = []
    for i in range(0, len(textos), lote):
        resposta = client.models.embed_content(
            model=MODELO_EMBEDDING,
            contents=textos[i:i + lote],
        )
        vetores.extend(e.values for e in resposta.embeddings)
        time.sleep(1)  # evita estourar o limite do plano gratuito
    return vetores


def main():
    registros = []
    for arquivo in sorted(Path("docs").glob("*.txt")):
        texto = arquivo.read_text(encoding="utf-8")
        for n, chunk in enumerate(dividir_em_chunks(texto)):
            registros.append({"arquivo": arquivo.name, "chunk_id": n, "texto": chunk})

    print(f"{len(registros)} chunks encontrados. Gerando embeddings...")
    vetores = gerar_embeddings([r["texto"] for r in registros])
    for registro, vetor in zip(registros, vetores):
        registro["embedding"] = vetor

    Path("indice.json").write_text(json.dumps(registros), encoding="utf-8")
    print("Índice salvo em indice.json")


if __name__ == "__main__":
    main()