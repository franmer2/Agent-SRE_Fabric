# Live Report de surveillance Fabric

Ce document est la spécification fonctionnelle de référence du Live Report
**Surveillance des capacités Fabric** intégré à Azure SRE Agent. Il complète le
[guide de déploiement](deployment.fr.md) et la
[procédure pas à pas](deployment-pas-a-pas.fr.md).

## 1. Référence de publication

La référence validée le 13 octobre 2026 correspond à la version de service 39.
Ce numéro est propre à l'actif Azure SRE utilisé pendant la validation : un
import dans un autre environnement peut produire un autre numéro. La conformité
doit donc être vérifiée avec la checklist de ce document, et non avec le seul
numéro de version.

Le dépôt ne contient pas actuellement le HTML exporté du Live Report. Avant un
déploiement client :

1. obtenir l'actif approuvé le plus récent auprès du responsable de la solution;
2. publier ou mettre à jour le même Live Report, sans créer de doublon;
3. conserver un export de l'actif approuvé dans le paquet de livraison contrôlé
   par l'organisation;
4. exécuter toute la recette de la section 4.

Ne pas reconstruire le rapport à partir de captures d'écran ou d'une ancienne
conversation d'auteur.

## 2. Sources et comportement attendu

Le Live Report appelle quatre outils en lecture seule :

- `FabricSRE` pour l'inventaire des capacités visible par l'identité;
- `FabricAdmin_list_workspaces`;
- `FabricAdmin_list_items`;
- `FabricAdmin_get_cu_metrics`, lorsque Capacity Metrics est configuré.

L'interface doit rester générique : aucun nom de client, identifiant de tenant,
abonnement, workspace, capacité ou artefact ne doit être codé en dur.

La version française utilise **espace de travail** et **artefact** dans tous les
libellés. La version anglaise conserve **workspace** et **item**.

## 3. Fonctions de la version de référence

### Présentation

- interface bilingue FR/EN et thèmes clair/sombre;
- affichage pleine largeur et mise en page responsive;
- titres contextuels ajoutant l'espace de travail sélectionné;
- filtres globaux dépendants par capacité et espace de travail;
- tableau des capacités et graphique **Artefacts par capacité** côte à côte sur
  écran large, empilés sur écran étroit;
- hauteur du graphique calculée selon le nombre de catégories, espacement
  minimal de 44 px par catégorie, barres de 28 px au maximum et défilement
  vertical au-delà de 560 px;
- aucun chevauchement de barres ni débordement horizontal;
- colonnes des tableaux redimensionnables.

### Indicateurs CU

- contrôle segmenté **CU-h / CU-s** appliqué à toutes les consommations
  cumulées, avec CU-h comme mode par défaut;
- en mode CU-h, **Consommation cumulée** calculée par `CU-s / 3 600` et
  affichée avec deux décimales;
- en mode CU-s, consommation cumulée brute affichée avec zéro décimale;
- **Moyenne soutenue** en CU avec trois décimales;
- **Pic de moyenne quotidienne** en CU avec trois décimales;
- tableaux des capacités, espaces de travail et artefacts harmonisés avec les
  mêmes unités et précisions : cumul selon le mode choisi, moyenne et pic en CU
  avec trois décimales;
- changement d'unité instantané, sans nouvel appel aux API, en conservant les
  valeurs CU-s brutes comme source de vérité;
- choix conservé pendant la navigation, les changements de langue et
  l'ouverture des fenêtres de détail de la session;
- en-têtes, descriptions accessibles, notes, infobulles, graphiques, Tree Map,
  résumés et fenêtre de détail alignés sur l'unité sélectionnée;
- tri des colonnes CU fondé sur les valeurs numériques brutes, et non sur les
  chaînes localisées affichées;
- pourcentage d'utilisation sous la moyenne et le pic lorsqu'une capacité
  numérique unique peut être déterminée;
- aucun pourcentage inventé lorsque plusieurs capacités ou un SKU non numérique
  rendent le dénominateur ambigu;
- message invitant à sélectionner une capacité lorsque le pourcentage ne peut
  pas être calculé;
- fenêtre de détail temporel appliquant les mêmes unités, précisions et
  pourcentages;
- distinction explicite entre une valeur zéro et une télémétrie indisponible.

### Glossaire CU

Le bouton **Glossaire CU** doit expliquer :

- CU, CU-s et CU-h;
- consommation cumulée, moyenne soutenue et moyenne quotidienne;
- différence entre pic de moyenne quotidienne et pic instantané;
- formule du pourcentage d'utilisation d'un SKU;
- effet des filtres actifs.

La fenêtre doit être accessible au clavier, se fermer par son bouton, le
backdrop ou `Échap`, mettre `aria-expanded` à jour et rendre le focus au bouton.

## 4. Recette obligatoire après publication

### Connecteurs et données

- [ ] les quatre outils attendus sont proposés au rapport;
- [ ] aucun outil n'est dupliqué;
- [ ] l'inventaire des capacités, espaces de travail et artefacts se charge;
- [ ] une valeur CU absente affiche **Non disponible**, jamais un faux zéro;
- [ ] la période réellement couverte est affichée.

### Français et anglais

