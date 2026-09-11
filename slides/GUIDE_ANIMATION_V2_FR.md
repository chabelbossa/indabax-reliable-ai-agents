# Guide d’animation — V2 française

Parcours de 50 minutes sans saisie de code obligatoire. La pratique repose sur les prédictions, les votes et le jeu de rôles. Les pseudo-codes simplifient le programme et ne sont pas exécutables. Le seul extrait Python réel est explicitement signalé.

Avant la session : ouvrir le PDF et, si souhaité, préparer le notebook solution en mock. Garder le mode affiché. Une démo facultative remplace les deux minutes de la slide 15 ; elle ne s’ajoute pas au programme. Ne pas attendre une installation ou une clé pour commencer.

Si le groupe est à l’aise : lui faire commenter les lignes et proposer un contre-exemple. Si le groupe hésite : lire chaque ligne en français puis demander qui agit. Si le temps manque : raccourcir les interventions aux slides 12 et 16, garder les erreurs et les évaluations.

Ce que l’on envoie : PDF V2 pour tous ; lien du notebook solution pour rejouer ; notebook participant pour pratiquer ensuite. Aucun code à copier depuis les slides. Sur Windows sans Python, le parcours slides suffit ; Colab est facultatif. Hors connexion, utiliser le PDF téléchargé.

## Slide 01 — Construire des agents IA fiables

00–01 min
À dire : Aujourd’hui, on va raisonner ensemble comme les concepteurs d’un agent. Vous n’avez pas besoin de taper du code pour participer.
Question : Que faudrait-il vérifier avant de faire confiance à une réponse ?
Réponse attendue : Les données et les actions réellement exécutées.
Action : Rester sur la présentation.

## Slide 02 — Vous prenez les décisions. Nous suivons leurs effets.

01–02 min
À dire : On lit quelques lignes, vous prédisez la suite, puis on regarde le résultat. Le notebook sert à montrer le même mécanisme en Python.
Question : Faut-il installer Python pour suivre ?
Réponse attendue : Non. Slides et votes suffisent ; Colab est facultatif.
Action : Rester sur la présentation.

## Slide 03 — 09:42 : une clinique signale une hausse de température.

02–04 min
À dire : Nous jouons l’équipe de garde de KoraCare. Une alerte arrive. Nous devons enquêter avant de conclure.
Question : 12,4 °C est-il un seuil ou une mesure ?
Réponse attendue : Une mesure du capteur dans notre jeu de données fictif.
Action : Rester sur la présentation.

## Slide 04 — 12,4 °C : une mesure, pas une moyenne.

04–06 min
À dire : La valeur 12,4 est comparée à une plage, pas à une moyenne. On doit aussi regarder la durée.
Question : Pourquoi la température seule ne suffit-elle pas ?
Réponse attendue : La règle dépend aussi de la durée et de la fiabilité du capteur.
Action : Rester sur la présentation.

## Slide 05 — Trois rôles à garder en tête.

06–07 min
À dire : Gardez ces trois rôles. Quand quelque chose se passe, nous allons demander qui en est responsable.
Question : Qui lit réellement la mesure ?
Réponse attendue : La fonction exécutée par Python, sur nos données locales.
Action : Rester sur la présentation.

## Slide 06 — Commencer par une conversation.

07–09 min
À dire : On commence comme un chatbot. Nous lui avons donné une question, mais aucun moyen de consulter nos données.
Question : L’IA peut-elle vérifier le capteur ici ?
Réponse attendue : Non. Elle peut répondre, mais aucun outil ne lui donne accès au capteur.
Action : Rester sur la présentation.

## Slide 07 — Définir une fonction ne la lance pas.

09–11 min
À dire : Une cellule de définition prépare le travail. Une autre cellule doit appeler la fonction pour que quelque chose se passe.
Question : À quelle ligne le travail se fait-il ?
Réponse attendue : À mesure ← lire_clinique(...). La définition seule ne lit rien.
Action : Rester sur la présentation.

## Slide 08 — Expliquer au modèle l’outil disponible.

