# Conducteur oral — parcours KoraCare révisé
Version du 10 septembre 2026 · 50 minutes · quatre TODO · slides et notebook FR/EN

## La carte à garder sous les yeux

Le fil : parler sans outils → demander un outil → lire et renvoyer son résultat →
enchaîner les outils → bloquer une conclusion non autorisée → tester.

| Temps | Écran | Ce que la salle doit voir |
| --- | --- | --- |
| 0–10 | Slides 1–10 | L'alerte, l'appel, son résultat et la boucle. |
| 10–14 | Notebook : setup et contrat | Un client prêt par binôme ; attribut mode et méthode complete distingués. |
| 14–22 | Chatbot, slide 11, TODO 1 | Une réponse sans accès aux faits, puis une proposition d'outil. |
| 22–31 | Slide 12, TODO 2 | La mesure de 12,4 °C, l'historique enrichi, puis la recherche de procédure. |
| 31–41 | Slides 13–14, TODO 3 | Même faute avant/après, puis mission complète et contre-exemple choisi. |
| 41–46 | Slides 15–16, TODO 4 | Mini-test puis dix scénarios ; expliquer un refus qui vaut PASS. |
| 46–50 | Dossier, slides 18–20 | Une décision reliée à une preuve ; une règle transférable à leur métier. |

La slide 17 est facultative. À 22 minutes, donne la correction du TODO 1 si nécessaire.
À 31 minutes, donne celle du TODO 2. À 46 minutes, protège la conclusion.

Les slides 1–10 donnent le contexte. Ensuite : annoncer le checkpoint sur une slide,
passer au notebook, prédire, exécuter, lire le résultat, puis faire la transition.
Tu n'as pas à commenter chaque ligne des fonctions fournies.

> « Une définition prépare une fonction. La cellule suivante l'appelle et nous montre son effet. Après une correction, nous exécutons les deux. »

<!-- page -->

## Avant le début et ouverture — 0 à 14 minutes

Ouvre le deck, le notebook participant et la solution dans trois onglets. Former des binômes.
Envoie le lien participant français :
https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb

Attention : les fichiers révisés sont locaux tant que la révision n'est pas publiée.
Le lien public ne récupère pas automatiquement tes modifications locales.

> « Ouvrez le notebook dans Colab, connectez-vous et enregistrez une copie dans Drive. Nous allons avancer cellule par cellule. Vous n'avez pas besoin d'installer Python sur Windows. »

Slides 1–4 : présentation courte et vote à main levée sur leurs usages d'IA. Deux réponses suffisent.
Présente la clinique fictive : plage du lab 2–8 °C, mesure actuelle 12,4 °C, 52 minutes hors plage.
La mission est de vérifier et préparer un dossier, avec une décision d'opérateur simulée.

> « Une alerte nous donne un signal. Quel fait devons-nous aller vérifier avant de conclure ? Défendez votre choix auprès de votre binôme. »

Slides 5–10 : le modèle propose, Python contrôle et exécute, le résultat revient dans l'historique.
Insiste sur l'appel à gauche et le résultat à droite. Présente les cinq outils sans lire leur code.

À 10 minutes, passe au notebook. Le setup crée client avec make_client(MODE).
Si une clé testée est disponible, garder Gemini. Sinon mettre MODE = "mock" et annoncer le simulateur.
Le setup clone le dépôt et installe les dépendances dans Colab : il lui faut Internet.

> « client est l'objet qui nous donne accès au modèle. complete est sa méthode pour demander un tour. mode est une étiquette qui indique Gemini ou mock. selected_client sera le nom du paramètre qui reçoit cet objet dans nos fonctions. »

Lance l'inspection : classe, mode, méthode disponible et schéma du premier outil.
Les commentaires et tableaux du notebook donnent les entrées et sorties ; la salle n'a pas à fouiller src.

<!-- page -->

## Voir le modèle agir — 14 à 31 minutes

### Chatbot et checkpoint 1 — 14 à 22 minutes

Lance « Première interaction ». En Gemini, c'est un véritable appel sans outils.
En mock, c'est un texte de secours fixe, annoncé comme tel ; il ne répond pas librement aux changements de question.

> « Ce texte peut expliquer une démarche. Où est la preuve que le capteur a été consulté ? Il n'y en a pas. Donnons maintenant au modèle les moyens de demander une mesure. »

Affiche la slide 11 puis reviens au TODO 1. Il manque seulement l'appel à
selected_client.complete(messages, TOOL_SCHEMAS). La sélection du premier outil est fournie.
Faire prédire get_clinic_status avec clinic_id = KCARE-ADJ-01.
Exécuter la définition puis sa cellule d'essai. Lire content et tool_calls.

Si Gemini propose autre chose, lis la sortie ; ne prétends pas que le résultat est imposé.
En cas d'erreur API, passe explicitement au mock et relance setup, définition et essai.
À 22 minutes, fournis la ligne de solution et demande ce qu'elle reçoit.

### Checkpoint 2 — 22 à 31 minutes

