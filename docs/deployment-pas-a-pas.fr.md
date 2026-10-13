# Déploiement pas à pas de Fabric SRE

Ce document explique comment installer la solution Fabric SRE lorsque la
personne qui réalise l'installation ne connaît ni le projet ni l'environnement
du client.

Il complète le [guide de déploiement technique](deployment.fr.md). Il ne le
remplace pas pour les choix d'architecture.

> **Important**
>
> - Suivre les étapes dans l'ordre.
> - Ne jamais deviner un identifiant, un abonnement ou un nom de ressource.
> - Ne jamais copier un secret, une clé API ou un mot de passe dans ce document,
>   dans un courriel, dans Teams ou dans Git.
> - Si un bouton ou une ressource décrite ci-dessous n'est pas visible, arrêter
>   l'installation et demander l'aide de l'administrateur indiqué dans la fiche
>   de préparation.
> - Les libellés des portails évoluent. Les noms anglais sont indiqués entre
>   parenthèses lorsqu'ils peuvent aider à retrouver un écran.

## 1. Parcours progressif

La solution se découvre et s'installe en trois niveaux. Il n'est pas nécessaire
de choisir Basic ou Advanced avant d'avoir essayé l'agent.

### Niveau Découverte

Découverte permet :

- de créer Azure SRE Agent depuis le portail;
- de connecter Fabric Core MCP;
- de poser des questions sur les ressources visibles;
- de générer des tableaux et des visuels à la demande;
- de comprendre les capacités et les limites de l'agent avant d'installer la
  solution Fabric SRE.

Ce niveau ne fournit pas un inventaire tenant garanti, un Live Report persistant
ou un historique durable.

### Édition Basic

Basic installe :

- la configuration Fabric SRE sur l'agent Azure SRE déjà créé;
- le connecteur Fabric Core déjà testé pendant Découverte;
- un service Fabric Admin MCP en lecture seule;
- le Live Report bilingue;
- en option, les métriques récentes de l'application Fabric Capacity Metrics.

Basic ne crée pas d'historique durable dans un Lakehouse.

### Édition Advanced

Advanced installe d'abord Basic, puis ajoute :

- un workspace Microsoft Fabric nommé par défaut `Fabric Administration`;
- un Lakehouse nommé par défaut `FabricSRE`;
- six notebooks;
- un pipeline de collecte quotidien;
- les tables Bronze, Silver et Gold;
- un modèle sémantique Power BI;
- un rapport français et un rapport anglais.

### Comment choisir

Commencer par **Découverte** pour valider l'accès à Fabric et apprendre à
utiliser Azure SRE Agent.

Choisir ensuite **Basic** pour obtenir un inventaire tenant, un Live Report
bilingue et éventuellement les CU récentes sans historique durable.

Choisir **Advanced** si le client veut :

- conserver au moins 60 jours d'historique;
- analyser les tendances;
- utiliser les rapports Power BI versionnés;
- conserver quotidiennement les données d'administration.

Le passage de Découverte à Basic ou Advanced ne nécessite pas de recréer
l'agent.

## 2. Répartition des responsabilités

Une seule personne peut cumuler plusieurs rôles, mais tous les rôles ci-dessous
doivent être couverts.

| Rôle | Ce que cette personne doit pouvoir faire |
|---|---|
| Responsable de la solution | Valider la progression Découverte, Basic ou Advanced et les noms |
| Administrateur Fabric | Modifier les paramètres du tenant Fabric |
| Administrateur Azure | Créer ou utiliser les ressources dans l'abonnement |
| Administrateur Entra | Créer un groupe de sécurité et gérer ses membres |
| Administrateur Azure SRE | Modifier l'agent et ses connecteurs |
| Administrateur Power BI | Publier et configurer le modèle et les rapports |
| Installateur | Exécuter les étapes de ce guide |

## 3. Fiche de préparation

Avant toute action, demander au responsable de remplir les lignes nécessaires
au niveau Découverte. Compléter les paramètres Azure supplémentaires seulement
au moment de passer à Basic ou Advanced. Conserver la fiche dans un emplacement
sécurisé du client.

| Information | Valeur à fournir |
|---|---|
| Niveau cible | `Découverte`, `Basic` ou `Advanced` |
| Nom du client | |
| Code client en minuscules, sans espace | |
| Langue par défaut | `fr-CA` ou `en-CA` |
| Fuseau horaire | Exemple : `America/Toronto` |
| Nom du tenant Microsoft Entra | |
| ID du tenant | |
| ID de l'abonnement Azure de l'agent | |
| ID des abonnements contenant les capacités Fabric | |
| Nom du groupe de ressources Azure | |
| Région Azure | Exemple : `canadacentral` |
| Nom de l'agent Azure SRE | |
| Nom du groupe de sécurité pour les API Fabric Admin | |
| Nom de l'identité managée Azure | |
| Nom de l'environnement Container Apps | |
| Nom de la Container App Fabric Admin MCP | |
| Nom de l'Azure Container Registry | |
| Nom du workspace Fabric | Par défaut : `Fabric Administration` |
| Nom du Lakehouse | Par défaut : `FabricSRE` |
| Nom de la capacité Fabric à utiliser | Advanced seulement |
| ID du modèle Fabric Capacity Metrics | Si les CU sont activées |
| Administrateur à contacter en cas de blocage | |

### Règles pour les noms Azure

Utiliser uniquement les noms approuvés par le client.

- Le nom de l'Azure Container Registry doit être unique dans Azure et ne peut
  contenir que des lettres et des chiffres.
- Le nom de la Container App doit être unique dans son environnement.
- Le code client ne doit contenir que des lettres minuscules, des chiffres et
  des tirets.
- Ne pas ajouter de suffixe comme `test`, `prod` ou une région sans validation.

## 4. Vérifications avant de commencer

Cocher chaque ligne.

- [ ] Le niveau Découverte, Basic ou Advanced est approuvé.
- [ ] Les lignes de la fiche nécessaires au niveau choisi sont complètes.
- [ ] L'installateur utilise un compte nominatif, jamais un compte partagé.
- [ ] Le compte voit le bon tenant Microsoft Entra.
- [ ] Le compte voit le bon abonnement Azure.
- [ ] Le compte peut ouvrir le portail Fabric.
- [ ] Le compte peut créer ou ouvrir Azure SRE Agent.

Pour Basic ou Advanced seulement :

- [ ] Une capacité Fabric est disponible pour Advanced.
- [ ] Le dépôt Fabric SRE est disponible sur le poste.
- [ ] Une fenêtre de changement a été approuvée.
- [ ] Une personne capable d'accorder les droits est joignable.

Ne pas continuer si une case reste vide.

## 5. Ouvrir les portails nécessaires

Ouvrir chaque lien dans un onglet distinct avec le même compte professionnel.

1. Portail Azure SRE Agent : <https://sre.azure.com>
2. Portail Azure : <https://portal.azure.com>
3. Portail Microsoft Fabric : <https://app.fabric.microsoft.com>

Dans chaque portail :

1. Cliquer sur l'avatar en haut à droite.
2. Vérifier l'adresse du compte.
3. Vérifier le nom de l'organisation ou du tenant.
4. Si le tenant n'est pas le bon, cliquer sur **Changer de répertoire**
   (**Switch directory**) et sélectionner le tenant fourni dans la fiche.

