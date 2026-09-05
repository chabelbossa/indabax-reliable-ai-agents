# Guide animateur : mission KoraCare

50 minutes, niveau intermédiaire, français prioritaire. Le deck anglais suit les mêmes
vingt slides et les notebooks ont les mêmes dix TODO. Les notes PowerPoint donnent les
questions et les transitions de chaque slide.

## Comment utiliser le deck pendant l'atelier

Ne pas présenter les vingt slides puis ouvrir le notebook. Le deck et le notebook
avancent ensemble :

1. slides 1–10 : ouverture, concepts et briefing de la mission ;
2. slide 11, puis notebook : TODO 1–2 ;
3. slide 12, puis notebook : TODO 3–6 ;
4. slide 13, puis notebook : TODO 7–9 et mission Gemini ;
5. slide 14 pendant le checkpoint 3 : réponse fautive et vote de la salle ;
   slide 15 au début des évaluations : résultat attendu et résultat observé ;
6. slide 16, puis notebook : TODO 10, évaluations et dossier ;
7. slide 17 : vérifier qu’un test détecte une protection retirée ;
   slides 18–20 : dossier obtenu, ressources et question de transfert.

Chaque page « DANS LE NOTEBOOK » annonce le checkpoint, puis peut rester affichée
pendant le travail. Revenir au notebook pour coder et exécuter ; revenir au deck pour
les transitions, les votes et la synthèse.

## Avant l'entrée des participants

- Ouvrir le deck français, le notebook participant FR et la solution FR.
- Faire ouvrir le notebook et préparer la clé avant le début si possible. Former des binômes
  avec un rôle Modèle et un rôle Orchestrateur ; une clé par binôme suffit.
- Préparer aussi une solution exécutée en mock. Ce secours ne dépend pas de Gemini ;
  le premier lancement Colab et l'installation des dépendances nécessitent Internet.
- Exécuter `python scripts/smoke_gemini.py` avec la clé dans l'environnement : les six
  contrôles doivent passer. Ce script exécute les définitions du notebook solution.
- Repérer la slide 6 (appel et résultat), la slide 7 (boucle) et la slide 14
  (conclusion sans approbation). Elles expliquent le mécanisme avec le même incident.
- Garder le QR du dépôt visible avant le démarrage. Les participants n'ont rien à installer
  sur leur ordinateur s'ils utilisent Colab.

## 0–4 min : comparer les usages (slides 1–4)

« Qui a utilisé ChatGPT en 2022 ? Qui l'utilise en 2026 ? Quelles tâches lui confiez-vous
aujourd'hui que vous ne lui confiiez pas alors ? »

Faire un vote à main levée pour chaque année, puis prendre deux réponses de vingt secondes.
On compare les usages ; on ne demande pas qui a créé ChatGPT. Ne pas supposer que tout le
monde utilisait déjà le produit en 2022. La slide 3 pose la question des informations et
outils nécessaires à ces nouveaux usages. La slide 4 introduit ensuite l’alerte KoraCare,
le rôle de l’équipe et le dossier attendu. Expliquer que données et opérateur sont simulés.

## 4–10 min : du modèle à l'agent (slides 5–10)

La slide 5 distingue le modèle de l’application qui exécute les outils. L’agent est
l’application dans laquelle le modèle choisit certaines étapes selon les observations.
Comparer brièvement avec un workflow dont les étapes sont fixées par le code.

Sur la slide 6, faire identifier le nom de la fonction, l’argument et le résultat obtenu.
L’appel affiché est une représentation normalisée du `ToolCall`, pas le format réseau
brut de Gemini. Suivre les flèches de la slide 7, puis lire les deux tours de la slide 8 :
mesure reçue, retour dans l’historique, recherche de la procédure. Demander pourquoi
le modèle a besoin de recevoir le résultat pour décider de la suite.

La slide 9 relie chaque outil à une question de la mission. Les fonctions sont fournies.
La slide 10 présente les trois erreurs qui seront provoquées dans le notebook.

## 10–14 min : ouvrir le notebook (slide 10, puis slide 11)

« Il est 09:42. La clinique KCARE-ADJ-01 signale 12,4°C depuis 52 minutes.
Votre équipe doit préparer un dossier et une décision justifiée. »

Faire choisir la première action : consulter la mesure contrôlée ou demander directement
au modèle si le stock est sûr ? « Défendez votre choix auprès de votre binôme. »

La mission est déjà présentée. Question de vérification : « À quel moment sait-on que
la mesure a été lue ? » Réponse : quand l’outil a retourné son résultat, pas au moment de
la proposition. Retrouver les cinq outils dans le notebook comme une référence.
Toutes les données, les procédures et l'opérateur sont simulés. Les règles ne constituent
pas un protocole médical ; aucune action physique n'est exécutée.

Faire exécuter le setup. Cette plage inclut le dépannage. En cas de blocage, choisir le
mock immédiatement et utiliser le poste du binôme. Un changement de clé n'est pas le
plan de secours : les clés d'un même projet partagent les quotas.

## 14–22 min : checkpoint 1, proposer (slide 11)

TODO 1–2 : compléter l'appel du client et sélectionner le premier outil.
Avant l'exécution, chacun prédit le nom, les arguments et l'information recherchée.
La prévisualisation est explicitement en mock. La mission complète sera en Gemini.

