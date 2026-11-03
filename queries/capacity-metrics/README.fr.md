# Adaptateur Capacity Metrics

Déposez ici les requêtes DAX validées contre **la version installée** du modèle
sémantique Fabric Capacity Metrics. Chaque fichier `nom_table.dax` produit une
table Delta `nom_table`.

Le collecteur découvre les capacités dédiées via l'API admin à chaque collecte,
puis exécute chaque adaptateur séparément par capacité avec
`DEFINE MPARAMETER 'CapacitiesList' = {"<capacity-id>"}`. Une requête sans ce
paramètre peut ne retourner que la capacité par défaut du modèle; une liste de
plusieurs capacités peut échouer lors de la résolution de leur région.
Ne pas définir ce paramètre dans les fichiers DAX : le collecteur l'injecte,
y compris lorsqu'un adaptateur contient déjà un bloc `DEFINE`.

Les réservations Premium Per User (`PP`) sont exclues : elles ne constituent
pas une capacité dédiée pour cette source CU. Les erreurs API, résultats
tronqués et dérives de schéma font échouer la collecte explicitement; aucune
capacité en erreur n'est transformée en consommation nulle. L'identité doit
conserver les accès aux API admin en lecture seule et Read/Build sur le modèle.

Le MCP de CU récentes utilise uniquement la fenêtre de rétention du modèle
source; il ne lit pas l'historique du Lakehouse. Ses champs
`requestedCapacityIds` et `unavailableCapacityIds` indiquent les capacités
interrogées et celles sans lignes CU retournées. L'historique est accumulé par
le notebook planifié. Pour mettre à jour une installation existante, déployer
l'image MCP et téléverser `capacity_metrics.py` et `collectors.py` dans
`Files/fabric-sre/src/fabric_sre` du Lakehouse de collecte. Ne pas relancer le
notebook en ajout seul pour vérifier le déploiement : cela peut dupliquer
l'historique.

Le modèle de l'application peut évoluer sans contrat de schéma public. Le
déploiement exécute donc un contrôle de schéma avant d'activer la collecte et
échoue explicitement si une colonne attendue manque. Ne masquez pas cette
erreur par une valeur vide.
