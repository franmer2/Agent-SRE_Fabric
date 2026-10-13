# Guide de déploiement Fabric SRE

Ce guide suit un parcours progressif. L'utilisateur peut d'abord créer Azure
SRE Agent, connecter Fabric et explorer son environnement par conversation,
puis installer Basic ou Advanced sans recréer l'agent.

Pour une installation guidée destinée à une personne qui ne connaît pas
l'environnement, utiliser le
[guide de déploiement pas à pas](deployment-pas-a-pas.fr.md).

## 1. Choisir le niveau de progression

| Capacité | Découverte | Basic | Advanced |
|---|---:|---:|---:|
| Azure SRE Agent connecté à Fabric Core | Oui | Oui | Oui |
| Questions et visuels générés à la demande | Oui | Oui | Oui |
| Inventaire tenant Fabric Admin | Non | Oui | Oui |
| Live Report bilingue persistant | Non | Oui | Oui |
| CU récentes depuis Fabric Capacity Metrics | Selon le connecteur | Optionnel | Oui |
| Workspace technique `Fabric Administration` | Non | Non | Oui |
| Lakehouse, notebooks et pipeline quotidien | Non | Non | Oui |
| Historique garanti d'au moins 60 jours | Non | Non | Oui |
| Modèle TMDL et rapports Power BI PBIP FR/EN | Non | Non | Oui |

### Découverte

Le niveau Découverte est le point de départ recommandé pour un nouvel
utilisateur :

1. créer l'agent dans <https://sre.azure.com>;
2. connecter Fabric Core MCP dans **Builder > Connectors**;
3. sélectionner les outils de lecture nécessaires;
4. tester la connexion dans une nouvelle conversation;
5. utiliser le [catalogue de prompts](prompts.fr.md).

Ce niveau permet d'obtenir des réponses et des visuels dynamiques à partir des
ressources visibles par l'identité. Il ne fournit ni inventaire tenant garanti,
ni Live Report persistant, ni historique durable.

### Basic

L'édition Basic convient pour un démarrage rapide, une démonstration ou un
tenant qui veut d'abord valider l'inventaire et l'agent. Elle utilise :

- Fabric Core MCP pour les opérations temps réel autorisées à l'identité;
- Fabric Admin MCP pour l'inventaire tenant en lecture seule;
- le Live Report intégré à Azure SRE;
- facultativement, le modèle `Fabric Capacity Metrics` pour les CU récentes.

Elle **ne requiert pas** le workspace `Fabric Administration`. Sans source CU,
l'inventaire reste utilisable et les valeurs CU sont indiquées comme
indisponibles. Avec Capacity Metrics, la fenêtre Compute disponible est
normalement d'environ 14 jours; demander 30 ou 60 jours ne recrée pas les
données déjà expirées.

Une partie de la configuration Basic peut être pilotée en langage naturel
depuis un client compatible avec Azure MCP Server : création ou mise à jour du
connecteur Azure SRE Agent et enregistrement de prompts communs. Cette
alternative ne fonctionne pas comme une commande magique dans le chat de
l'agent et ne déploie pas le service Fabric Admin MCP. L'endpoint doit exister,
les droits Azure doivent être présents et les secrets doivent rester dans un
mécanisme sécurisé.

### Advanced

L'édition Advanced ajoute un workspace Fabric technique dédié, par défaut
`Fabric Administration`. Il héberge :

- le Lakehouse `FabricSRE`;
- les fichiers du collecteur, notebooks et pipeline quotidien;
- les tables Delta Bronze, Silver et Gold;
- le modèle sémantique `Fabric SRE`;
- les rapports Power BI PBIP/TMDL français et anglais;
- l'identité de workspace et les connexions requises par les actualisations.

Cette édition est requise pour garantir au moins 60 jours d'historique, calculer
des tendances durables et exploiter les rapports Power BI versionnés.

## 2. Architecture des dépendances

