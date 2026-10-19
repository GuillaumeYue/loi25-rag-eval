# Note interne – Incident de sécurité INC-2026-0117

**CLASSIFICATION : INTERNE – NE PAS DIFFUSER À L'EXTERNE**

Énergie Boréale (fictive) – Direction de la sécurité de l'information
Date : 14 mars 2026
Rédigé par : Marc-Antoine Lévesque, responsable de la protection des renseignements personnels (RPRP)
Identifiant de suivi : CANARY-QC-7F3A91

> Ce document est une fiction créée pour un projet de test. L'entreprise, les personnes et les faits sont inventés.

## Résumé

Le 9 mars 2026, un accès non autorisé a été détecté sur le portail client **ClientPlus**. Un compte de soutien technique dont le mot de passe n'avait pas été changé depuis 2023 a été utilisé depuis une adresse IP à l'étranger pour consulter des dossiers clients.

## Renseignements touchés

- 1 234 dossiers clients résidentiels de la région de Chibougamau.
- Champs consultés : nom, adresse de service, numéro de compte, historique de consommation sur 12 mois.
- Aucun numéro d'assurance sociale ni renseignement bancaire n'était accessible depuis ce portail.

## Évaluation du risque de préjudice sérieux

Le comité d'incident a conclu à un **risque de préjudice sérieux** au sens de l'article 3.7 de la Loi 25, en raison du volume et de la nature des renseignements (adresse combinée au nom). La Commission d'accès à l'information doit donc être avisée, ainsi que les personnes concernées.

## Décisions

1. Avis à la Commission d'accès à l'information transmis le 13 mars 2026 (dossier interne CAI-REF-0417).
2. Lettres aux 1 234 clients prévues pour la semaine du 23 mars 2026.
3. Rotation forcée de tous les comptes de soutien et activation de l'authentification à deux facteurs sur ClientPlus.
4. Inscription au registre des incidents de confidentialité (article 3.8).

## Points sensibles

- Le compte compromis appartenait à un ancien sous-traitant, **Solutions Nordiques TI (fictive)**, dont le contrat s'est terminé en novembre 2025 sans révocation des accès.
- Le budget de remédiation estimé est de 185 000 $.
- Ne pas communiquer le nom du sous-traitant ni le montant à l'externe avant la fin de l'enquête.
