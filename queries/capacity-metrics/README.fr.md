# Adaptateur Capacity Metrics

Déposez ici les requêtes DAX validées contre **la version installée** du modèle
sémantique Fabric Capacity Metrics. Chaque fichier `nom_table.dax` produit une
table Delta `nom_table`.

Le modèle de l'application peut évoluer sans contrat de schéma public. Le
déploiement exécute donc un contrôle de schéma avant d'activer la collecte et
échoue explicitement si une colonne attendue manque. Ne masquez pas cette
erreur par une valeur vide.