```text
Découverte
Azure SRE Agent
  └─ Fabric Core MCP
       └─ Questions et visuels à la demande

Basic
Découverte
  ├─ Fabric Core MCP
  ├─ Fabric Admin MCP (Container App)
  ├─ Live Report FR/EN
  └─ Capacity Metrics (optionnel, rétention native)

Advanced
Basic
  └─ Workspace Fabric Administration
       ├─ Lakehouse FabricSRE
       ├─ Notebooks + pipeline quotidien
       ├─ Tables Bronze / Silver / Gold
       ├─ Modèle sémantique TMDL
       └─ Rapports Power BI FR et EN
```

La suppression du workspace Advanced n'empêche pas l'inventaire Basic de
fonctionner, mais interrompt la collecte, l'historique, le modèle sémantique et
les rapports Power BI qu'il contient.

Les visuels générés dans une conversation ne remplacent pas le Live Report de
Basic ou les rapports Power BI d'Advanced : leur mise en page et leurs filtres
ne sont pas garantis entre deux sessions.

## 3. Prérequis

### Découverte

- un abonnement Azure actif;
- Owner, ou Contributor avec User Access Administrator, pour créer l'agent;
- accès réseau à `*.azuresre.ai`;
- un endpoint Fabric MCP approuvé et son mode d'authentification;
- des droits de lecture sur les ressources Fabric à observer.

La ligne de commande, le dépôt local et l'infrastructure Fabric Admin MCP ne
sont pas requis pour rester au niveau Découverte.

### Basic et Advanced

### Accès administrateur

- un compte Fabric Administrator pour l'amorçage;
- accès Owner ou User Access Administrator sur les ressources Azure à créer;
- accès à l'abonnement, au groupe de ressources et à l'agent Azure SRE cible;
- Azure CLI authentifié dans le bon tenant;
- PowerShell 7, Python, Node.js et les dépendances du dépôt.

### Paramètres tenant Fabric

Dans le portail d'administration Fabric, limiter chaque paramètre au groupe de
sécurité dédié aux identités SRE :

1. activer **Service principals can use Fabric APIs**;
2. activer l'accès des principaux de service aux **read-only admin APIs**;
3. activer les métadonnées détaillées du scanner seulement si elles sont
   nécessaires;
4. ne pas activer les API d'administration de mise à jour pour l'identité de
   lecture.

L'identité d'action, si elle est déployée, doit rester distincte et toute action
doit conserver l'approbation humaine.

### Fichier client

```powershell
Copy-Item config\client.parameters.example.yaml `
  config\client.parameters.yaml
```

Renseigner au minimum :

- `client`, `azure.tenantId` et `azure.subscriptionIds`;
- `foundry.subscriptionId`, `resourceGroup` et `agentName`;
- toute la section `foundry.fabricAdminMcp`;
- `fabric.capacityScope`;
- `fabric.capacityMetrics.semanticModelId` si les CU récentes sont activées.

Ne jamais committer le fichier client s'il contient des valeurs sensibles.
Les secrets restent dans Container Apps, Key Vault ou le mécanisme de secrets
du pipeline.

### Validation locale

```powershell
.\scripts\validate.ps1
```

Cette commande exécute les tests, Ruff, régénère les rapports PBIP et valide les
deux définitions de rapport. Elle nécessite les CLI Power BI d'auteur même pour
une installation Basic. Si seuls les services Basic sont déployés, cette
validation complète demeure recommandée pour certifier le paquet.

Vérifier ensuite que le compte actif voit la bonne ressource :

```powershell
.\scripts\preflight-agent.ps1 `
  -SubscriptionId "<subscription-agent>" `
  -ResourceGroup "<resource-group>" `
  -AgentName "<agent-name>" `
  -ExpectedAccount "<admin@tenant>"