> **Point de contrôle**
>
> Le même tenant client doit être affiché dans Azure SRE Agent, Azure et
> Fabric.

# Partie 0 — Découvrir Azure SRE Agent avec Fabric

Cette partie ne requiert pas encore le Lakehouse, les notebooks, le pipeline,
Power BI ou le service Fabric Admin MCP de la solution Basic.

## D1. Créer l'agent depuis le portail

1. Ouvrir <https://sre.azure.com>.
2. Se connecter avec le compte professionnel approuvé.
3. Cliquer sur **Create agent**.
4. Dans **Subscription**, sélectionner l'abonnement approuvé.
5. Dans **Resource group**, sélectionner un groupe existant ou saisir le nom du
   groupe approuvé à créer.
6. Dans **Agent name**, saisir le nom validé.
7. Dans **Region**, sélectionner une région prise en charge et approuvée.
8. Dans **Model provider**, sélectionner le fournisseur approuvé par le client.
9. Dans **Application Insights**, conserver la création proposée ou
   sélectionner la ressource approuvée.
10. Cliquer sur **Next**.
11. Vérifier l'abonnement, le groupe, le nom et la région.
12. Cliquer sur **Create**.
13. Attendre que le déploiement indique **Succeeded**.
14. Cliquer sur **Set up your agent**.

La création prend normalement quelques minutes. Le portail crée l'agent, ses
identités managées et les ressources de supervision choisies.

> **Point de contrôle**
>
> Le compte courant doit disposer du rôle **SRE Agent Administrator** sur le
> nouvel agent.

## D2. Ajouter le connecteur Fabric

Utiliser le serveur MCP Fabric approuvé par l'organisation. Ne pas inventer une
URL et ne pas utiliser un serveur communautaire non validé.

Dans <https://sre.azure.com> :

1. Ouvrir l'agent.
2. Ouvrir **Builder**.
3. Cliquer sur **Connectors**.
4. Cliquer sur **+ Add connector**.
5. Choisir **MCP Server**.
6. Saisir l'URL du serveur Fabric MCP approuvé.
7. Choisir le mode d'authentification fourni par l'administrateur.
8. Enregistrer sans placer de secret dans le nom ou la description.
9. Attendre que l'état passe de **Initializing** à **Connected**.
10. Cliquer sur **Edit** pour ce connecteur.
11. Dans **MCP Tools**, sélectionner uniquement les outils Fabric de lecture
    nécessaires.
12. Cliquer sur **Save**.

Azure SRE Agent accepte au maximum 80 outils sur l'ensemble de ses connecteurs.
Ne pas sélectionner tous les outils par défaut.

## D3. Tester la connexion

1. Cliquer sur **New chat thread**.
2. Envoyer :

```text
Quels outils Microsoft Fabric peux-tu utiliser dans cette conversation ?
Indique leur périmètre et précise lesquels sont en lecture seule.
```

3. Vérifier que les cartes d'appel d'outil affichent **Completed**.
4. Envoyer :

```text
Vérifie la connexion à Fabric sans modifier aucune ressource. Liste les
workspaces visibles et précise clairement si ce résultat couvre tout le tenant
ou seulement les workspaces accessibles à ton identité.
```

Si l'appel échoue, revenir à **Builder > Connectors**, vérifier l'état, l'URL,
l'authentification et la sélection des outils.

## D4. Commencer avec des prompts guidés

Utiliser le [catalogue de prompts](prompts.fr.md). Pour une première session,
essayer dans cet ordre :

```text
Explique en termes simples ce que tu peux faire pour Microsoft Fabric avec les
outils actuellement connectés. Liste aussi ce que tu ne peux pas faire.
```

```text
Crée un résumé exécutif de mon environnement Fabric visible : nombre de
capacités, nombre de workspaces, nombre d'items par type et principales limites
de visibilité. Indique l'heure de collecte.
```

```text
Génère un graphique en barres du nombre d'items par workspace à partir des
données visibles. Affiche les dix premiers. Si tu ne peux pas rendre le
graphique, fournis un tableau trié prêt à être visualisé et explique pourquoi.
```

Les graphiques générés dans le chat sont des résultats à la demande. Ils ne
créent pas un dashboard persistant et leurs filtres ne sont pas conservés entre
les conversations.

## D5. Choisir l'étape suivante

Rester au niveau Découverte si les questions ponctuelles et les ressources
visibles par l'identité suffisent.

Passer à **Basic** pour :

- obtenir un inventaire en lecture seule à l'échelle du tenant;
- ajouter le Live Report bilingue;
- utiliser Capacity Metrics pour les CU récentes, si disponible;
- proposer des prompts communs à tous les utilisateurs.

Passer à **Advanced** pour ajouter un historique durable, des tendances, des
SLO, un modèle sémantique et des rapports Power BI.

Les sections 6 à 13 ci-dessous préparent Basic et Advanced. Elles ne sont pas
requises pour rester au niveau Découverte.

## 6. Relever les identifiants sans les deviner

### 6.1 ID du tenant

Dans le portail Azure :

1. Dans la barre de recherche supérieure, saisir `Microsoft Entra ID`.
2. Cliquer sur **Microsoft Entra ID**.
3. Dans **Vue d'ensemble** (**Overview**), repérer **ID de locataire**
   (**Tenant ID**).
4. Cliquer sur l'icône de copie.
5. Comparer la valeur avec la fiche de préparation.

### 6.2 ID de l'abonnement

Dans le portail Azure :

1. Dans la barre de recherche, saisir `Abonnements`.
2. Cliquer sur **Abonnements** (**Subscriptions**).
3. Cliquer sur l'abonnement fourni dans la fiche.
4. Dans **Vue d'ensemble**, copier **ID de l'abonnement**.
5. Vérifier que l'état est **Actif** (**Active**).

### 6.3 Groupe de ressources

Toujours dans le portail Azure :

1. Rechercher `Groupes de ressources`.
2. Cliquer sur **Groupes de ressources**.
3. Rechercher le nom fourni dans la fiche.
4. Ouvrir le groupe et vérifier l'abonnement affiché en haut de la page.

Si le groupe n'existe pas et si sa création a été autorisée :

1. Cliquer sur **Créer**.
2. Choisir le bon abonnement.
3. Saisir exactement le nom approuvé.
4. Choisir la région approuvée.
5. Cliquer sur **Vérifier + créer**, puis sur **Créer**.

## 7. Préparer Microsoft Entra et Fabric

Cette section doit être réalisée par un administrateur Entra/Fabric.

### 7.1 Créer ou vérifier le groupe de sécurité

Dans le portail Azure :

1. Rechercher `Microsoft Entra ID`.
2. Dans le menu de gauche, cliquer sur **Groupes**.
3. Cliquer sur **Tous les groupes**.
4. Rechercher le groupe indiqué dans
   `adminApiSecurityGroupName`.
5. S'il existe, l'ouvrir et confirmer que son **Type de groupe** est
   **Sécurité**.

Si le groupe n'existe pas :