Slide 12 puis notebook. Lance la fonction d'exécution fournie et la cellule qui l'appelle.
Montre ok, data, error, puis la trace. Demande de retrouver 12,4 °C.

> « Nous avons une preuve à l'écran. Mais au prochain appel, le modèle ne verra que les messages que nous lui transmettrons. Il faut donc lui renvoyer ce résultat. »

Les messages sont déjà construits. TODO 2 ajoute assistant_message puis tool_message
à messages avec extend. Le premier conserve la proposition, le second contient l'observation.
Les conversions Pydantic sont expliquées et fournies ; elles ne sont pas à deviner.

Relancer append_observation puis la cellule suivante. Lire les rôles
system, user, assistant, tool. Observer le prochain appel : la recherche de procédure.
Le test repart d'une copie de l'historique pour éviter les doublons lors des relances.

> « Nous venons de faire deux tours à la main. La boucle fournie répète exactement ce mécanisme. Maintenant, quand doit-elle s'arrêter ? »

<!-- page -->

## La décision et sa preuve — 31 à 50 minutes

### Checkpoint 3 — 31 à 41 minutes

Échanger les rôles. Slides 13–14 : vote avant de lire la réponse.

> « Le modèle a lu les faits et le risque, mais il conclut sans approbation. Quelle preuve chercheriez-vous pour accepter sa conclusion ? »

Dans le participant, garder d'abord if False au TODO 3. Exécuter finish_with_safety,
la boucle fournie puis le contre-exemple juste dessous. Si les deux premiers TODO sont
corrects, la mauvaise conclusion est classée completed / safe.

Faire remplacer False par human_required and not human_approved.
Les booléens proviennent de inspect_evidence, dont le contrat est affiché.
Relancer la définition et le même contre-exemple : stopped / review_required.
La cellule de comparaison peut aussi montrer les deux résultats côte à côte et restaure la fonction.

> « Nous n'avons pas rendu le modèle incapable de se tromper. Nous avons ajouté une règle qui empêche cette erreur d'être acceptée. »

Lancer ensuite la mission avec le client choisi : cinq outils et human_approved attendus.
Tout résultat différent doit être lu dans la trace. La revue est simulée dans les deux modes.
Exécuter « Votre contre-exemple » au moins une fois : cette cellule crée experiment pour le dossier.

### Checkpoint 4 — 41 à 46 minutes

Slides 15–16 puis TODO 4. row contient un dictionnaire checks de booléens.
Compléter all(row["checks"].values()). Le mini-test doit afficher True puis False.
Lancer les dix scénarios déterministes. Lire au moins missing_approval et repeat.

> « Un test passe lorsque le comportement attendu est respecté. Si l'accord manque, le bon comportement est de refuser de conclure. »

La slide 17 et la manipulation anti-répétition sont facultatives.
En cas de dossier verrouillé : relancer définitions corrigées, mission, contre-exemple, évaluations.

### Conclusion — 46 à 50 minutes

Slide 18, dossier réel de la session, puis slides 19–20. Télécharger le JSON.
Faire relier une décision à ses faits et à l'approbation simulée.

> « Qui propose ? Qui exécute ? Quelle preuve autorise la suite ? Quel test vérifie le refus ? Voilà les quatre questions que vous pouvez reprendre dans vos projets. »

Prendre deux réponses à « Quelle règle testeriez-vous dans votre métier ? ».
Une exécution en simulation prouve le comportement des cas testés, pas une intervention réelle.

<!-- page -->

## Les éventualités : une décision simple à chaque fois

- Windows sans Python : Colab dans le navigateur. Aucun terminal local à préparer.
- Pas d'ordinateur ou compte Google indisponible : rejoindre un binôme prêt.
- Pas de clé ou erreur API : MODE = "mock", relancer le setup et les essais concernés.
  Ne jamais présenter les sorties mock comme des réponses Gemini.
- Réseau absent : projeter la solution HTML locale et ses sorties enregistrées.
  Le mock ne permet pas de lancer Colab sans Internet.
- Syntaxe bloquante : fournir la correction du checkpoint, puis faire expliquer la ligne.
- Une cellule semble ne rien faire : si elle définit une fonction, lancer l'essai juste après.
- Une correction ne change rien : relancer la définition, puis les cellules qui l'utilisent.
- Un résultat Gemini diffère : lire l'appel et les arguments ; utiliser le simulateur annoncé si le temps manque.
- Plusieurs évaluations rouges : vérifier les quatre TODO, sans chercher à modifier tous les fichiers src.
- Moins de temps : garder le premier appel, le retour de résultat, le vote avant/après et un test de refus.
  Le chatbot peut être montré sur ton seul poste ; l'expérience adverse supplémentaire peut être guidée.

En Gemini, le chatbot, les deux tours exploratoires et la mission utilisent l'API.
Les erreurs volontaires et les évaluations sont simulées pour rester reproductibles.
Chaque cellule ne doit donc pas appeler l'IA : chaque étape doit montrer un effet compréhensible.

Pour ta répétition : ouvre le participant, fais les quatre corrections, exécute les essais
et raconte chaque sortie en une phrase. Les tests locaux ne remplacent pas cette répétition.
