# Assistente RAG sobre documentos

Assistente que responde perguntas usando **somente** o conteúdo de documentos próprios e mostra de onde veio cada informação. Projeto de estudo de RAG (*Retrieval-Augmented Generation*) em Python com a API do Gemini.

## Como funciona

```
PREPARAÇÃO (ingestao.py)
docs/*.txt → chunks → embeddings → indice.json

CONSULTA (rag.py)
pergunta → embedding → similaridade com os chunks → top-3 → prompt com os trechos → resposta + fontes
```

1. **Ingestão:** os documentos são divididos em chunks (800 caracteres, com 150 de sobreposição) e cada chunk vira um embedding.
2. **Busca:** a pergunta é convertida em embedding e comparada com todos os chunks por similaridade de cosseno, e os 3 mais parecidos são recuperados.
3. **Geração:** os trechos entram no prompt, com instrução para responder só com base neles, citar os trechos usados e dizer que não sabe quando a resposta não está lá. A temperatura é baixa (0.1) para manter a resposta fiel.
4. **Fontes:** a lista de fontes vem dos metadados dos chunks recuperados, não do texto do modelo, então a origem exibida é sempre verdadeira.

## Estrutura

```
rag-assistente/
├── docs/               # documentos (.txt) sobre cibersegurança
├── ingestao.py         # chunking + embeddings → indice.json
├── buscar.py           # busca por similaridade (top-k)
├── rag.py              # prompt, geração, retry e fontes
├── avaliar.py          # avaliação da recuperação
├── requirements.txt
└── README.md
```

## Como rodar

Requisitos: Python 3.9+ e uma chave de API do [Google AI Studio](https://aistudio.google.com).

```bash
git clone https://github.com/lucasgabrielm11/rag-assistente.git
cd rag-assistente

python -m venv .venv
source .venv/Scripts/activate      # Git Bash
# .venv\Scripts\Activate.ps1       # PowerShell

pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz:

```
GEMINI_API_KEY=sua-chave-aqui
```

Gere o índice e faça perguntas:

```bash
python ingestao.py
python rag.py "O que é password spraying?"
python avaliar.py
```

O `.env` e o `indice.json` estão no `.gitignore`. O índice é gerado localmente pelo `ingestao.py`.

## Aprendizados

- **Teste também o teste.** A primeira avaliação deu 0%, mas a busca estava certa: os arquivos tinham sido salvos com extensão dupla (`.txt.txt`) e a comparação de nomes nunca batia. O erro estava na avaliação, não no sistema.
- Nomes de modelos mudam e podem deixar de estar disponíveis, por isso ficam em constantes no topo dos arquivos.
- A API pode falhar temporariamente (erros 503 e 429). O `rag.py` repete a chamada com espera crescente (1s, 2s, 4s...).
- Recuperação e geração são etapas distintas, e cada uma precisa ser avaliada separadamente.

## Limitações

- Base pequena (4 documentos), então as conclusões da avaliação são limitadas.
- Chunking por número de caracteres, que pode cortar frases no meio.
- A busca compara a pergunta com todos os chunks, o que funciona para uma base pequena mas não escala.
- A qualidade das respostas geradas foi avaliada manualmente, sem métrica automática.
- Apenas a etapa de geração tem tratamento de erros da API (a ingestão não).

## Próximos passos

- [ ] Dividir os documentos por parágrafo ou frase
- [ ] Usar um banco vetorial (Chroma ou FAISS)
- [ ] Avaliar também a qualidade da resposta final
- [ ] Interface com FastAPI

## Tecnologias

Python · Gemini API (`google-genai`) · NumPy · python-dotenv

---