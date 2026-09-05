# Validation de la livraison : 4 septembre 2026

## Résultats observés

| Contrôle | Résultat | Portée |
|---|---|---|
| `python -m pytest -q` | 37 tests réussis | Runtime, erreurs Gemini, preuves, régressions et contrats des supports |
| `python -m evals.run_evals` | 10/10 | Trois cas opérationnels et sept cas adverses déterministes |
| Quatre notebooks FR/EN | Exécutés sans erreur en noyaux locaux frais | Mode mock explicite ; notebooks participants volontairement incomplets |
| Gemini réel | Six critères du smoke test réussis | Runtime de la solution FR sauvegardée, cinq outils, zéro erreur, incident escaladé |
| Solution FR dans Colab | 16 cellules de code exécutées, dont une préparation de validation | Python 3.13 ; archive locale importée ; mode mock ; 10/10 ; tableau de bord et lien de dossier affichés |
| Présentations | 20 diapositives par langue, notes incluses | 40 pages PDF rendues et inspectées ; structure et identité du template original conservées |

Le test Gemini a utilisé `gemini-3.7-flash` et produit `RUN-F96BE6CC`,
`outcome=escalated`, `safety_status=human_approved`. La clé n'est ni enregistrée
dans les supports ni incluse dans l'archive. L'identifiant du run est dérivé de
la question ; il ne distingue pas à lui seul une exécution mock d'une exécution
Gemini. Toujours lire le champ `mode`.

La validation Colab a été effectuée dans une copie Drive privée nommée
« VALIDATION KoraCare final FR : archive locale.ipynb ». Une cellule réservée au
test extrait l'archive et active explicitement le mock. Elle ne fait pas partie
des notebooks livrés. Le premier lancement de test avait précédé la fin du
transfert ZIP et a échoué ; après transfert complet et redémarrage du runtime,
l'exécution complète a réussi. Les résultats Colab décrivent cette seconde
exécution, pas les sorties préenregistrées. Le lien JSON a été activé ; la
réception du fichier dans le dossier de téléchargements n'a pas été vérifiée.

## Ce qui protège le parcours

- Une mesure altérée est rejetée avant l'évaluation du risque.
- Une réponse sans preuves ne devient pas un résultat sûr.
- L'approbation doit concerner le bon incident et la bonne action.
- Une approbation absente ou refusée ne clôture pas l'incident.
- Un appel identique répété et les erreurs fournisseur arrêtent le parcours.
- Les tests de mutation montrent que retirer la protection anti-répétition ou
  accepter une approbation absente fait échouer les évaluations concernées.
- Le mock reste annoncé : aucune substitution silencieuse à Gemini.

## Vérifications encore distinctes

### Révision pédagogique des présentations

Les decks français et anglais ont été réécrits après la revue éditoriale : mission
expliquée avant le code, appel et résultat comparés, boucle dessinée, deux tours
illustrés, contre-exemple avec approbation manquante, évaluations attendues/observées
et extrait du dossier obtenu. Les consignes d’animation restent dans les notes.
Le guide animateur suit le nouvel ordre des vingt slides.

Vérifications effectuées sur cette révision : 37 tests réussis ; vingt slides et notes
par langue ; aucun doublon de fichier dans les PowerPoint ; quarante pages PDF
rendues et inspectées ; titres et notes conformes aux sources ; aucune forme hors
des limites des slides. Les exemples d’évaluation correspondent aux scénarios de
la solution. Le code du lab et les notebooks n’ont pas été modifiés par cette révision.

### Contrôles à compléter pour la livraison

1. **Publication** : les changements finaux sont locaux. Publier la révision
   approuvée, vérifier son SHA distant et ouvrir le lien Colab public à neuf.
   Le test avec archive ne prouve pas que GitHub sert déjà ces nouveaux fichiers.
2. **Répétition humaine** : faire les dix TODO en binôme avec chronomètre. Le
   déroulé prévoit 50 minutes, mais aucune répétition humaine chronométrée n'a
   été réalisée par l'assistant. Utiliser le parcours comprimé du runbook si besoin.
3. **Salle** : vérifier projecteur, Wi-Fi, création des clés et quota réel du
   groupe. Un appel Gemini réussi ne garantit pas la capacité simultanée.
4. **Soumission** : le message est un brouillon ; aucun email n'a été envoyé.

Les données et décisions humaines sont simulées. Le livrable est une trace et
un dossier de preuves, jamais une intervention physique ou un protocole médical.
