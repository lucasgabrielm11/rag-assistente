import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from buscar import buscar, carregar_indice

load_dotenv()
client = genai.Client()

MODELO_GERACAO = "gemini-3.8-flash"  # troque se o nome mudar
K = 3
LIMITE_SIMILARIDADE = 0.0  # 0.0 = desligado; calibre com o avaliar.py (veja abaixo)

INSTRUCAO = (
    "Você é um assistente que responde perguntas usando SOMENTE os trechos fornecidos. "
    "Regras: "
    "(1) Se a resposta não estiver nos trechos, responda exatamente: "
    "'Não encontrei essa informação nos documentos.' "
    "(2) Cite os trechos usados no formato [1], [2]. "
    "(3) Responda em português, em até 4 frases."
)


def montar_contexto(resultados):
    partes = []
    for i, (registro, _score) in enumerate(resultados, start=1):
        partes.append(f"Trecho {i} (arquivo: {registro['arquivo']}):\n{registro['texto']}")
    return "\n\n".join(partes)


def chamar_modelo(prompt, tentativas=5):
    for i in range(tentativas):
        try:
            return client.models.generate_content(
                model=MODELO_GERACAO,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=INSTRUCAO,
                    temperature=0.1,  # baixa: queremos fidelidade, não criatividade
                ),
            )
        except (errors.ServerError, errors.ClientError) as e:
            temporario = isinstance(e, errors.ServerError) or getattr(e, "code", None) == 429
            if not temporario or i == tentativas - 1:
                raise
            espera = 2 ** i  # 1s, 2s, 4s, 8s...
            print(f"Erro temporário da API. Nova tentativa em {espera}s...")
            time.sleep(espera)


def responder(pergunta, indice):
    resultados = buscar(pergunta, indice, k=K)

    # as fontes vêm dos metadados dos chunks, não do texto do modelo
    fontes = [
        {"arquivo": r["arquivo"], "chunk_id": r["chunk_id"], "similaridade": round(s, 3)}
        for r, s in resultados
    ]

    if resultados[0][1] < LIMITE_SIMILARIDADE:
        return "Não encontrei essa informação nos documentos.", []

    prompt = f"{montar_contexto(resultados)}\n\nPergunta: {pergunta}"
    resposta = chamar_modelo(prompt)
    return resposta.text, fontes


if __name__ == "__main__":
    pergunta = " ".join(sys.argv[1:])
    if not pergunta:
        sys.exit('Uso: python rag.py "sua pergunta"')

    indice = carregar_indice()
    texto, fontes = responder(pergunta, indice)

    print("\nResposta:\n" + texto)
    print("\nFontes:")
    for f in fontes:
        print(f"  - {f['arquivo']} (chunk {f['chunk_id']}, similaridade {f['similaridade']})")