Acceptation : `get_clinic_status` avec `clinic_id=KCARE-ADJ-01`, puis explication de
la différence entre l'appel et le résultat. À 22 minutes, fournir la solution si nécessaire.

## 22–31 min : checkpoint 2, exécuter et observer (slide 12)

TODO 3–6 : exécuter avec le contrôle de provenance, enregistrer le résultat réel dans
la structure de trace fournie, ajouter la proposition assistant puis l'observation tool.

Masquer la réponse finale. Faire raconter le premier appel uniquement à partir de la trace.
Acceptation : l'observation contient la valeur retournée par l'outil et l'identité de l'appel.
Si l'on dépasse de deux minutes, donner le code de ce checkpoint et poursuivre.

## 31–41 min : checkpoint 3 et contre-exemple (slides 13–14)

Échanger les rôles. Afficher la slide 14 et faire voter avant de commenter la trace.
Avant TODO 7–8, exécuter le client adverse qui conclut après le calcul du risque ;
sa réponse n’est pas autorisée. Aucun dossier ni accord n’existe. Demander quelle preuve manque.
Compléter TODO 7–9 : obligation de revue, approbation liée au bon incident et à la bonne
action, arrêt d'un appel répété. Réexécuter les cellules de définition après modification.

Lancer la mission complète Gemini une fois les protections ajoutées. Puis relancer le client
adverse, qui doit donner `review_required`. Le binôme choisit une autre panne dans la cellule
« Votre contre-exemple » : mesure altérée, approbation rejetée ou répétition.

Acceptation : l'agent s'arrête pour une raison que le binôme retrouve dans les preuves.
La timeline se révèle après le run ; ne pas demander de prédire chaque étape pendant un
affichage qui arrive d'un seul bloc. Faire prédire avant l'exécution, puis comparer.

Si une protection est corrigée après la mission, relancer sa cellule `mission_run = ...`
avant les évaluations : un objet déjà calculé ne se met pas à jour tout seul.

## 41–46 min : checkpoint 4, évaluer (slides 15–17)

La slide 15 compare quatre résultats attendus et observés de la solution. La colonne
de statut ne résume pas toutes les vérifications : les tests contrôlent aussi la séquence,
la revue, la trace et la réponse. TODO 10 : exiger toutes les conditions avec `all(row["checks"].values())`.
Lancer les dix scénarios sans API : trois chemins métier et sept erreurs volontaires.
Lire au moins le cas d'approbation absente et celui d'appel répété.

Un test PASS peut signifier que l'agent a correctement refusé de continuer. Retirer le
garde anti-répétition fait échouer son scénario ; retirer le contrôle humain fait échouer
les scénarios concernés. La slide 17 montre cette comparaison. Si le temps permet de la
reproduire, restaurer le contrôle et relancer les définitions puis les évaluations.
Le score couvre uniquement les cas testés. Les cinq minutes du checkpoint incluent
la lecture des slides et des résultats ; elles ne s’ajoutent pas aux cinq minutes de l’agenda.

## 46–50 min : dossier et transfert (slides 18–20)

La slide 18 représente un extrait abrégé du dossier produit en mode mock. Ce n’est pas
une capture d’un appel Gemini. Montrer ensuite le dossier de la session et son champ `mode`.
Télécharger le dossier JSON : faits, appels, décision simulée, évaluations et panne choisie.
Chaque binôme explique la protection illustrée par son expérience. Une capture est facultative.

Prendre deux réponses à : « Quelle règle testeriez-vous dans votre propre métier ? »
Réponse attendue : une règle précise et un cas où elle doit bloquer, pas seulement un nom d'outil.
Ne pas présenter le dossier comme la preuve qu'un réfrigérateur a été réparé.

## Secours explicite, en moins d'une minute

1. Annoncer : « L'API est indisponible ; nous passons au simulateur déterministe. »
2. Dans le setup du notebook, remplacer la ligne `MODE = ...` par `MODE = "mock"`.
3. Relancer le setup, la mission, l'expérience choisie et les évaluations. Le clone est réutilisé.
4. Ne jamais présenter les sorties mock comme des décisions Gemini en direct.

En cas de panne totale de réseau, utiliser le notebook solution local déjà exécuté ou
partager le poste d'un binôme. Le mock supprime la dépendance API, pas l'accès initial à Colab.

## Parcours compressé, 35 minutes

- 0–4 : usages et boucle.
- 4–8 : mission, choix de première action et ouverture.
- 8–14 : TODO 1–2 ; donner la solution TODO 3–6 et lire une trace.
- 14–26 : TODO 7–9, mission et contre-exemple.
- 26–31 : TODO 10 et lecture de trois scénarios représentatifs.
- 31–35 : dossier et question de transfert.

## Répétition humaine à effectuer avant l'atelier

- Une personne suit les TODO sans connaître les solutions ; l'animateur suit ce guide.
- Le parcours tient en 50 minutes ; sinon fournir davantage de code répétitif.
- Le passage Gemini → mock prend moins d'une minute dans le notebook.
- La personne explique qui propose, qui exécute et pourquoi un résultat est refusé.
- Le JSON est téléchargé et la panne choisie peut être expliquée.

Les tests automatisés et l'exécution Gemini ne remplacent pas cette répétition.
