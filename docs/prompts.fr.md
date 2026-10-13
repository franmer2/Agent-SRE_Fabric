# Prompts de démarrage pour Azure SRE Agent et Microsoft Fabric

Ce catalogue aide un utilisateur qui découvre Azure SRE Agent à explorer
Microsoft Fabric progressivement, après avoir connecté un serveur MCP Fabric à
l'agent.

Les prompts de cette page :

- interrogent uniquement les outils auxquels l'agent a réellement accès;
- demandent à l'agent d'indiquer son périmètre et la fraîcheur des données;
- ne remplacent pas l'installation Basic ou Advanced;
- ne créent pas un rapport persistant, sauf si un outil de publication
  spécifique a été ajouté à l'agent.

## 1. Premier contact avec l'agent

```text
Explique en termes simples ce que tu peux faire pour Microsoft Fabric avec les
outils actuellement connectés. Liste aussi ce que tu ne peux pas faire.
```

```text
Quels connecteurs et outils Fabric peux-tu utiliser dans cette conversation ?
Pour chaque outil, indique s'il est en lecture seule et son périmètre.
```

```text
Vérifie la connexion à Fabric sans modifier aucune ressource. Donne le résultat
de chaque appel et explique toute erreur d'autorisation.
```

## 2. Découvrir le périmètre visible

```text
Liste les capacités, workspaces et types d'items Fabric que tu peux voir.
Commence par préciser si le résultat couvre tout le tenant ou seulement les
workspaces accessibles à ton identité. N'invente aucune donnée manquante.
```

```text
Crée un résumé exécutif de mon environnement Fabric visible : nombre de
capacités, nombre de workspaces, nombre d'items par type et principales limites
de visibilité. Indique l'heure de collecte.
```

```text
Quels workspaces semblent les plus importants à examiner en premier ? Classe-les
selon le nombre d'items et explique les limites de ce classement.
```

Avec le connecteur Fabric Core seul, les résultats sont limités aux ressources
visibles par l'identité. Ne pas présenter ce résultat comme un inventaire
exhaustif du tenant.

## 3. Examiner un workspace

```text
Analyse le workspace "<NOM-DU-WORKSPACE>". Liste ses items par type, signale les
noms en double et propose trois vérifications administratives utiles. Reste en
lecture seule.
```

```text
Dans le workspace "<NOM-DU-WORKSPACE>", quels sont les rapports, modèles
sémantiques, Lakehouses, Warehouses, notebooks et pipelines visibles ? Présente
le résultat dans un tableau.
```

```text
Compare les workspaces "<WORKSPACE-A>" et "<WORKSPACE-B>" selon les types
d'items visibles. Signale explicitement les données que tu ne peux pas obtenir.
```

## 4. Capacité et consommation

Ces prompts nécessitent une source Capacity Metrics connectée et accessible.

```text
Résume la consommation CU disponible pour les 7 derniers jours. Distingue total
en CU-secondes, moyenne soutenue et pic. Indique la période réellement
disponible et ne transforme jamais une donnée absente en zéro.
```

```text
Quelles capacités et quels items consomment le plus de CU sur la période
disponible ? Donne les cinq premiers, leur contribution et les limites de la
source.
```

```text
Recherche des signes de saturation ou de throttling dans les données
disponibles. Sépare les observations, les hypothèses et les recommandations.
```

Sans l'édition Advanced, la fenêtre Compute de Capacity Metrics est normalement
limitée à environ 14 jours. Un prompt demandant 30 ou 60 jours ne recrée pas les
données expirées.

## 5. Gouvernance et hygiène

```text
À partir des métadonnées visibles, identifie les espaces de travail ou
artefacts qui
méritent une vérification de gouvernance : nom ambigu, doublon apparent,
propriétaire non visible, certification absente ou contenu potentiellement
inactif. Ne conclus pas à une anomalie lorsque la donnée est indisponible.
```

```text
Prépare une liste de dix questions de gouvernance à poser aux administrateurs
Fabric à partir de l'inventaire visible. Classe-les par impact.
```

```text
Crée une checklist de revue hebdomadaire Fabric fondée uniquement sur les
signaux que tu peux réellement lire.
```

## 6. Générer des visuels à la demande

Azure SRE Agent peut produire des visualisations dans la conversation lorsque
l'expérience et les données retournées le permettent. Ces visuels sont
dynamiques et ne remplacent pas un Live Report publié.

```text
Génère un graphique en barres du nombre d'artefacts par espace de travail à
partir des
données visibles. Affiche les dix premiers. Si tu ne peux pas rendre le
graphique, fournis un tableau trié prêt à être visualisé et explique pourquoi.
```

```text
Génère un diagramme montrant la répartition des artefacts par type. Indique le
périmètre, la date et le nombre de valeurs inconnues. Si un diagramme circulaire
est illisible, utilise des barres horizontales.
```

```text
Si les données CU sont disponibles, trace l'évolution quotidienne des CU sur
la période réellement disponible. Ne prolonge pas artificiellement la série.
Ajoute une courte interprétation sous le graphique.
```

```text
Crée une vue de synthèse avec quatre indicateurs : capacités visibles,
espaces de travail visibles, artefacts visibles et fraîcheur des données. Ajoute
ensuite un graphique des dix espaces de travail contenant le plus d'artefacts.
Si les cartes visuelles
ne sont pas prises en charge, utilise un tableau Markdown.
```

Les mises en page, filtres et visuels générés dans une conversation ne sont pas
garantis entre deux sessions. Installer Basic pour un Live Report stable, ou
Advanced pour des rapports Power BI et un historique durable.

## 7. Préparer le passage à Basic

```text
Évalue si mon agent est prêt pour l'édition Basic de Fabric SRE. Vérifie les
outils Fabric connectés, le périmètre actuel, la disponibilité de Capacity
Metrics et les autorisations manquantes. Ne modifie rien.
```

```text
Explique la différence entre mon expérience actuelle et Fabric SRE Basic :
inventaire tenant, Fabric Admin MCP, Live Report bilingue et Capacity Metrics.
Donne une checklist d'installation sans afficher de secret.
```

```text
Après l'installation Basic, vérifie que FabricAdmin_list_workspaces,
FabricAdmin_list_items et, si configuré, FabricAdmin_get_cu_metrics sont
disponibles. Compare le périmètre Fabric Admin au périmètre Fabric Core.
```

## 8. Préparer le passage à Advanced

```text
Évalue si nous avons besoin de Fabric SRE Advanced. Base ta recommandation sur
le besoin d'historique supérieur à 14 jours, les tendances, les SLO, les coûts,
les rapports Power BI et la conservation des données. Sépare besoins confirmés
et hypothèses.
```

```text
Prépare une checklist de prérequis Advanced : abonnement Azure, capacité
Fabric, workspace d'administration, identité du workspace, Lakehouse,
notebooks, pipeline, modèle sémantique et rapports. Ne crée aucune ressource.
```

```text
Explique à un décideur non technique ce que l'édition Advanced ajoute à Basic,
les coûts opérationnels supplémentaires et les responsabilités de maintenance.
```

## 9. Prompts à éviter

Éviter les demandes ambiguës comme :

```text
Optimise tout Fabric.
```

```text
Corrige les capacités.
```

```text
Crée le dashboard et publie-le.
```

Préférer une demande qui précise :

- le périmètre;
- la période;
- la source souhaitée;
- le format attendu;
- l'obligation de rester en lecture seule;
- la conduite à tenir lorsque la donnée manque.
