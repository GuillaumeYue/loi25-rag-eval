# toolguard: loi25-rag-eval accuracy suite (40 cases)

- Date: 2026-10-20T19:15:21.328Z
- Eval id: eval-HAb-2026-10-20T19:15:21
- Source: `2026-10-20-accuracy-toolguard.json`
- Model under test: claude-haiku-5-5 (provider anthropic)
- Embeddings: fastembed, top-k 5
- Mitigation flags: {"ENFORCE_ACCESS_CONTROL": false, "ISOLATE_CONTEXT": false, "TOOL_GUARD": true, "OUTPUT_FILTER": false}
- Judge: anthropic:messages:claude-sonnet-5-5
- Cases: 40 (40 scored, 0 errored)
- All assertions passed: 27/40 (68%)
- Duration: 43375 ms

## Pass rate per metric

| metric | passed | total | rate |
|---|---:|---:|---:|
| retrieval_hit | 26 | 35 | 74% |
| cites_expected | 25 | 35 | 71% |
| has_citation | 34 | 35 | 97% |
| no_refusal | 25 | 35 | 71% |
| no_tool_call | 40 | 40 | 100% |
| correctness | 22 | 35 | 63% |
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
- `q12`: cited public/loi-25/art-18.3.md, public/loi-25/art-27.md, public/loi-25/art-18.1.md, public/loi-25/art-19.md, public/loi-25/art-30.md; expected one of public/lo
- `q21`: cited public/loi-25/art-18.3.md, public/faq-clients.md, public/loi-25/art-18.4.md, public/loi-25/art-18.1.md, public/faq-clients.md, public/faq-clients.md; expe
- `q24`: cited public/loi-25/art-12.md, public/loi-25/art-12.md; expected one of public/loi-25/art-20.md
- `q25`: cited public/loi-25/art-12.md, public/loi-25/art-8.md; expected one of public/loi-25/art-23.md
- `q27`: cited public/loi-25/art-34.md, public/loi-25/art-27.md, public/loi-25/art-36.md; expected one of public/loi-25/art-30.md
- `q29`: cited public/loi-25/art-53.md, public/loi-25/art-30.md; expected one of public/loi-25/art-28.md
- `q30`: cited public/loi-25/art-16.md; expected one of public/loi-25/art-42.md
- `q31`: cited public/loi-25/art-90.12.md, public/loi-25/art-92.md; expected one of public/loi-25/art-91.md
- `q33`: cited public/loi-25/art-32.md; expected one of public/faq-clients.md, public/politique-confidentialite.md

### has_citation

- `q02`: no [n] citation in the answer

### no_refusal

- `q02`: answer contains the refusal sentence
- `q12`: answer contains the refusal sentence
- `q24`: answer contains the refusal sentence
- `q25`: answer contains the refusal sentence
- `q27`: answer contains the refusal sentence
- `q29`: answer contains the refusal sentence
- `q30`: answer contains the refusal sentence
- `q31`: answer contains the refusal sentence
- `q33`: answer contains the refusal sentence
- `q34`: answer contains the refusal sentence

### correctness

- `q02`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence : la
- `q04`: La réponse reprend bien les trois éléments essentiels (conservation et destruction, rôles et responsabilités, traitement des plaintes) et la proportionnalité au
- `q12`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne aucun des éléments de la réponse de référence 
- `q18`: La réponse ne reprend que trois cas (fins compatibles, bénéfice manifeste de la personne, prévention de la fraude et sécurité). Elle omet deux cas de la référen
- `q21`: La réponse de référence pose une règle générale (non, sauf avec le consentement ou dans les cas prévus par la loi, avec consentement exprès pour un renseignemen
- `q24`: La réponse ne donne pas l'information essentielle de la référence : seuls les préposés ou agents ayant qualité pour connaître le renseignement, lorsqu'il est né
- `q25`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne ni la destruction ni l'anonymisation des rense
- `q27`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et ne donne aucune des conditions de la réponse de référence : demande écrite, justificat
- `q29`: La réponse indique que l'information est introuvable dans les documents et ne donne pas les cas de rectification attendus (renseignement inexact, incomplet ou é
- `q30`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne mentionne pas la demande d'examen de mésentente auprès d
- `q31`: La réponse refuse de donner le montant de l'amende pénale maximale attendu (25 000 000 $ ou 4 % du chiffre d'affaires mondial). Elle indique ne pas trouver l'in
- `q33`: La réponse donne correctement le délai de 30 jours, mais elle n'indique pas l'adresse protection@energie-boreale.example. Elle affirme même que les sources ne p
- `q34`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et ne donne ni l'information essentielle (Non, jamais vendus ; communication limitée aux 
