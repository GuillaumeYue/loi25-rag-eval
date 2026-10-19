# stub-null-baseline: loi25-rag-eval accuracy suite (40 cases)

- Date: 2026-10-19T06:40:05.133Z
- Eval id: eval-dH0-2026-10-19T06:40:05
- Source: `2026-10-19-accuracy-stub.json`
- Model under test: unknown (provider stub)
- Embeddings: fastembed, top-k 5
- Mitigation flags: {}
- Judge: anthropic:messages:claude-sonnet-5-5
- Cases: 40 (40 scored, 0 errored)
- All assertions passed: 0/40 (0%)
- Duration: 38086 ms

## Pass rate per metric

| metric | passed | total | rate |
|---|---:|---:|---:|
| retrieval_hit | 26 | 35 | 74% |
| cites_expected | 17 | 35 | 49% |
| has_citation | 35 | 35 | 100% |
| no_refusal | 35 | 35 | 100% |
| no_tool_call | 40 | 40 | 100% |
| correctness | 0 | 35 | 0% |
| refusal | 0 | 5 | 0% |
| no_fabrication | 0 | 5 | 0% |

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

- `q01`: cited public/loi-25/art-1.1.md; expected one of public/loi-25/art-2.md
- `q02`: cited public/loi-25/art-28.1.md; expected one of public/loi-25/art-1.md
- `q07`: cited public/loi-25/art-3.5.md; expected one of public/loi-25/art-3.6.md
- `q09`: cited public/loi-25/art-3.5.md; expected one of public/loi-25/art-3.7.md
- `q10`: cited public/loi-25/art-3.5.md; expected one of public/loi-25/art-3.8.md
- `q11`: cited public/loi-25/art-27.md; expected one of public/loi-25/art-4.md, public/loi-25/art-5.md
- `q12`: cited public/loi-25/art-18.3.md; expected one of public/loi-25/art-8.md
- `q19`: cited public/loi-25/art-18.4.md; expected one of public/loi-25/art-12.md
- `q21`: cited public/loi-25/art-18.1.md; expected one of public/loi-25/art-13.md
- `q22`: cited public/loi-25/art-8.md; expected one of public/loi-25/art-17.md
- `q24`: cited public/loi-25/art-18.3.md; expected one of public/loi-25/art-20.md
- `q25`: cited public/loi-25/art-8.md; expected one of public/loi-25/art-23.md
- `q27`: cited public/loi-25/art-14.md; expected one of public/loi-25/art-30.md
- `q29`: cited public/loi-25/art-12.md; expected one of public/loi-25/art-28.md
- `q30`: cited public/loi-25/art-16.md; expected one of public/loi-25/art-42.md
- `q31`: cited public/loi-25/art-93.1.md; expected one of public/loi-25/art-91.md
- `q33`: cited public/loi-25/art-32.md; expected one of public/faq-clients.md, public/politique-confidentialite.md
- `q34`: cited public/politique-confidentialite.md; expected one of public/faq-clients.md

### correctness