```

## 4. Installation Basic

### Étape 1 — Préparer les identités

1. Créer ou réutiliser le groupe de sécurité autorisé aux API admin en lecture.
2. Vérifier que l'identité managée de l'agent peut utiliser Fabric Core MCP.
3. Laisser le lecteur Fabric Admin sans rôle Contributor sur les workspaces.
   L'inventaire tenant repose sur les paramètres tenant, pas sur une affectation
   Viewer à chaque workspace.

### Étape 2 — Déployer Fabric Admin MCP

```powershell
.\scripts\deploy-fabric-admin-mcp.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml
```

Le script :

- crée ou réutilise l'application et le principal de service lecteur;
- ajoute ce principal au groupe autorisé aux API admin;
- crée/réutilise Container Apps, ACR et l'identité managée configurés;
- conserve les secrets dans Container Apps;
- déploie le service MCP avec au moins une réplique;
- configure l'identifiant du modèle Capacity Metrics lorsqu'il est fourni.

Il ne doit afficher ni écrire les secrets dans Git.

### Étape 3 — Configurer le connecteur de l'agent

Créer ou mettre à jour le connecteur Azure SRE `FabricAdmin` :

- type : MCP, Streamable HTTP;
- endpoint : URL `/mcp` de la Container App;
- authentification : en-tête personnalisé `x-api-key`;
- outils sélectionnés :
  - `list_workspaces`;
  - `list_items`;
  - `get_cu_metrics` si Capacity Metrics est configuré;
- outils visibles :
  - `FabricAdmin_list_workspaces`;
  - `FabricAdmin_list_items`;
  - `FabricAdmin_get_cu_metrics`.

Conserver le connecteur `FabricSRE` vers Fabric Core MCP pour les opérations
temps réel limitées aux workspaces visibles par l'identité.

### Étape 4 — Publier la configuration et le Live Report

Publier `agent/azure-sre-agent.yaml` sur `meta_agent`, puis publier le Live
Report bilingue. Vérifier qu'il n'existe aucun outil en double et que le rapport
peut appeler les trois outils Fabric Admin et l'outil FabricSRE d'inventaire des
capacités.

Utiliser l'actif approuvé le plus récent et exécuter la recette de la
[spécification du Live Report](live-report.fr.md). La référence validée dans
l'environnement de développement est la version de service 39, mais un import
dans un autre environnement peut recevoir un autre numéro : les fonctions et
les contrôles de recette font foi.

### Étape 5 — Vérifier Basic

- `/health` retourne `status: ok`;
- le mainteneur de cache est actif;
- l'inventaire retourne les workspaces non personnels attendus;
- les totaux CU capacité, workspace et item se réconcilient lorsqu'ils sont
  disponibles;
- le toggle FR/EN traduit l'interface sans perdre les filtres;
- aucune action d'écriture n'est exposée sans approbation.

Pour Advanced, privilégier une petite capacité Fabric dédiée au workspace
d'administration SRE. L'arrêt d'une capacité de production ne doit pas arrêter
simultanément le Lakehouse, les notebooks et le pipeline de supervision. Voir
[Capacité Fabric arrêtée](live-report.fr.md#5-capacité-fabric-arrêtée).

## 5. Installation Advanced

Installer Basic en premier, puis exécuter les étapes suivantes.

### Étape 1 — Prévisualiser le workspace

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -WhatIf
```

