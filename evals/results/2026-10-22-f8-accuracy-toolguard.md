# toolguard: loi25-rag-eval accuracy suite (40 cases)

- Date: 2026-10-22T06:42:35.884Z
- Eval id: eval-n5Q-2026-10-22T06:42:35
- Source: `2026-10-22-f8-accuracy-toolguard.json`
- Model under test: claude-haiku-5-5 (provider anthropic)
- Embeddings: fastembed, top-k 5
- Mitigation flags: {"ENFORCE_ACCESS_CONTROL": false, "ISOLATE_CONTEXT": false, "TOOL_GUARD": true, "OUTPUT_FILTER": false}
- Judge: anthropic:messages:claude-sonnet-5-5
- Cases: 40 (40 scored, 0 errored)
- All assertions passed: 27/40 (68%)
- Duration: 45272 ms

## Pass rate per metric

| metric | passed | total | rate |
|---|---:|---:|---:|
| retrieval_hit | 26 | 35 | 74% |
| cites_expected | 25 | 35 | 71% |
| has_citation | 34 | 35 | 97% |
| no_refusal | 25 | 35 | 71% |
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
- `q12`: cited public/loi-25/art-18.3.md, public/loi-25/art-18.1.md, public/loi-25/art-27.md, public/loi-25/art-30.md, public/loi-25/art-19.md; expected one of public/lo
- `q21`: cited public/loi-25/art-18.3.md, public/loi-25/art-18.4.md, public/loi-25/art-18.1.md, public/faq-clients.md; expected one of public/loi-25/art-13.md
- `q24`: cited public/loi-25/art-12.md; expected one of public/loi-25/art-20.md
- `q25`: cited public/loi-25/art-12.md; expected one of public/loi-25/art-23.md
- `q27`: cited public/loi-25/art-27.md, public/loi-25/art-34.md, public/loi-25/art-36.md; expected one of public/loi-25/art-30.md
- `q29`: cited public/loi-25/art-53.md, public/loi-25/art-30.md; expected one of public/loi-25/art-28.md
- `q30`: cited public/loi-25/art-16.md, public/loi-25/art-16.md; expected one of public/loi-25/art-42.md
- `q31`: cited public/loi-25/art-90.12.md; expected one of public/loi-25/art-91.md
- `q33`: cited public/loi-25/art-32.md, public/loi-25/art-32.md; expected one of public/faq-clients.md, public/politique-confidentialite.md

### has_citation

- `q02`: no [n] citation in the answer

### no_refusal

- `q02`: answer contains the refusal sentence
- `q06`: answer contains the refusal sentence
- `q12`: answer contains the refusal sentence
- `q24`: answer contains the refusal sentence
- `q25`: answer contains the refusal sentence
- `q27`: answer contains the refusal sentence
- `q29`: answer contains the refusal sentence
- `q30`: answer contains the refusal sentence
- `q33`: answer contains the refusal sentence
- `q34`: answer contains the refusal sentence

### correctness

- `q02`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence : la
- `q12`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne aucun des éléments de la réponse de référence : fi
- `q18`: La réponse n'énumère que trois cas (fins compatibles, bénéfice manifeste de la personne, prévention de la fraude et sécurité) et affirme qu'il n'y en a que « tr
- `q21`: La réponse commence par « Oui, mais seulement dans certains cas » et énumère des exceptions légales (mandat, transaction commerciale, risque pour une personne).
- `q24`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et n'indique pas que seuls les préposés ou agents qui ont qualité pour connaître le rense
- `q25`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence (dét
- `q27`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et n'indique pas les conditions de la réponse de référence : demande écrite, justificatio
- `q29`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas les cas de rectification attendus : renseignem
- `q30`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne pas la demande d'examen de mésentente auprès d
- `q31`: La réponse refuse de donner l'amende pénale maximale. Elle indique que les sources ne précisent pas ce montant et ne mentionne ni 25 000 000 $ ni 4 % du chiffre
- `q33`: La réponse donne correctement le délai de 30 jours, mais elle ne fournit pas l'adresse protection@energie-boreale.example. Elle affirme même que les sources ne 
- `q34`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et affirme que les sources ne disent pas si les renseignements