11–13 min
À dire : Nous devons présenter les outils au modèle, comme je dois vous présenter les fonctions avant de vous demander de les utiliser.
Question : Le modèle devine-t-il nos fonctions cachées ?
Réponse attendue : Non. L’application lui transmet explicitement leurs descriptions.
Action : Rester sur la présentation.

## Slide 09 — Avec l’outil, la réponse peut devenir une demande.

13–15 min
À dire : La nouveauté, c’est cette demande structurée. Elle sera interprétée et contrôlée par notre programme.
Question : Avons-nous déjà lu la température ?
Réponse attendue : Non : nous avons seulement une demande structurée.
Action : Rester sur la présentation.

## Slide 10 — Python retrouve la fonction et vérifie l’appel.

15–17 min
À dire : On retrouve la fonction autorisée. On ne transforme pas librement le texte du modèle en code exécutable.
Question : Un appel bien écrit est-il toujours cohérent ?
Réponse attendue : Non. Il faut aussi vérifier la clinique visée et la provenance des valeurs.
Action : Rester sur la présentation.

## Slide 11 — Renvoyer le résultat au modèle.

17–19 min
À dire : Voici le lien essentiel. Exécuter un outil ne suffit pas : le résultat doit revenir dans la conversation.
Question : Que perd-on si le résultat n’est pas ajouté ?
Réponse attendue : Le modèle n’a pas l’observation ; il ne peut pas fonder la suite sur cette mesure.
Action : Rester sur la présentation.

## Slide 12 — Prédisez le prochain outil.

19–21 min
À dire : Laissez trente secondes au binôme, puis prenez deux justifications.
Question : A, B ou C ? Pourquoi ?
Réponse attendue : B. Il manque la procédure. La mesure seule ne permet pas de conclure.
Action : Rester sur la présentation.

## Slide 13 — Construire la boucle : le modèle choisit la suite.

21–23 min
À dire : On ne code pas cinq étapes aveugles. Le modèle reçoit les observations, puis propose la suite dans les limites fixées.
Question : Qu’est-ce qui décide de la prochaine étape ?
Réponse attendue : Le modèle propose à partir de l’historique ; le programme autorise ou bloque.
Action : Rester sur la présentation.

## Slide 14 — Dans le notebook, qui est client ?

23–25 min
À dire : Personne n’est censé deviner cela. Notre code définit ce contrat. Le pseudo-code interroger_IA correspond à complete dans le notebook.
Question : mode et complete sont-ils tous les deux des méthodes ?
Réponse attendue : Non : mode est un attribut, complete est une méthode. Les parenthèses indiquent l’appel.
Action : Rester sur la présentation.

## Slide 15 — Faire le lien avec les vraies lignes Python.

25–27 min
À dire : Voici le seul petit pont de syntaxe dont nous avons besoin. Lisez le sens. Vous n’avez pas à le recopier.
Question : D’où vient selected_client dans cette fonction ?
Réponse attendue : De l’argument transmis quand on appelle propose_tool ; ce nom est local à la fonction.
Action : Démo facultative de 2 minutes à la place de l’explication : notebook solution, contrat client puis premier appel. Si le setup ne fonctionne pas, rester sur la slide.

## Slide 16 — Jouons la mission complète.

27–30 min
À dire : Une personne joue le modèle, une autre Python. Après chaque résultat, le groupe propose l’outil suivant.
Question : Après la qualification critique, quelle suite faut-il justifier ?
Réponse attendue : Créer le dossier puis demander la revue pour cet incident et cette action.
Action : Annoncer les résultats : mesure ; procédure ; CRITICAL ; identifiant d’incident ; décision simulée. Aucun ordinateur requis.

## Slide 17 — Appliquer une règle connue, sans la réinventer.

30–32 min
À dire : Nous séparons l’interprétation de la demande et l’application des règles. Le seuil est fixé par le scénario.
Question : Qui calcule ici le niveau de risque ?
Réponse attendue : L’outil Python. Le modèle lui transmet les mesures déjà vérifiées.
Action : Rester sur la présentation.

