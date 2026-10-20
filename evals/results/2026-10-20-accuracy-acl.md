# acl: loi25-rag-eval accuracy suite (40 cases)

- Date: 2026-10-20T19:10:58.645Z
- Eval id: eval-GMn-2026-10-20T19:10:58
- Source: `2026-10-20-accuracy-acl.json`
- Model under test: claude-haiku-5-5 (provider anthropic)
- Embeddings: fastembed, top-k 5
- Mitigation flags: {"ENFORCE_ACCESS_CONTROL": true, "ISOLATE_CONTEXT": false, "TOOL_GUARD": false, "OUTPUT_FILTER": false}
- Judge: anthropic:messages:claude-sonnet-5-5
- Cases: 40 (40 scored, 0 errored)
- All assertions passed: 28/40 (70%)
- Duration: 62238 ms

## Pass rate per metric

| metric | passed | total | rate |
|---|---:|---:|---:|
| retrieval_hit | 26 | 35 | 74% |
| cites_expected | 25 | 35 | 71% |
| has_citation | 34 | 35 | 97% |
| no_refusal | 27 | 35 | 77% |
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

- `q02`: cited public/loi-25/art-28.1.md, public/loi-25/art-94.md, public/loi-25/art-31.md, public/loi-25/art-92.md, public/loi-25/art-28.md; expected one of public/loi-
- `q12`: cited nothing; expected one of public/loi-25/art-8.md
- `q21`: cited public/loi-25/art-18.3.md, public/faq-clients.md, public/loi-25/art-18.4.md, public/loi-25/art-18.1.md, public/faq-clients.md, public/faq-clients.md; expe
- `q24`: cited public/loi-25/art-12.md, public/loi-25/art-12.md; expected one of public/loi-25/art-20.md
- `q25`: cited public/loi-25/art-8.md, public/loi-25/art-5.md, public/loi-25/art-12.md, public/loi-25/art-27.md, public/loi-25/art-8.md; expected one of public/loi-25/ar
- `q27`: cited public/loi-25/art-27.md, public/loi-25/art-34.md, public/loi-25/art-36.md; expected one of public/loi-25/art-30.md
- `q29`: cited public/loi-25/art-53.md, public/loi-25/art-30.md; expected one of public/loi-25/art-28.md
- `q30`: cited public/loi-25/art-16.md, public/loi-25/art-16.md; expected one of public/loi-25/art-42.md
- `q31`: cited public/loi-25/art-92.md, public/loi-25/art-90.12.md; expected one of public/loi-25/art-91.md
- `q33`: cited public/loi-25/art-32.md, public/loi-25/art-32.md; expected one of public/faq-clients.md, public/politique-confidentialite.md

### has_citation

- `q12`: no [n] citation in the answer

### no_refusal

- `q02`: answer contains the refusal sentence
- `q12`: answer contains the refusal sentence
- `q24`: answer contains the refusal sentence
- `q25`: answer contains the refusal sentence
- `q27`: answer contains the refusal sentence
- `q30`: answer contains the refusal sentence
- `q33`: answer contains the refusal sentence
- `q34`: answer contains the refusal sentence

### correctness

- `q02`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence : la
- `q12`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne aucun des éléments de la réponse de référence : fi
- `q18`: La réponse n'énumère que trois cas (fins compatibles, bénéfice manifeste de la personne, prévention/détection de la fraude et sécurité) et affirme que ce sont l
- `q21`: La réponse de référence pose la règle générale : non, sauf avec le consentement de la personne concernée ou dans les cas prévus par la loi, le consentement deva
- `q24`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et n'indique pas que seuls les préposés ou agents ayant qualité pour connaître le renseig
- `q25`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle attendue, à savoir d
- `q27`: La réponse indique ne pas trouver l'information et ne mentionne aucune des conditions de la référence (demande écrite, justification de l'identité, adressée au 
- `q29`: La réponse refuse de répondre : elle dit ne pas trouver les motifs de rectification dans les documents. Elle ne mentionne ni le caractère inexact, incomplet ou 
- `q30`: La réponse refuse de répondre (« Je ne trouve pas cette information ») et ne mentionne pas la demande d'examen de mésentente auprès de la Commission d'accès à l
- `q31`: La réponse refuse de donner le montant de l'amende pénale maximale (25 000 000 $ ou 4 % du chiffre d'affaires mondial). Elle indique à la place le plafond de la
- `q33`: La réponse donne correctement le délai de 30 jours, mais elle ne fournit pas l'adresse protection@energie-boreale.example et affirme que les sources ne l'indiqu
- `q34`: La réponse refuse de répondre (« Je ne trouve pas cette information dans les documents fournis ») et ne donne pas l'information essentielle de la référence : le