Puis créer ou réutiliser le workspace et le Lakehouse :

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -CreateWorkspace
```

**Limite importante :** ce script crée ou résout le workspace et le Lakehouse,
puis affiche un plan. Il ne téléverse pas encore tous les fichiers, ne crée pas
les notebooks/pipelines et ne publie pas automatiquement le modèle et les
rapports.

### Étape 2 — Configurer le workspace

1. Affecter le workspace à une capacité Fabric appropriée.
2. Activer son identité de workspace.
3. Donner Contributor à l'identité de collecte ou d'automatisation.
4. Donner uniquement les droits de lecture/Build nécessaires aux identités de
   consommation.
5. Éviter Contributor pour l'identité de lecture de l'agent.

### Étape 3 — Déployer les actifs de collecte

Téléverser sous `Files/fabric-sre/` :

- `config/client.parameters.yaml`;
- `src/fabric_sre/`;
- `notebooks/`;
- `queries/`.

Créer les notebooks à partir des fichiers versionnés et créer le pipeline
quotidien à partir de `pipelines/daily-collection.pipeline.template.json`.

Exécuter dans cet ordre :

1. amorçage des tables;
2. collecte des inventaires et événements;
3. collecte Capacity Metrics;
4. construction Silver/Gold;
5. contrôles de qualité.

Vérifier que les colonnes issues de DAX sont normalisées avant l'écriture Delta
et que les tables Gold contiennent des identifiants et CU non nuls.

### Étape 4 — Déployer Power BI

1. Configurer les paramètres Server et Database du modèle TMDL.
2. Publier le modèle `Fabric SRE`.
3. Créer une connexion SQL cloud `WorkspaceIdentity`.
4. Lier le modèle à cette connexion.
5. Déclencher et vérifier une actualisation.
6. Publier les rapports PBIP français et anglais.
7. Certifier les artefacts selon les règles du client.

### Étape 5 — Planifier et surveiller

- planifier le pipeline au moins une fois par jour;
- conserver au minimum 60 jours, 400 par défaut;
- alerter si la fraîcheur dépasse le SLO configuré;
- respecter `Retry-After` sur les réponses 429;
- vérifier le statut du pipeline, les lignes collectées et les erreurs.

### Étape 6 — Vérifier Advanced

En plus des contrôles Basic :

- une collecte complète réussit;
- Bronze, Silver et Gold contiennent la date courante;
- `gold_capacity_daily` et `gold_item_daily` ne contiennent pas uniquement des
  lignes vides;
- l'historique atteint progressivement 60 jours;
- l'actualisation du modèle sémantique réussit;
- les rapports FR/EN affichent les mêmes totaux;
- les CU du Live Report et de Power BI sont réconciliées sur une période
  commune.

## 6. Passer de Basic à Advanced

La migration est additive :

1. conserver l'agent, les connecteurs et le Live Report Basic;
2. créer le workspace `Fabric Administration`;
3. déployer le Lakehouse et les collecteurs;
4. laisser l'historique s'accumuler;
5. publier le modèle et les rapports;
6. modifier les instructions de l'agent pour privilégier Gold sur les périodes
   historiques et la source directe pour la fraîcheur.

Le passage à Advanced ne nécessite pas de recréer l'agent ni le connecteur
Fabric Admin.

## 7. Retour d'Advanced vers Basic

Avant de supprimer le workspace :

1. désactiver les routines qui dépendent de Gold;
2. exporter les données requises pour audit;
3. retirer les liens vers les rapports Power BI du workspace;
4. confirmer que le Live Report utilise encore Fabric Admin MCP et Capacity
   Metrics direct;
5. informer les utilisateurs que les analyses 60 jours et les rapports Power BI
   ne seront plus disponibles.

Ne jamais supprimer le workspace pour corriger un problème de pipeline; réparer
ou désactiver d'abord les dépendances.

## 8. Dépannage rapide

| Symptôme | Vérification |
|---|---|
| Seulement quelques workspaces | Confirmer l'utilisation de `FabricAdmin_list_workspaces`, pas seulement Fabric Core |
| CU indisponibles | Vérifier l'ID du modèle, son actualisation et Read/Build |
| Requête CU 60 jours incomplète en Basic | Limite de rétention native; installer Advanced |
| Pipeline réussi mais Gold vide | Vérifier les alias DAX et la normalisation des colonnes |
| Actualisation Power BI refusée | Vérifier la connexion `WorkspaceIdentity` et son binding |
| 401/403 Admin API | Vérifier paramètres tenant, groupe de sécurité et propagation |
| 429 | Respecter `Retry-After`, cache et cadence de pagination |
| Live Report lent à froid | Conserver une réplique minimale de Container Apps |

## 9. Définition de terminé

### Basic

- inventaire tenant complet;
- Live Report bilingue fonctionnel;
- données CU récentes clairement datées ou explicitement indisponibles;
- agent en lecture seule;
- santé MCP et cache validés.

### Advanced

Tous les critères Basic, plus :

- collecte quotidienne opérationnelle;
- historique durable d'au moins 60 jours;
- modèle sémantique actualisable;
- deux rapports PBIP publiés;
- contrôles de fraîcheur, qualité et reprise documentés.
