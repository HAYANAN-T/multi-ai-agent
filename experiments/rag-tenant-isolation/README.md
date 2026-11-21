# A data-leak-shaped mistake in AI retrieval

Reproducible, synthetic-data benchmark for the article **The Most Dangerous Part of an AI Assistant Might Be Its Search Results**.

**Scope:** Eight fictional teaching businesses × 96 similar fee records (768 records). 768 query cases, TF-IDF cosine ranking, three permission-check placements and a deliberately unsafe client-claimed tenant scenario. **No real user data, no language model, and no external service calls.** The answer renderer takes the first search hit; it does not simulate actual chatbot reasoning.

## Run

~~~bash
python -m pip install -r requirements.txt
python benchmark.py
python plot.py
~~~

The benchmark writes results.json, and plot.py generates three PNG charts locally (images are deliberately not checked into this code repository).

## Confirmed top-five results

| Measurement | Results |
|---|---:|
| Wrong-tenant first result, unrestricted global ranking | 672/768 (87.5%) |
| Foreign record present anywhere in global top five | 768/768 |
| Target found after global top five, then permission filtering | 480/768 (62.5%) |
| Target found after restricting tenant before ranking | 768/768 (100%) |
| Foreign record returned when trusting client-claimed tenant | 768/768 |
| Foreign record returned when using trusted simulated caller tenant | 0/768 |

These percentages are a **property of the purpose-built equal-overlap dataset**, not observed rates of real chatbot vulnerabilities. A change in corpus or query distribution can change the percentages. The study does not test prompt injection, neural embeddings or LLM-generated answers.

The core engineering insight is about placement and provenance of authorization: scope candidates to records the caller may see *before ranking*, and derive that scope from a server-validated identity rather than a client-supplied field.

Security background: OWASP RAG Security Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html