- [ ] le rapport s'ouvre en français;
- [ ] aucun libellé français n'utilise `Workspace` ou `Item`;
- [ ] le passage en anglais affiche `Workspace` et `Item`;
- [ ] le retour en français conserve les filtres;
- [ ] les titres du graphique par espace de travail et de l'inventaire ajoutent
      le nom de l'espace sélectionné.

### Mise en page

- [ ] à 720 px, les cartes de la section Capacités sont empilées;
- [ ] à 1 024, 1 440 et 2 000 px, la page ne déborde pas horizontalement;
- [ ] les barres d'**Artefacts par capacité** ne se chevauchent pas;
- [ ] les valeurs CU restent sur une ligne;
- [ ] les tableaux restent utilisables avec un défilement interne.

### Calculs CU

- [ ] le mode par défaut est CU-h et le contrôle segmenté expose clairement
      l'état sélectionné au clavier et aux technologies d'assistance;
- [ ] `7 514 CU-s` devient `2,09 CU-h` en français et `2.09 CU-h` en anglais;
- [ ] le passage en CU-s affiche `7 514 CU-s` sans décimale dans le KPI, les
      trois tableaux, les graphiques, les infobulles et la fenêtre de détail;
- [ ] dans les trois tableaux, les colonnes cumulées suivent le mode choisi,
      tandis que moyenne et pic restent en CU avec trois décimales;
- [ ] pour `Load_Activities_E2E`, `5 009 CU-s`, `0,00414 CU` et `0,058 CU`
      deviennent `1,39 CU-h`, `0,004 CU` et `0,058 CU` en mode CU-h, puis
      `5 009 CU-s`, `0,004 CU` et `0,058 CU` en mode CU-s;
- [ ] les moyennes, pics et pourcentages ne changent pas lors du basculement;
- [ ] les en-têtes, descriptions accessibles et notes mentionnent CU-h et deux
      décimales en mode CU-h, puis CU-s et zéro décimale en mode CU-s, en
      français et en anglais;
- [ ] le tri ascendant et descendant des colonnes cumulées reste numérique et
      conserve le même ordre dans les deux modes;
- [ ] une télémétrie absente affiche **Non disponible**, tandis qu'un vrai zéro
      reste affiché;
- [ ] `0,0062 CU` devient `0,006 CU` en français;
- [ ] `0,085 CU` reste affiché avec trois décimales;
- [ ] pour un SKU F16, `0,0062 / 16 × 100` donne environ `0,04 %`;
- [ ] pour un SKU F16, `0,085 / 16 × 100` donne environ `0,53 %`;
- [ ] les pourcentages disparaissent lorsque le SKU est ambigu;
- [ ] le glossaire s'ouvre, se ferme avec `Échap` et rend le focus au bouton.

## 5. Capacité Fabric arrêtée

Le Live Report et `FabricAdmin` sont extérieurs au workspace Fabric Advanced.
L'arrêt de la capacité qui héberge le Lakehouse, les notebooks et le pipeline
n'empêche donc pas le rapport de s'ouvrir.

| Fonction | Comportement attendu |
|---|---|
| Ouverture du Live Report | Fonctionne |
| Inventaire des capacités, espaces de travail et artefacts | Devrait fonctionner, car il provient des API Fabric Admin via le MCP externe; le cache peut servir la dernière collecte pendant un rafraîchissement |
| État de la capacité | Devrait apparaître comme suspendue ou inactive après actualisation du cache |
| Données CU récentes | Peuvent devenir **indisponibles** si le modèle Fabric Capacity Metrics interrogé est hébergé sur la capacité arrêtée |
| Lakehouse et tables Bronze/Silver/Gold | Données conservées, mais calcul et accès dépendants de la capacité interrompus |
| Notebooks et pipeline quotidien | Ne s'exécutent plus tant que la capacité est arrêtée |
| Historique Advanced et rapports Power BI associés | N'est plus actualisé; les requêtes au modèle peuvent échouer |

Le rapport doit continuer à afficher l'inventaire disponible et marquer les CU
comme **Non disponible** lorsque la source ne répond pas.

Après redémarrage :

1. confirmer que la capacité est active;
2. vérifier `/health` du service Fabric Admin MCP;
3. relancer ou attendre le prochain pipeline selon le plan de reprise;
4. vérifier la fraîcheur Bronze, Silver et Gold;
5. actualiser le modèle sémantique;
6. réconcilier les CU du Live Report et de Power BI;
7. documenter tout trou historique. Capacity Metrics Compute ne conserve
   normalement qu'environ 14 jours.

## 6. Recommandation de résilience

Pour Advanced, utiliser de préférence une **petite capacité Fabric dédiée au
workspace d'administration SRE** qui contient le Lakehouse, les notebooks, le
pipeline, le modèle sémantique et les rapports Power BI. La dimensionner selon
la collecte réelle et la garder active pendant les fenêtres de surveillance.

Cette capacité n'héberge pas Azure SRE Agent ni Fabric Admin MCP : l'agent reste
dans Azure SRE et le MCP dans Azure Container Apps. La séparation évite qu'une
capacité de production désactive en même temps sa propre chaîne
d'historisation et de supervision.