1. Cliquer sur **Nouveau groupe**.
2. Pour **Type de groupe**, choisir **Sécurité**.
3. Saisir le nom exact fourni dans la fiche.
4. Pour **Type d'appartenance**, choisir **Attribué** (**Assigned**).
5. Ne pas ajouter manuellement l'application Fabric Admin à cette étape : le
   script le fera.
6. Cliquer sur **Créer**.

### 7.2 Autoriser les API Fabric publiques

Dans le portail Fabric :

1. Dans la barre de navigation de gauche, ouvrir **Catalogue OneLake**
   (**OneLake catalog**).
2. Cliquer sur **Gouverner** (**Govern**).
3. Cliquer sur **Configurations**.
4. Cliquer sur **Paramètres du locataire** (**Tenant settings**).
5. Utiliser la zone de recherche et saisir
   `Service principals can call Fabric public APIs`.
6. Ouvrir le paramètre.
7. Activer le paramètre.
8. Choisir l'option qui limite l'accès à des groupes de sécurité précis.
9. Ajouter le groupe créé à l'étape 7.1.
10. Cliquer sur **Appliquer** (**Apply**).

### 7.3 Autoriser les API d'administration en lecture seule

Dans le même écran **Paramètres du locataire** :

1. Rechercher
   `Service principals can access read-only admin APIs`.
2. Ouvrir le paramètre.
3. Activer le paramètre.
4. Limiter l'accès au même groupe de sécurité.
5. Cliquer sur **Appliquer**.

Ne pas activer l'accès aux API d'administration de mise à jour pour cette
identité.

### 7.4 Attendre la propagation

Les paramètres du tenant et l'appartenance à un groupe peuvent prendre quelques
minutes avant d'être utilisables.

Attendre 15 minutes avant de diagnostiquer un premier refus `401` ou `403`.

## 8. Préparer les ressources Azure requises

### 8.1 Créer ou vérifier l'identité managée

Le script de déploiement réutilise une identité managée affectée par
l'utilisateur. Il ne la crée pas.

Dans le portail Azure :

1. Rechercher `Identités managées`.
2. Cliquer sur **Identités managées** (**Managed Identities**).
3. Rechercher le nom fourni dans `managedIdentityName`.
4. Si l'identité existe, vérifier son abonnement et son groupe de ressources.

Si elle n'existe pas :

1. Cliquer sur **Créer**.
2. Choisir le bon abonnement.
3. Choisir le groupe de ressources de la fiche.
4. Choisir la région approuvée.
5. Saisir le nom exact.
6. Cliquer sur **Vérifier + créer**, puis sur **Créer**.

Le script accordera ensuite le rôle `AcrPull` à cette identité sur le registre.

### 8.2 Vérifier les droits de l'installateur

Dans le groupe de ressources Azure :

1. Cliquer sur **Contrôle d'accès (IAM)**.
2. Cliquer sur **Afficher mon accès** (**View my access**).
3. Vérifier que le compte dispose des droits nécessaires pour créer des
   ressources et attribuer un rôle.

Le plus souvent, il faut :

- **Contributeur** sur le groupe de ressources;
- **Administrateur de l'accès utilisateur** ou **Propriétaire** pour créer
  l'attribution `AcrPull`;
- les droits Entra nécessaires pour créer une application et un secret;
- les droits nécessaires pour ajouter un membre au groupe de sécurité.

Si l'un de ces droits manque, arrêter et contacter l'administrateur Azure.

## 9. Préparer le poste d'installation

### 9.1 Logiciels requis

Installer :

- Visual Studio Code;
- PowerShell 7;
- Azure CLI;
- Python 3.11 ou version ultérieure;
- Node.js 22;
- Power BI Desktop pour Advanced.

Pour confirmer les installations :

1. Ouvrir Visual Studio Code.
2. Cliquer sur **Fichier** > **Ouvrir un dossier**.
3. Sélectionner le dossier racine `Azure SRE`.
4. Cliquer sur **Terminal** > **Nouveau terminal**.
5. Vérifier que le terminal indique `PowerShell`.
6. Copier-coller les commandes suivantes, une ligne à la fois :

```powershell
pwsh --version
az version
python --version
node --version
```

Résultats attendus :

- PowerShell retourne une version 7;
- Azure CLI retourne ses numéros de version;
- Python retourne au minimum `3.11`;
- Node retourne une version 22.

Si une commande affiche « introuvable » ou « non reconnu », installer ou
réparer le logiciel concerné avant de continuer.

### 9.2 Installer les dépendances du projet

Dans le terminal Visual Studio Code ouvert à la racine du projet :

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
npm install -g @microsoft/powerbi-report-authoring-cli@latest
az extension add --name containerapp --upgrade
```

Attendre le retour de l'invite après chaque commande.

> **Point de contrôle**
>
> Aucune commande ne doit se terminer par un message d'erreur rouge. Les
> avertissements de mise à jour ne sont pas nécessairement bloquants.

## 10. Se connecter au bon environnement Azure

Dans le terminal :

```powershell
az login --tenant "<ID-DU-TENANT>"
```

1. Une page de connexion s'ouvre.
2. Se connecter avec le compte professionnel approuvé.
3. Revenir dans Visual Studio Code.
4. Sélectionner l'abonnement de l'agent :

```powershell
az account set --subscription "<ID-ABONNEMENT-AGENT>"
az account show --output table
```

Comparer le nom de l'abonnement, l'ID du tenant et le compte affichés avec la
fiche de préparation.

Si une valeur diffère, ne lancer aucun script.

## 11. Créer le fichier de configuration client

### 11.1 Copier le modèle

Dans le terminal :

```powershell
Copy-Item .\config\client.parameters.example.yaml `
  .\config\client.parameters.yaml
```

Dans l'explorateur de fichiers de Visual Studio Code :

1. Développer le dossier `config`.
2. Cliquer sur `client.parameters.yaml`.
3. Remplacer les valeurs d'exemple par les valeurs approuvées.

### 11.2 Valeurs obligatoires

| Champ | Valeur attendue |
|---|---|
| `client.code` | Code court en minuscules, sans espace |
| `client.displayName` | Nom lisible du client |
| `client.defaultLanguage` | `fr-CA` ou `en-CA` |
| `client.timeZone` | Fuseau IANA, par exemple `America/Toronto` |
| `azure.tenantId` | ID du tenant |
| `azure.subscriptionIds` | Liste des abonnements contenant les capacités |
| `foundry.subscriptionId` | Abonnement de l'agent |
| `foundry.resourceGroup` | Groupe de ressources de l'agent |
| `foundry.agentName` | Nom exact de l'agent |
| `foundry.fabricAdminMcp.appName` | Nom de la Container App |
| `foundry.fabricAdminMcp.environmentName` | Nom de l'environnement Container Apps |
| `foundry.fabricAdminMcp.managedIdentityName` | Identité créée à l'étape 8 |
| `foundry.fabricAdminMcp.registryName` | Nom unique de l'ACR |
| `foundry.fabricAdminMcp.servicePrincipalDisplayName` | Nom de l'application Entra à créer |
| `foundry.fabricAdminMcp.adminApiSecurityGroupName` | Groupe créé à l'étape 7 |
| `foundry.fabricAdminMcp.location` | Région Azure, sans espace |
| `fabric.capacityScope.includeIds` | Capacités incluses, ou `[]` selon la décision client |
| `fabric.capacityScope.excludeIds` | Capacités exclues |
| `fabric.capacityMetrics.semanticModelId` | ID du modèle Capacity Metrics, ou vide |