- `q01`: Le champ « answer » ne contient que « Réponse de démonstration fondée sur la source [1]. » Il ne donne aucune définition du renseignement personnel. L'informati
- `q02`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information substantielle. Elle ne dit pas que la loi ne s'applique pas a
- `q03`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information substantielle. Elle n'indique ni que la personne ayant la plu
- `q04`: La réponse est un texte de démonstration (« Réponse de démonstration fondée sur la source [1] ») qui ne contient aucune des informations de la réponse de référe
- `q05`: Le champ « answer » ne contient que « Réponse de démonstration fondée sur la source [1] », sans aucune information substantielle. Il ne mentionne ni les projets
- `q06`: La réponse est un texte de démonstration (« Réponse de démonstration fondée sur la source [1] ») qui ne donne aucune information sur les mesures de sécurité. El
- `q07`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne définit pas l'incident de confidentialité. Elle ne mentionne ni l'accès, l'utilisation ou
- `q08`: La réponse se limite à « Réponse de démonstration fondée sur la source [1] » et ne contient aucune information de fond. Elle ne mentionne ni l'obligation d'avis
- `q09`: La réponse se limite à « Réponse de démonstration fondée sur la source [1] » et ne donne aucun des facteurs attendus : la sensibilité du renseignement, les cons
- `q10`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne répond pas à la question. Elle ne dit pas qu'une entreprise doit tenir un registre des in
- `q11`: La réponse n'est qu'un texte générique (« Réponse de démonstration fondée sur la source [1] ») qui ne contient pas l'information essentielle attendue : détermin
- `q12`: La réponse est un texte générique (« Réponse de démonstration fondée sur la source [1] ») qui ne contient aucune des informations attendues : ni les fins de la 
- `q13`: Le champ « answer » indique seulement « Réponse de démonstration fondée sur la source [1]. » Il ne donne aucune information substantielle. Il ne mentionne ni l'
- `q14`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information substantielle. Elle ne dit pas qu'une politique de confidenti
- `q15`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information concrète. Elle ne mentionne ni le plus haut niveau de confide
- `q16`: Le champ « answer » contient uniquement « Réponse de démonstration fondée sur la source [1]. » Cette phrase ne donne aucune des qualités du consentement valide 
- `q17`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne donne aucune information concrète. Elle ne mentionne ni le titulaire de l'autorité parent
- `q18`: La réponse se limite à « Réponse de démonstration fondée sur la source [1] ». Elle ne contient aucune des exceptions de la référence : fin compatible, bénéfice 
- `q19`: La réponse n'est qu'un texte de démonstration (« Réponse de démonstration fondée sur la source [1] ») et ne dit rien sur la prospection commerciale. Elle ne con
- `q20`: La réponse se limite à « Réponse de démonstration fondée sur la source [1] ». Elle ne contient aucune des informations de la réponse de référence : ni l'obligat
- `q21`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucun contenu substantiel. Elle n'indique ni la règle générale (pas de communica
- `q22`: La réponse se limite à « Réponse de démonstration fondée sur la source [1] ». Elle ne mentionne ni l'évaluation des facteurs relatifs à la vie privée, ni l'ente
- `q23`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information de fond. Elle ne mentionne ni le contrat écrit, ni les mesure
- `q24`: La réponse (« Réponse de démonstration fondée sur la source [1] ») ne contient aucune information de fond. Elle ne mentionne pas que seuls les préposés ou agent
- `q25`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information de fond. Elle ne dit pas que les renseignements doivent être 
- `q26`: La réponse est un texte générique (« Réponse de démonstration fondée sur la source [1] ») qui ne donne aucun délai. Elle ne mentionne ni les 30 jours, ni la rép
- `q27`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information substantielle. Elle ne mentionne ni la demande écrite, ni la 
- `q28`: La réponse est un texte de démonstration générique (« Réponse de démonstration fondée sur la source [1] ») qui ne donne aucune des informations de référence : n
- `q29`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne donne aucun contenu substantiel. Elle ne mentionne ni le caractère inexact, incomplet ou 
- `q30`: La réponse ne contient que « Réponse de démonstration fondée sur la source [1] ». Elle ne mentionne ni la demande d'examen de mésentente ni la Commission d'accè
- `q31`: La réponse ne contient que « Réponse de démonstration fondée sur la source [1] » et ne donne aucun montant. Elle n'indique ni 25 000 000 $, ni 4 % du chiffre d'
- `q32`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne donne aucun montant. Elle n'indique ni les 50 000 $ pour une personne physique, ni les 10
- `q33`: La réponse est un texte de démonstration (« Réponse de démonstration fondée sur la source [1] ») qui ne donne ni l'adresse protection@energie-boreale.example ni
- `q34`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne répond pas à la question. Elle n'indique pas qu'Énergie Boréale ne vend jamais les rensei
- `q35`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») ne contient aucune information substantielle. Elle ne dit pas que les fonctions d'identifica

### refusal

- `u01`: no refusal sentence; answer starts: Réponse de démonstration fondée sur la source [1].
- `u02`: no refusal sentence; answer starts: Réponse de démonstration fondée sur la source [1].
- `u03`: no refusal sentence; answer starts: Réponse de démonstration fondée sur la source [1].
- `u04`: no refusal sentence; answer starts: Réponse de démonstration fondée sur la source [1].
- `u05`: no refusal sentence; answer starts: Réponse de démonstration fondée sur la source [1].

### no_fabrication

- `u01`: La réponse (« Réponse de démonstration fondée sur la source [1] ») n'indique pas que l'information est absente des documents. Elle prétend au contraire s'appuye
- `u02`: La réponse (« Réponse de démonstration fondée sur la source [1] ») n'indique pas que l'information est absente des documents. Elle prétend au contraire s'appuye
- `u03`: La réponse n'affirme aucun fait de fond, mais elle n'indique pas non plus que l'information est absente des documents. Elle se dit « fondée sur la source [1] »,
- `u04`: La réponse (« Réponse de démonstration fondée sur la source [1]. ») n'indique pas que l'information est absente des documents. Elle laisse entendre que la sourc
- `u05`: La réponse ne dit pas que l'information est indisponible dans les documents. Elle se présente comme « fondée sur la source [1] », ce qui laisse croire qu'une ré
