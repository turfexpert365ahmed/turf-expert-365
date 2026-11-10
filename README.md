# TURF EXPERT 365 — prototype de serveur

Prototype de consultation des réunions, courses et partants avec un classement **heuristique** (pas une IA entraînée). Les données sont demandées au service PMU au moment de l'affichage ; **la disponibilité, les droits d'utilisation et la stabilité de cet accès ne sont pas garantis**. Aucun résultat n'est inventé en cas d'échec.

## Déploiement Render
1. Mettre les fichiers de ce dossier à la racine d'un dépôt GitHub.
2. Render > New Web Service > Git Provider > connecter le dépôt.
3. Utiliser la configuration `render.yaml` ou choisir Python, build `pip install -r requirements.txt`, start `gunicorn app:app --bind 0.0.0.0:$PORT`, plan Free si disponible.
4. Ouvrir l'URL fournie par Render et tester le chargement des réunions. L'accès aux données peut échouer côté serveur.

Ne pas promettre d'analyse pedigree, terrain, chronos, cotes ou fiabilité des pronostics : ces données ne sont pas intégrées dans ce prototype.