Ne pas ajouter de mot de passe ou de clé API dans ce fichier.

### 11.3 Variables d'environnement

Dans le terminal actif :

```powershell
$env:AZURE_TENANT_ID = "<ID-DU-TENANT>"
$env:AZURE_SUBSCRIPTION_ID = "<ID-ABONNEMENT>"
$env:AZURE_FOUNDRY_SUBSCRIPTION_ID = "<ID-ABONNEMENT-AGENT>"
$env:FOUNDRY_RESOURCE_GROUP = "<GROUPE-DE-RESSOURCES>"
$env:FOUNDRY_AGENT_NAME = "<NOM-DE-L-AGENT>"
$env:AZURE_LOCATION = "<REGION-AZURE>"
```

Ces valeurs ne restent actives que dans le terminal courant. Si le terminal est
fermé, les définir de nouveau.

### 11.4 Vérifier le fichier

Dans le terminal :

```powershell
$env:PYTHONPATH = ".\src"
python -c "from fabric_sre.config import load_config; load_config(r'.\config\client.parameters.yaml', r'.\config\client.parameters.schema.json'); print('Configuration valide')"
```

Résultat attendu :

```text
Configuration valide
```

Corriger toute erreur indiquée avant de continuer.

## 12. Valider le paquet

Toujours à la racine du projet :

```powershell
.\scripts\validate.ps1
```

La commande exécute les tests, vérifie le code et valide les deux rapports.

Résultat attendu à la fin :

```text
Fabric SRE validation succeeded.
```

Si la validation échoue :

1. Ne pas lancer le déploiement.
2. Copier uniquement le message d'erreur, sans secret.
3. Faire corriger le paquet par l'équipe technique.
4. Relancer la validation depuis le début.

## 13. Vérifier l'agent cible

Dans le terminal :

```powershell
.\scripts\preflight-agent.ps1 `
  -SubscriptionId "<ID-ABONNEMENT-AGENT>" `
  -ResourceGroup "<GROUPE-DE-RESSOURCES>" `
  -AgentName "<NOM-DE-L-AGENT>" `
  -ExpectedAccount "<COMPTE-PROFESSIONNEL>"
```

Le résultat doit afficher une ressource correspondant au nom de l'agent.

Si le script indique que l'abonnement ou l'agent n'est pas visible, ne pas
continuer.

# Partie A — Installation Basic

Basic réutilise l'agent et le connecteur Fabric déjà testés dans le parcours
Découverte. Il ajoute Fabric Admin MCP, le Live Report et les prompts communs;
il ne faut pas créer un deuxième agent.

### Alternative assistée par prompts d'administration

Un administrateur peut automatiser une partie de Basic depuis un client
compatible avec Azure MCP Server, par exemple VS Code ou GitHub Copilot CLI.
Azure MCP Server expose des outils capables de créer ou mettre à jour :

- un connecteur MCP sur une ressource Azure SRE Agent;
- des prompts communs réutilisables par les utilisateurs.

Exemples d'intention d'administration :

```text
Crée ou mets à jour sur l'agent "<NOM-AGENT>" un connecteur MCP HTTP nommé
"FabricAdmin" qui utilise l'endpoint Fabric Admin MCP approuvé.
```

```text
Crée sur l'agent "<NOM-AGENT>" un prompt commun nommé
"fabric-basic-overview" avec le contenu du prompt de synthèse Basic approuvé.
```

Cette alternative simplifie les clics, mais ne réalise pas toute
l'installation :

- elle doit être lancée depuis un client qui dispose d'Azure MCP Server, pas
  comme un prompt ordinaire dans le chat de l'agent;
- l'endpoint Fabric Admin MCP doit déjà avoir été déployé;
- le compte doit disposer des droits de modification sur Azure SRE Agent;
- aucune clé API ne doit être écrite en clair dans le prompt;
- le Live Report doit encore être importé ou publié comme actif persistant.

Pour un premier déploiement ou si le stockage sécurisé des secrets n'est pas
déjà configuré, suivre les étapes du portail ci-dessous.

## 14. Déployer Fabric Admin MCP

Dans le terminal :

```powershell
.\scripts\deploy-fabric-admin-mcp.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml
```

Cette opération peut prendre plusieurs minutes. Le script :

1. crée ou réutilise l'application Entra de lecture;
2. crée son principal de service;
3. ajoute ce principal au groupe autorisé dans Fabric;
4. crée un secret applicatif d'une durée d'un an;
5. crée ou réutilise l'environnement Container Apps;
6. crée l'Azure Container Registry s'il n'existe pas;
7. construit l'image du service;
8. attribue `AcrPull` à l'identité managée;
9. crée ou met à jour la Container App;
10. enregistre les secrets dans Container Apps.

À la fin, un bloc JSON est affiché. Il doit contenir :

- `endpoint` avec une adresse terminée par `/mcp`;
- `health` avec une adresse terminée par `/health`;
- `apiKeyConfigured` avec la valeur `true`;
- `apiKeyHeader` avec la valeur `x-api-key`.

Copier uniquement les URL `endpoint` et `health` dans la fiche de déploiement.
Ne pas copier de secret.

### 14.1 Vérifier la ressource dans Azure

Dans le portail Azure :

1. Ouvrir le groupe de ressources.
2. Vérifier la présence des ressources suivantes :
   - une **Container App**;
   - un **environnement Container Apps**;
   - un **Azure Container Registry**;
   - l'**identité managée**.
3. Cliquer sur la Container App.
4. Dans **Vue d'ensemble**, vérifier que l'état est **En cours d'exécution**
   (**Running**).
5. Dans **Révisions et réplicas**, vérifier qu'une révision est active et qu'au
   moins un réplica est prêt.

### 14.2 Tester la page de santé

Copier l'URL `health` dans un navigateur.

Résultat attendu :

```json
{"status":"ok"}
```

Si la page ne répond pas :

1. Dans la Container App, cliquer sur **Journaux** ou **Flux de journaux**.
2. Rechercher une erreur de démarrage.
3. Ne pas recréer la ressource manuellement.
4. Faire analyser l'erreur par l'équipe technique.

## 15. Récupérer la clé du connecteur de façon sécurisée

La clé est stockée comme secret de la Container App. Ne l'afficher que lorsque
l'écran de configuration du connecteur est prêt.

Dans le portail Azure :

1. Ouvrir la Container App.
2. Dans le menu de gauche, ouvrir **Secrets**.
3. Repérer `mcp-api-key`.
4. Cliquer sur l'action permettant d'afficher ou de copier sa valeur.
5. Coller immédiatement la valeur dans le champ secret du connecteur.
6. Ne pas enregistrer la valeur dans un fichier local.

Si le portail ne permet pas de lire la valeur, demander à un administrateur
Azure de la récupérer de façon sécurisée. Ne pas générer une deuxième clé sans
procédure de rotation.

## 16. Ajouter le connecteur FabricAdmin à l'agent

