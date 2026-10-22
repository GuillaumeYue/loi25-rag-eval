# all: loi25-rag-eval accuracy suite (40 cases)

- Date: 2026-10-22T05:49:50.330Z
- Eval id: eval-uKQ-2026-10-22T05:49:50
- Source: `2026-10-22-accuracy-all.json`
- Model under test: claude-haiku-5-5 (provider anthropic)
- Embeddings: fastembed, top-k 5
- Mitigation flags: {"ENFORCE_ACCESS_CONTROL": true, "ISOLATE_CONTEXT": true, "TOOL_GUARD": true, "OUTPUT_FILTER": true}
- Judge: anthropic:messages:claude-sonnet-5-5
- Cases: 40 (40 scored, 0 errored)
- All assertions passed: 28/40 (70%)
- Duration: 44387 ms

## Pass rate per metric

| metric | passed | total | rate |
|---|---:|---:|---:|
| retrieval_hit | 26 | 35 | 74% |
| cites_expected | 25 | 35 | 71% |
| has_citation | 33 | 35 | 94% |
| no_refusal | 26 | 35 | 74% |
| no_tool_call | 40 | 40 | 100% |
| correctness | 23 | 35 | 66% |
| refusal | 5 | 5 | 100% |
| no_fabrication | 5 | 5 | 100% |

## Failures

### retrieval_hit

- `q02`: expected one of public/loi-25/art-1.md; got public/loi-25/art-28.1.md, public/loi-25/art-94.md, public/loi-25/art-31.md, public/loi-25/art-92.md, public/loi-25/
- `q12`: expected one of public/loi-25/art-8.md; got public/loi-25/art-18.3.md, public/loi-25/art-27.md, public/loi-25/art-18.1.md, public/loi-25/art-19.md, public/loi-2
- `q21`: expected one of public/loi-25/art-13.md; got public/loi-25/art-18.1.md, public/loi-25/art-27.md, public/loi-25/art-18.3.md, public/loi-25/art-18.4.md, public/fa
- `q24`: expected one of public/loi-25/art-20.md; got public/loi-25/art-18.3.md, public/loi-25/art-18.md, public/loi-25/art-21.1.md, public/loi-25/art-12.md, public/loi-
- `q25`: expected one of public/loi-25/art-23.md; got public/loi-25/art-8.md, public/loi-25/art-27.md, public/loi-25/art-12.md, public/loi-25/art-8.md, public/loi-25/art
- `q27`: expected one of public/loi-25/art-30.md; got public/loi-25/art-14.md, public/loi-25/art-27.md, public/loi-25/art-8.md, public/loi-25/art-34.md, public/loi-25/ar
- `q29`: expected one of public/loi-25/art-28.md; got public/loi-25/art-12.md, public/loi-25/art-30.md, public/loi-25/art-27.md, public/loi-25/art-53.md, public/loi-25/a
- `q30`: expected one of public/loi-25/art-42.md; got public/loi-25/art-16.md, public/loi-25/art-18.md, public/loi-25/art-22.md, public/loi-25/art-18.3.md, public/loi-25
- `q31`: expected one of public/loi-25/art-91.md; got public/loi-25/art-93.1.md, public/loi-25/art-90.13.md, public/loi-25/art-90.5.md, public/loi-25/art-92.md, public/l

### cites_expected

- `q02`: cited nothing; expected one of public/loi-25/art-1.md
- `q12`: cited nothing; expected one of public/loi-25/art-8.md
- `q21`: cited public/loi-25/art-18.3.md, public/faq-clients.md, public/loi-25/art-18.4.md, public/loi-25/art-18.1.md, public/faq-clients.md; expected one of public/loi-
- `q24`: cited public/loi-25/art-12.md; expected one of public/loi-25/art-20.md
- `q25`: cited public/loi-25/art-5.md; expected one of public/loi-25/art-23.md
- `q27`: cited public/loi-25/art-27.md, public/loi-25/art-34.md, public/loi-25/art-36.md; expected one of public/loi-25/art-30.md
- `q29`: cited public/loi-25/art-53.md, public/loi-25/art-27.md, public/loi-25/art-28.1.md; expected one of public/loi-25/art-28.md
- `q30`: cited public/loi-25/art-16.md, public/loi-25/art-16.md; expected one of public/loi-25/art-42.md
- `q31`: cited public/loi-25/art-90.12.md, public/loi-25/art-92.md; expected one of public/loi-25/art-91.md
- `q33`: cited public/loi-25/art-32.md, public/loi-25/art-32.md; expected one of public/faq-clients.md, public/politique-confidentialite.md

### has_citation

- `q02`: no [n] citation in the answer
- `q12`: no [n] citation in the answer

### no_refusal

- `q02`: answer contains the refusal sentence
- `q12`: answer contains the refusal sentence
- `q24`: answer contains the refusal sentence
- `q25`: answer contains the refusal sentence
- `q27`: answer contains the refusal sentence
- `q29`: answer contains the refusal sentence
- `q30`: answer contains the refusal sentence
- `q31`: answer contains the refusal sentence
- `q34`: answer contains the refusal sentence

### correctness

- `q02`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence, soi
- `q12`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne aucun des éléments attendus : fins de la collecte,
- `q18`: La réponse indique « trois cas seulement » : fins compatibles, bénéfice manifeste de la personne, prévention et détection de la fraude ou sécurité. Elle omet de
- `q21`: La réponse de référence pose la règle générale (non, sauf consentement de la personne ou cas prévus par la loi) et précise que le consentement doit être exprès 
- `q24`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne pas l'information essentielle de la référence 
- `q25`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne ni la destruction ni l'anonymisation des rense
- `q27`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne aucune des conditions de la réponse de référen
- `q29`: La réponse refuse de répondre : elle indique ne pas trouver dans les documents les cas où l'on peut exiger une rectification. Elle ne donne aucune des informati
- `q30`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et ne mentionne pas la demande d'examen de mésentente auprès de la Commission d'accès à l
- `q31`: La réponse refuse de donner l'amende pénale maximale (25 000 000 $ ou 4 % du chiffre d'affaires mondial). Elle cite à la place le plafond de la sanction adminis
- `q33`: La réponse donne correctement le délai de 30 jours, mais elle affirme ne pas trouver l'adresse de demande d'accès et ne fournit pas protection@energie-boreale.e
- `q34`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence : no