## Slide 18 — Première panne : la mesure a changé en route.

32–34 min
À dire : Faites voter : accepter ou refuser ? Puis demandez quelle preuve permet de trancher.
Question : Pourquoi une simple validation de type ne suffit-elle pas ?
Réponse attendue : Elle accepterait 5. Le contrôle de cohérence doit comparer avec les données réellement observées.
Action : Rester sur la présentation.

## Slide 19 — Le modèle dit « résolu ». Peut-on accepter sa réponse ?

34–36 min
À dire : Lisez la phrase du modèle. Laissez le groupe voter avant de commenter les preuves manquantes.
Question : Peut-on accepter « résolu » ?
Réponse attendue : Non. Le cas exige une revue, mais aucun accord correspondant n’a été enregistré.
Action : Rester sur la présentation.

## Slide 20 — Autoriser la conclusion à partir des preuves.

36–38 min
À dire : Le dernier message n’est pas la preuve. C’est l’historique des opérations réussies qui permet d’autoriser la conclusion.
Question : Un accord pour un autre incident suffit-il ?
Réponse attendue : Non. La décision doit correspondre au dossier de cette exécution et à l’action proposée.
Action : Rester sur la présentation.

## Slide 21 — Éviter une boucle sans fin.

38–40 min
À dire : Ce choix est volontairement simple. Un autre produit pourrait prévoir des reprises, avec des limites explicites.
Question : Pourquoi garder une limite même avec l’anti-répétition ?
Réponse attendue : Le modèle pourrait varier les arguments et continuer indéfiniment.
Action : Rester sur la présentation.

## Slide 22 — Retrouver la preuve derrière chaque étape.

40–41 min
À dire : La trace est notre journal de preuve. Choisissez une ligne et expliquez à quoi elle sert.
Question : Trace et historique sont-ils identiques ?
Réponse attendue : L’historique est transmis au modèle ; la trace sert à contrôler et examiner l’exécution.
Action : Rester sur la présentation.

## Slide 23 — Un test passe quand le comportement attendu est respecté.

41–43 min
À dire : Un arrêt attendu peut faire passer un test. Faisons la différence entre réussite de la mission et réussite du test.
Question : Pourquoi missing_approval peut-il être PASS ?
Réponse attendue : Parce que le comportement attendu est de refuser la conclusion sans approbation.
Action : Rester sur la présentation.

## Slide 24 — Un test compare le comportement à une attente.

43–45 min
À dire : Faites proposer un nouveau cas : par exemple une approbation donnée pour le mauvais incident.
Question : Que devrait-il arriver si on retire une protection ?
Réponse attendue : Le test qui dépend de cette protection doit échouer. Sinon, il ne la vérifie pas assez bien.
Action : Rester sur la présentation.

## Slide 25 — Si Gemini ne répond pas, on garde le fil.

45–46 min
À dire : Le mode doit être annoncé. Une simulation est utile, mais nous ne la présentons pas comme une réponse live.
Question : Qu’évaluons-nous encore en mock ?
Réponse attendue : L’orchestration, les preuves, les validations et les conditions d’arrêt.
Action : Rester sur la présentation.

## Slide 26 — Le notebook prolonge ce que vous venez d’expliquer.

46–48 min
À dire : Pour refaire la démonstration, prenez la solution. Pour écrire les quatre décisions vous-mêmes, prenez le notebook participant.
Question : Que lancer après une cellule qui définit une fonction ?
Réponse attendue : La cellule qui appelle cette fonction ; une définition seule ne produit pas le résultat.
Action : Afficher les liens cliquables. Colab facultatif : navigateur, connexion et compte Google ; pas d’installation Python sur Windows.

## Slide 27 — Pouvez-vous expliquer un agent avec vos mots ?

48–50 min
À dire : Prenez une minute à deux. Puis recueillez deux exemples.
Question : Dans votre métier, quel appel doit exiger un accord ?
Réponse attendue : Une action concrète, un accord identifiable et un test qui bloque son absence.
Action : Rester sur la présentation.