Les écrans exacts dépendent de la version de l'interface Azure SRE utilisée par
le client. Le connecteur doit accepter un serveur MCP distant avec un en-tête
personnalisé. Si l'interface ne propose pas ces options, arrêter et demander à
l'administrateur Azure SRE; ne pas remplacer l'authentification par
« aucune ».

Dans l'interface d'administration Azure SRE :

1. Ouvrir le projet indiqué dans la fiche.
2. Ouvrir l'agent cible.
3. Ouvrir **Outils** (**Tools**) ou **Connecteurs** (**Connectors**).
4. Cliquer sur **Ajouter**.
5. Choisir **MCP**.
6. Pour le transport, choisir **Streamable HTTP**.
7. Pour le nom, saisir `FabricAdmin`.
8. Pour l'URL, coller la valeur `endpoint` terminée par `/mcp`.
9. Pour l'authentification, choisir **En-tête personnalisé**
   (**Custom header**).
10. Pour le nom de l'en-tête, saisir exactement `x-api-key`.
11. Pour la valeur, coller la clé récupérée à l'étape 15.
12. Enregistrer.
13. Attendre que la connexion soit indiquée comme disponible.
14. N'activer que les outils :
    - `list_workspaces`;
    - `list_items`;
    - `get_cu_metrics` si l'ID Capacity Metrics a été fourni.

Les noms visibles par l'agent doivent être :

- `FabricAdmin_list_workspaces`;
- `FabricAdmin_list_items`;
- `FabricAdmin_get_cu_metrics`, si activé.

## 17. Vérifier le connecteur Fabric Core

Dans le même écran :

1. Ouvrir le connecteur nommé `FabricSRE`.
2. Confirmer qu'il pointe vers Fabric Core MCP.
3. Ne pas ajouter une deuxième fois les outils Fabric Admin.
4. Enregistrer sans modifier les autorisations si le connecteur est déjà
   fonctionnel.

Fabric Core sert aux ressources visibles par l'identité. Fabric Admin sert à
l'inventaire en lecture seule à l'échelle du tenant.

## 18. Mettre à jour la configuration de l'agent

Dans l'interface Azure SRE :

1. Ouvrir la configuration de l'agent `meta_agent`.
2. Choisir l'action **Importer**, **Téléverser** ou **Modifier la
   configuration**, selon l'interface.
3. Sélectionner le fichier
   `agent\azure-sre-agent.yaml`.
4. Vérifier que le nom reste `meta_agent`.
5. Vérifier que les outils `FabricAdmin_*` et `FabricSRE_*` sont listés une
   seule fois.
6. Enregistrer.
7. Publier une nouvelle version si l'interface distingue **Enregistrer** et
   **Publier**.

Ne pas activer d'outil d'écriture non décrit dans le fichier.

## 19. Ajouter les routines

Si l'environnement Azure SRE prend en charge l'import de routines :

1. Ouvrir **Routines** ou **Schedules**.
2. Cliquer sur **Importer**.
3. Sélectionner `agent\routines.yaml`.
4. Vérifier le fuseau horaire.
5. Laisser les routines désactivées jusqu'à la fin des tests.
6. Enregistrer.

Si l'import n'est pas disponible, transmettre le fichier à l'administrateur
Azure SRE. Ne pas recréer les expressions de planification au hasard.

## 20. Publier le Live Report

Dans l'interface Azure SRE :

1. Ouvrir la section **Live Reports** ou **Reports**.
2. Sélectionner l'actif bilingue approuvé le plus récent. La référence validée
   est la version de service 39, mais le numéro peut changer après import.
3. Lier le rapport à l'agent `meta_agent`.
4. Vérifier que `FabricSRE` pour les capacités et les trois outils
   `FabricAdmin` sont proposés comme sources.
5. Publier.
6. Ouvrir le rapport publié.
7. Passer de FR à EN puis revenir à FR.
8. Vérifier que les filtres restent appliqués.
9. Exécuter toute la recette de la
   [spécification du Live Report](live-report.fr.md), notamment la terminologie
   **espaces de travail/artefacts**, le toggle cumulatif CU-h/CU-s, les calculs
   CU, le glossaire, les titres contextuels et l'absence de chevauchement des
   barres.

Si aucun actif de Live Report n'est fourni dans l'environnement, arrêter cette
étape et demander au responsable de la solution l'actif à publier.

