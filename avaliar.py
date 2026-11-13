import time

from buscar import buscar, carregar_indice

K = 3

# (pergunta, arquivos aceitos como corretos)
PERGUNTAS = [
    ("O que é password spraying?", {"forca_bruta.txt"}),
    ("Como me proteger de senhas vazadas reutilizadas?", {"forca_bruta.txt"}),
    ("O que é smishing?", {"phishing.txt"}),
    ("Quais sinais mostram que um e-mail é falso?", {"phishing.txt"}),
    ("O que significa correlação de eventos?", {"siem.txt"}),
    ("Por que falsos positivos são um problema?", {"siem.txt"}),
    ("Qual evento do Windows indica falha de logon?", {"logs_autenticacao.txt"}),
    ("Por que os relógios dos sistemas precisam estar sincronizados?", {"logs_autenticacao.txt"}),
    ("Alguém tentou entrar muitas vezes na minha conta", {"forca_bruta.txt", "logs_autenticacao.txt"}),
    ("Como a empresa junta os registros de vários sistemas?", {"siem.txt"}),
]

FORA_DO_ESCOPO = [
    "Qual é a capital da França?",
    "O que é ransomware?",
    "Como fazer um bolo de cenoura?",
]


def main():
    indice = carregar_indice()

    acertos = 0
    for pergunta, esperados in PERGUNTAS:
        resultados = buscar(pergunta, indice, k=K)
        arquivos = [r["arquivo"] for r, _ in resultados]
        acertou = any(a in esperados for a in arquivos)
        acertos += acertou
        marca = "OK  " if acertou else "FALHA"
        print(f"[{marca}] {pergunta}\n        top-{K}: {arquivos}")
        time.sleep(0.5)  # evita estourar o limite da API

    print(f"\nTaxa de acerto no top-{K}: {acertos}/{len(PERGUNTAS)} = {acertos / len(PERGUNTAS):.0%}")

    print("\nMelhor similaridade em perguntas FORA do escopo (use para calibrar o limite):")
    for pergunta in FORA_DO_ESCOPO:
        melhor = buscar(pergunta, indice, k=1)[0][1]
        print(f"  {melhor:.3f}  {pergunta}")
        time.sleep(0.5)


if __name__ == "__main__":
    main()