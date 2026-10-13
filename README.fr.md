# Accélérateur Fabric SRE

Solution réutilisable pour historiser l’administration Microsoft Fabric,
alimenter deux rapports Power BI PBIP/TMDL et enrichir un agent `fabricsre`
avec analyse, détection d’anomalies et actions soumises à approbation.

## Contenu

- `config/` : paramètres client sans identifiant codé en dur;
- `notebooks/` et `pipelines/` : collecte quotidienne vers Delta;
- `src/fabric_sre/` : clients REST, reprise sur 429 et garde d’approbation;
- `agent/` : instructions FR/EN, sous-agents et routines;
- `powerbi/FabricSRE/` : modèle TMDL partagé et rapports FR/EN distincts;
- `docs/` : architecture, permissions, déploiement, personnalisation et tests.

## Démarrage progressif

Commencer sans choisir immédiatement une édition :

1. **Découverte** : créer Azure SRE Agent dans le portail, connecter Fabric Core
   MCP, puis poser des questions et générer des visuels à la demande;
2. **Basic** : ajouter l'inventaire tenant Fabric Admin, le Live Report bilingue
   et, en option, les CU récentes, sans workspace Fabric technique;
3. **Advanced** : ajouter le workspace `Fabric Administration`, le Lakehouse,
   l'historique d'au moins 60 jours, le modèle sémantique et les rapports Power
   BI.

Lire le [guide de déploiement](docs/deployment.fr.md) avant l'installation.
Pour une procédure détaillée adaptée à un public non technique, suivre le
[guide de déploiement pas à pas](docs/deployment-pas-a-pas.fr.md).
Le [catalogue de prompts](docs/prompts.fr.md) permet de commencer à explorer
Fabric dès que le premier connecteur est opérationnel.
La [spécification du Live Report](docs/live-report.fr.md) décrit la version
fonctionnelle à publier, sa recette et son comportement lorsqu'une capacité est
arrêtée.

1. Créer l'agent dans <https://sre.azure.com>.
2. Ajouter le connecteur Fabric dans **Builder > Connectors**.
3. Tester les prompts de découverte.
4. Pour installer Basic ou Advanced, copier
   `config/client.parameters.example.yaml` vers
   `config/client.parameters.yaml`, puis remplir les valeurs client.
5. Définir `AZURE_TENANT_ID` et `AZURE_SUBSCRIPTION_ID`.
6. Exécuter `scripts/validate.ps1`.
7. Lire `docs/solution.fr.md`.
8. Pour Advanced seulement, lancer `scripts/deploy.ps1 -WhatIf`.
9. Ouvrir `powerbi/FabricSRE/fr/FabricSRE-fr.pbip` pour la version française.

Le script de prévol échoue explicitement si le compte actif ne voit pas
l’abonnement cible, afin d’éviter un déploiement dans le mauvais environnement.