Pour Advanced, recommander une petite capacité Fabric dédiée au workspace
d'administration SRE. Elle héberge le Lakehouse, les notebooks, le pipeline,
le modèle et les rapports, mais pas Azure SRE Agent ni Fabric Admin MCP. Le
comportement dégradé et la reprise sont décrits dans
[Capacité Fabric arrêtée](live-report.fr.md#5-capacité-fabric-arrêtée).

## 21. Recette Basic

Dans la zone de test de l'agent, envoyer les demandes suivantes :

1. `Donne-moi l'état de santé du service Fabric Admin.`
2. `Liste les workspaces Fabric non personnels du tenant.`
3. `Liste les items du workspace <nom connu>.`
4. Si Capacity Metrics est configuré :
   `Résume la consommation CU des 7 derniers jours.`

Vérifier :

- [ ] la santé retourne `ok`;
- [ ] l'inventaire contient les workspaces attendus;
- [ ] l'agent distingue données absentes et valeur zéro;
- [ ] la période réellement disponible est indiquée;
- [ ] aucune action d'écriture n'est proposée sans approbation;
- [ ] aucun secret n'apparaît dans la réponse ou dans les journaux.

Activer les routines seulement après validation de ces contrôles.

Si seule l'édition Basic est demandée, passer directement à la section
[Clôture du déploiement](#34-clôture-du-déploiement).

# Partie B — Installation Advanced

Advanced nécessite une installation Basic réussie.

## 22. Prévisualiser la création du workspace

Dans le terminal Visual Studio Code :

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -WhatIf
```

Lire le résultat. Aucune ressource ne doit être créée avec `-WhatIf`.

Vérifier le nom du workspace et le nom du Lakehouse. S'ils sont incorrects,
modifier `config\client.parameters.yaml`, revalider le fichier, puis relancer
la prévisualisation.

## 23. Créer ou retrouver le workspace et le Lakehouse

Dans le terminal :

```powershell
.\scripts\deploy.ps1 `
  -ConfigurationPath .\config\client.parameters.yaml `
  -CreateWorkspace
```

Le script affiche un plan JSON et les identifiants trouvés. Il ne téléverse pas
les fichiers et ne publie pas les rapports.

Dans le portail Fabric :

1. Cliquer sur **Espaces de travail** (**Workspaces**) dans la navigation de
   gauche.
2. Rechercher le nom configuré, par défaut `Fabric Administration`.
3. Ouvrir le workspace.
4. Vérifier qu'un Lakehouse nommé `FabricSRE` est présent.

S'il existe plusieurs workspaces portant ce nom, arrêter et demander à
l'administrateur de supprimer l'ambiguïté.

## 24. Affecter le workspace à une capacité

Dans le workspace Fabric :

1. Cliquer sur **Paramètres du workspace** (**Workspace settings**).
2. Ouvrir **Type de workspace** (**Workspace type**).
3. Cliquer sur **Modifier** (**Edit**).
4. Choisir un type de workspace Fabric.
5. Sélectionner exactement la capacité indiquée dans la fiche.
6. Cliquer sur **Appliquer**.
7. Attendre la confirmation.

> **Point de contrôle**
>
> Le nom de la capacité affiché doit être exactement celui approuvé. Une
> capacité d'essai ne doit pas être utilisée pour la production.

## 25. Créer l'identité du workspace

Dans **Paramètres du workspace** :

1. Ouvrir **Identité du workspace** (**Workspace identity**).
2. Cliquer sur **Créer une identité**.
3. Confirmer.
4. Attendre que l'état indique que l'identité est prête.
5. Copier le nom de l'identité dans la fiche de déploiement.

Ensuite :

1. Revenir au workspace.
2. Cliquer sur **Gérer l'accès** (**Manage access**).
3. Ajouter l'identité utilisée pour la collecte ou l'automatisation.
4. Attribuer **Contributeur** uniquement si cette identité doit exécuter et
   modifier les notebooks et le pipeline.
5. Donner seulement **Lecture** et **Build** aux identités qui consomment le
   modèle.

Ne pas attribuer **Contributeur** à l'identité de lecture de l'agent.

## 26. Téléverser les fichiers dans le Lakehouse

### 26.1 Arborescence attendue

Le résultat doit être :

```text
Files/
└── fabric-sre/
    ├── config/
    │   ├── client.parameters.yaml
    │   └── client.parameters.schema.json
    ├── src/
    │   └── fabric_sre/
    │       └── fichiers Python du paquet
    └── queries/
        └── capacity-metrics/
            ├── silver_item_cu.dax
            └── silver_storage.dax
```

Le fichier `client.parameters.schema.json` est obligatoire : les notebooks
l'utilisent pour valider la configuration.

### 26.2 Créer les dossiers

Dans le portail Fabric :

1. Ouvrir le Lakehouse `FabricSRE`.
2. Dans l'explorateur du Lakehouse, ouvrir **Files**.
3. Cliquer sur les trois points `...` à côté de **Files**.
4. Choisir **Nouveau sous-dossier**.
5. Créer `fabric-sre`.
6. Dans `fabric-sre`, créer `config`, `src` et `queries`.
7. Dans `src`, créer `fabric_sre`.
8. Dans `queries`, créer `capacity-metrics`.

### 26.3 Téléverser les fichiers

Pour chaque dossier :

1. Ouvrir le dossier cible dans le Lakehouse.
2. Cliquer sur **Téléverser** (**Upload**).
3. Choisir **Téléverser des fichiers**.
4. Sélectionner les fichiers du dossier local correspondant.
5. Attendre la fin de l'envoi.
6. Vérifier que tous les noms sont visibles.

Ne pas téléverser le dépôt complet et ne pas téléverser `.git`,
`client.parameters.example.yaml`, les caches ou les tests.

## 27. Créer les six notebooks

Les fichiers du dossier local `notebooks` sont des sources, pas des notebooks
Fabric exportés. Pour cette version du projet, créer les notebooks dans le
portail et copier leur contenu.

### 27.1 Procédure commune

Pour chaque notebook :

1. Ouvrir le workspace `Fabric Administration`.
2. Cliquer sur **+ Nouvel élément** (**+ New item**).
3. Rechercher `Notebook`.
4. Cliquer sur **Notebook**.
5. Renommer le notebook avec le nom exact indiqué ci-dessous, sans extension.
6. Dans l'explorateur du notebook, cliquer sur **Ajouter un Lakehouse**.
7. Choisir **Lakehouse existant**.
8. Sélectionner `FabricSRE`.
9. Confirmer que `FabricSRE` est le Lakehouse par défaut.
10. Ouvrir le fichier source correspondant dans Visual Studio Code.
11. Copier tout son contenu.
12. Coller le contenu dans la première cellule du notebook.
13. Enregistrer le notebook.

### 27.2 Notebooks Python

Créer :

| Nom du notebook Fabric | Fichier source local | Langage de la cellule |
|---|---|---|
| `01_collect_inventory` | `notebooks\01_collect_inventory.py` | PySpark (Python) |
| `02_collect_activity_events` | `notebooks\02_collect_activity_events.py` | PySpark (Python) |
| `03_collect_capacity_metrics` | `notebooks\03_collect_capacity_metrics.py` | PySpark (Python) |

### 27.3 Notebooks SQL

Créer :

| Nom du notebook Fabric | Fichier source local | Langage de la cellule |
|---|---|---|
| `00_bootstrap_lakehouse` | `notebooks\00_bootstrap_lakehouse.sql` | Spark SQL |
| `04_normalize_inventory` | `notebooks\04_normalize_inventory.sql` | Spark SQL |
| `05_build_gold` | `notebooks\05_build_gold.sql` | Spark SQL |

Pour changer le langage d'une cellule :

1. Cliquer dans la cellule.
2. Ouvrir la liste de langage dans la barre de la cellule.
3. Choisir **Spark SQL**.

Ne pas choisir le point de terminaison SQL du Lakehouse : ces requêtes créent
des tables Delta et doivent être exécutées par Spark.

## 28. Exécuter l'amorçage

1. Ouvrir `00_bootstrap_lakehouse`.
2. Confirmer que le Lakehouse `FabricSRE` est attaché.
3. Cliquer sur **Exécuter tout** (**Run all**).
4. Attendre la coche verte.
5. Revenir au Lakehouse.
6. Dans **Tables**, cliquer sur **Actualiser**.

Les tables Bronze, Silver et `collection_run` doivent apparaître.

Si le notebook échoue, ne pas poursuivre avec les autres notebooks.

## 29. Créer le pipeline quotidien

Le fichier
`pipelines\daily-collection.pipeline.template.json` décrit le pipeline attendu,
mais n'est pas un export Fabric à importer directement. Créer le pipeline dans
l'interface.

### 29.1 Créer le pipeline

1. Dans le workspace, cliquer sur **+ Nouvel élément**.
2. Rechercher `Pipeline de données` (**Data pipeline**).
3. Cliquer sur **Pipeline de données**.
4. Saisir `pl_fabric_sre_daily`.
5. Cliquer sur **Créer**.

### 29.2 Ajouter une activité Notebook

Pour chaque ligne du tableau suivant :

1. Dans le volet **Activités**, rechercher **Notebook**.
2. Faire glisser **Notebook** sur le canevas.
3. Sélectionner l'activité.
4. Dans l'onglet **Général**, saisir le nom de l'activité.
5. Dans l'onglet **Paramètres** (**Settings**), choisir l'authentification
   **Identité du workspace** si elle est proposée et approuvée.
6. Dans **Notebook**, sélectionner le notebook indiqué.

| Activité | Notebook |
|---|---|
| `Bootstrap Lakehouse` | `00_bootstrap_lakehouse` |
| `Collect Inventory` | `01_collect_inventory` |
| `Collect Activity` | `02_collect_activity_events` |
| `Collect Capacity Metrics` | `03_collect_capacity_metrics` |
| `Normalize Inventory` | `04_normalize_inventory` |
| `Build Gold` | `05_build_gold` |

### 29.3 Relier les activités

Utiliser la dépendance verte **Réussite** (**Succeeded**) :

1. `Bootstrap Lakehouse` vers `Collect Inventory`;
2. `Bootstrap Lakehouse` vers `Collect Activity`;
3. `Bootstrap Lakehouse` vers `Collect Capacity Metrics`;
4. `Collect Inventory` vers `Normalize Inventory`;
5. `Normalize Inventory` vers `Build Gold`;
6. `Collect Activity` vers `Build Gold`;
7. `Collect Capacity Metrics` vers `Build Gold`.

Le pipeline doit former trois branches après l'amorçage, puis se rejoindre sur
`Build Gold`.

### 29.4 Configurer les reprises

Pour chaque activité :

1. Sélectionner l'activité.
2. Ouvrir les paramètres généraux ou la stratégie d'exécution.
3. Définir **Nombre de nouvelles tentatives** (**Retry**) à `3`.
4. Définir l'intervalle à `120` secondes.
5. Définir le délai maximal à `2` heures lorsque ce champ est disponible.

### 29.5 Enregistrer

Dans l'onglet **Accueil** (**Home**) du pipeline :

1. Cliquer sur **Enregistrer**.
2. Attendre la confirmation.

## 30. Tester le pipeline

1. Dans le pipeline, cliquer sur **Exécuter** (**Run**).
2. Confirmer l'exécution.
3. Ouvrir l'onglet **Sortie** (**Output**) sous le canevas.
4. Attendre la fin de toutes les activités.
5. Cliquer sur chaque activité pour consulter son résultat.

Toutes les activités doivent être vertes.

Ensuite, dans le Lakehouse :

1. Actualiser **Tables**.
2. Vérifier la présence de tables commençant par `bronze_`, `silver_` et
   `gold_`.
3. Ouvrir `gold_capacity_daily`.
4. Vérifier qu'elle contient des lignes si Capacity Metrics est activé et
   disponible.
5. Ouvrir `gold_item_daily`.
6. Vérifier que les identifiants attendus ne sont pas vides.

Un pipeline indiqué comme réussi avec des tables Gold vides n'est pas une
recette réussie.

## 31. Planifier le pipeline

Dans l'éditeur du pipeline :

1. Cliquer sur **Accueil**.
2. Cliquer sur **Planifier** (**Schedule**).
3. Cliquer sur **Ajouter une planification** si nécessaire.
4. Choisir une fréquence **Quotidienne**.
5. Définir l'heure locale approuvée, par défaut `01:00`.
6. Vérifier le fuseau horaire.
7. Activer la planification.
8. Enregistrer.

Dans l'historique des exécutions, confirmer que la prochaine occurrence est
affichée.

## 32. Publier le modèle et les rapports Power BI

### 32.1 Récupérer le serveur SQL du Lakehouse

Dans le portail Fabric :

1. Ouvrir le Lakehouse `FabricSRE`.
2. Ouvrir **Point de terminaison d'analytique SQL**
   (**SQL analytics endpoint**).
3. Ouvrir les paramètres ou l'action de copie de la chaîne de connexion.
4. Copier le nom du serveur se terminant par
   `.datawarehouse.fabric.microsoft.com`.
5. Noter `FabricSRE` comme nom de base de données, sauf si le Lakehouse a été
   renommé.

### 32.2 Ouvrir le projet français

Sur le poste :

1. Dans l'Explorateur Windows, ouvrir
   `powerbi\FabricSRE\fr`.
2. Double-cliquer sur `FabricSRE-fr.pbip`.
3. Attendre l'ouverture de Power BI Desktop.
4. Si Power BI demande d'activer la fonctionnalité PBIP, accepter puis
   redémarrer Power BI Desktop.

### 32.3 Modifier les paramètres

Dans Power BI Desktop :

1. Dans le ruban **Accueil**, cliquer sur **Transformer les données**.
2. Cliquer sur **Modifier les paramètres** (**Edit parameters**).
3. Pour `Server`, coller le serveur SQL relevé à l'étape 32.1.
4. Pour `Database`, saisir le nom du Lakehouse.
5. Valider.
6. Cliquer sur **Actualiser**.
7. S'authentifier avec le compte professionnel si demandé.
8. Vérifier qu'aucune erreur de source n'est affichée.
9. Enregistrer le projet.

### 32.4 Publier en français

1. Dans le ruban **Accueil**, cliquer sur **Publier** (**Publish**).
2. Choisir le workspace `Fabric Administration`.
3. Confirmer.
4. Attendre le message de réussite.

### 32.5 Publier en anglais

1. Fermer le projet français.
2. Ouvrir
   `powerbi\FabricSRE\en\FabricSRE-en.pbip`.
3. Vérifier les paramètres `Server` et `Database`.
4. Actualiser.
5. Publier dans le même workspace.

Dans le workspace, vérifier la présence :

- du modèle sémantique `Fabric SRE`;
- du rapport français;
- du rapport anglais.

Si Power BI propose de remplacer un modèle existant, vérifier que le modèle
cible est bien `Fabric SRE` dans le workspace d'administration avant
d'accepter.

### 32.6 Configurer la connexion cloud

Dans le portail Fabric :

1. Dans le workspace, repérer le modèle sémantique `Fabric SRE`.
2. Cliquer sur les trois points `...`.
3. Cliquer sur **Paramètres**.
4. Ouvrir **Connexions de passerelle et cloud**
   (**Gateway and cloud connections**).
5. Sous **Connexions cloud**, ouvrir **Maps to**.
6. Choisir **Créer une connexion**.
7. Sélectionner l'authentification par **Identité du workspace** si elle est
   disponible.
8. Sélectionner l'identité du workspace `Fabric Administration`.
9. Enregistrer.

### 32.7 Actualiser le modèle

1. Revenir au modèle sémantique.
2. Cliquer sur les trois points `...`.
3. Cliquer sur **Actualiser maintenant** (**Refresh now**).
4. Ouvrir **Historique d'actualisation**.
5. Vérifier que l'état final est **Terminé** (**Completed**).

### 32.8 Vérifier les rapports

Ouvrir les deux rapports.

Vérifier :

- [ ] les pages s'ouvrent sans erreur;
- [ ] les cartes et graphiques contiennent des données;
- [ ] les totaux français et anglais correspondent;
- [ ] la date de fraîcheur est cohérente avec la dernière collecte;
- [ ] les filtres utilisent les mêmes périodes;
- [ ] aucun identifiant technique sensible n'est exposé inutilement.

## 33. Recette Advanced

Tous les contrôles Basic doivent déjà être réussis.

Vérifier ensuite :

- [ ] le workspace est sur la capacité approuvée;
- [ ] l'identité du workspace est active;
- [ ] les fichiers sont présents sous `Files/fabric-sre`;
- [ ] les six notebooks sont attachés au Lakehouse;
- [ ] l'amorçage crée les tables attendues;
- [ ] une exécution complète du pipeline réussit;
- [ ] les tables Bronze contiennent la collecte brute;
- [ ] les tables Silver contiennent des données normalisées;
- [ ] les tables Gold contiennent des lignes exploitables;
- [ ] la planification quotidienne est active;
- [ ] le modèle sémantique s'actualise;
- [ ] les deux rapports affichent les mêmes totaux;
- [ ] l'agent utilise Gold pour l'historique et les outils directs pour le temps
  réel;
- [ ] aucune action d'écriture ne s'exécute sans approbation humaine.

# Clôture et exploitation

## 34. Clôture du déploiement

Consigner, sans secret :

- l'édition installée;
- la date et l'heure;
- le compte nominatif de l'installateur;
- les noms des ressources;
- les URL du portail et de santé;
- l'heure de la planification;
- le résultat de la recette;
- les erreurs résolues;
- les actions restantes et leur propriétaire.

Ne pas consigner :

- la valeur de `x-api-key`;
- le secret de l'application Entra;
- des jetons Azure;
- des chaînes de connexion contenant un secret.

## 35. Sécuriser après l'installation

1. Vérifier que `config\client.parameters.yaml` n'est pas ajouté à Git.
2. Fermer le terminal qui contient les variables d'environnement.
3. Fermer toute fenêtre qui affiche un secret.
4. Vérifier la date d'expiration du secret de l'application Entra.
5. Créer un rappel de rotation avant un an.
6. Vérifier que la Container App conserve au moins un réplica si le client
   exige une réponse sans démarrage à froid.
7. Vérifier que les identités de lecture n'ont pas le rôle Contributor.

## 36. Surveillance quotidienne

Dans Fabric :

1. Ouvrir le workspace.
2. Ouvrir le pipeline `pl_fabric_sre_daily`.
3. Ouvrir l'historique.
4. Confirmer que la dernière exécution est réussie.
5. Vérifier la date la plus récente dans les tables Gold.

Dans Azure :

1. Ouvrir la Container App.
2. Vérifier que la révision active est saine.
3. Consulter les journaux en cas de réponse lente ou d'erreur.

Dans Power BI :

1. Ouvrir l'historique d'actualisation du modèle.
2. Vérifier la dernière actualisation.
3. Ouvrir les deux rapports après toute modification du modèle.

## 37. Dépannage guidé

### Le script ne voit pas l'abonnement

1. Exécuter `az account show --output table`.
2. Comparer l'abonnement et le tenant avec la fiche.
3. Relancer `az login --tenant "<ID-DU-TENANT>"`.
4. Relancer `az account set --subscription "<ID-ABONNEMENT>"`.

### Le script ne trouve pas l'identité managée

1. Ouvrir **Identités managées** dans Azure.
2. Vérifier le nom, le groupe de ressources et l'abonnement.
3. Corriger la configuration ou créer l'identité manquante.
4. Ne pas remplacer le nom par l'ID client.

### Fabric Admin retourne 401 ou 403

1. Vérifier les deux paramètres du tenant Fabric.
2. Vérifier que le bon groupe de sécurité est sélectionné.
3. Dans Entra, ouvrir le groupe et vérifier que le principal de service Fabric
   Admin est membre.
4. Attendre la propagation.
5. Ne pas donner Contributor sur tous les workspaces pour contourner l'erreur.

### La page `/health` ne répond pas

1. Ouvrir la Container App.
2. Vérifier la révision active.
3. Vérifier qu'un réplica est prêt.
4. Ouvrir le flux de journaux.
5. Faire analyser l'erreur de démarrage.

### Le notebook ne trouve pas `fabric_sre`

1. Ouvrir le Lakehouse.
2. Vérifier
   `Files/fabric-sre/src/fabric_sre`.
3. Vérifier que les fichiers Python du paquet sont directement dans ce dossier.
4. Ne pas ajouter un niveau de dossier `src` supplémentaire.

### Le notebook ne trouve pas la configuration

Vérifier la présence exacte de :

```text
Files/fabric-sre/config/client.parameters.yaml
Files/fabric-sre/config/client.parameters.schema.json
```

### Capacity Metrics est vide

1. Vérifier que `collectCapacityMetrics` vaut `true`.
2. Vérifier `fabric.capacityMetrics.semanticModelId`.
3. Vérifier les droits **Read** et **Build** sur le modèle Capacity Metrics.
4. Vérifier que l'application Capacity Metrics a été actualisée.
5. Ne pas interpréter l'absence de données comme zéro CU.

### Le pipeline réussit mais Gold est vide

1. Ouvrir le résultat de chaque notebook.
2. Vérifier le nombre de lignes collectées.
3. Vérifier les tables Silver.
4. Vérifier les requêtes DAX sous
   `Files/fabric-sre/queries/capacity-metrics`.
5. Escalader à l'équipe technique avec le nom de l'activité et l'heure
   d'exécution.

### L'actualisation Power BI échoue

1. Vérifier `Server` et `Database`.
2. Vérifier la connexion cloud du modèle.
3. Vérifier l'identité du workspace.
4. Vérifier les droits de cette identité.
5. Ouvrir le détail de l'erreur dans l'historique d'actualisation.

### Un message 429 apparaît

Le service a demandé de ralentir les appels.

1. Ne pas relancer immédiatement plusieurs fois.
2. Laisser la stratégie de reprise respecter `Retry-After`.
3. Vérifier qu'une seule planification quotidienne est active.

## 38. Retour arrière

### Basic

Pour désactiver Basic sans supprimer les ressources :

1. Désactiver les routines.
2. Retirer le connecteur `FabricAdmin` de l'agent.
3. Conserver les journaux nécessaires à l'audit.
4. Arrêter la Container App seulement après validation du responsable.

### Advanced

Pour désactiver Advanced sans perdre les données :

1. Désactiver la planification du pipeline.
2. Désactiver les actualisations du modèle.
3. Exporter les données requises pour l'audit.
4. Retirer les liens vers les rapports.
5. Revenir au fonctionnement Basic.

Ne jamais supprimer le workspace pour résoudre un problème de pipeline.

## 39. Documentation Microsoft officielle

- [Créer et configurer Azure SRE Agent](https://learn.microsoft.com/azure/sre-agent/create-and-set-up)
- [Configurer un connecteur MCP dans Azure SRE Agent](https://learn.microsoft.com/azure/sre-agent/mcp-connector)
- [Gérer Azure SRE Agent avec Azure MCP Server](https://learn.microsoft.com/azure/developer/azure-mcp-server/tools/azure-sre-agent)
- [Créer un workspace Fabric](https://learn.microsoft.com/fabric/fundamentals/create-workspaces)
- [Créer un Lakehouse](https://learn.microsoft.com/fabric/data-engineering/create-lakehouse)
- [Utiliser les notebooks Fabric](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)
- [Ajouter une activité Notebook à un pipeline](https://learn.microsoft.com/fabric/data-factory/notebook-activity)
- [Paramètres des API d'administration Fabric](https://learn.microsoft.com/fabric/admin/service-admin-portal-admin-api-settings)
- [Autoriser un principal de service pour les API d'administration](https://learn.microsoft.com/fabric/admin/enable-service-principal-admin-apis)
- [Projets Power BI Desktop PBIP](https://learn.microsoft.com/power-bi/developer/projects/projects-overview)
- [Configurer une connexion cloud Power BI](https://learn.microsoft.com/power-bi/connect-data/service-connect-cloud-data-sources)
- [Authentification par identité de workspace](https://learn.microsoft.com/fabric/security/workspace-identity-authenticate)
