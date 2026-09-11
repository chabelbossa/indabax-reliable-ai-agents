# Guide d’animation — présentation française V2

La présentation est autonome : chaque notion est expliquée avant le code qui l’applique. Les blocs marqués « Python réel » correspondent à l’architecture exécutable de `examples/guided_demo.py` ou aux contrôles utilisés par le projet.

Le public n’a pas besoin de coder pendant la séance. Il doit cependant pouvoir distinguer modèle, outil, agent, historique et trace ; lire la boucle ; expliquer les contrôles ; et proposer un scénario de test.

## Slide 01 — Couverture

00:00–00:01
Objectif : Annoncer le résultat d’apprentissage.
À dire : Nous allons partir d’un modèle qui répond, lui donner des outils, construire sa boucle d’exécution puis vérifier ses décisions.

## Slide 02 — Un concept, son code, puis son comportement observable.

00:01–00:02
Objectif : Donner la carte de la session.
À dire : Chaque bloc commence par l’idée. Le code vient ensuite pour montrer comment cette idée devient un système exécutable.

## Slide 03 — 09:42 : une clinique signale une hausse de température.

00:02–00:04
Objectif : Installer un problème concret.
À dire : KoraCare est fictif. Nous devons examiner cette alerte sans confondre une réponse plausible avec une exécution prouvée.
Question : Quelle information faut-il vérifier en premier ?
Réponse attendue : La mesure actuelle de la clinique.

## Slide 04 — 12,4 °C est une mesure, pas une moyenne.

00:04–00:06
Objectif : Rendre les données et la règle explicites.
À dire : La valeur 12,4 n’est ni un seuil ni une moyenne : c’est la mesure lue dans notre jeu de données.
Question : Pourquoi 12,4 °C ne suffit-il pas à lui seul ?
Réponse attendue : La durée, l’état du capteur et la procédure comptent aussi.

## Slide 05 — Un modèle produit une proposition. Une application agit.

00:06–00:09
Objectif : Poser le vocabulaire avant le code.
À dire : Le modèle propose. Notre code décide ce qui est autorisé, exécute les fonctions et conserve les preuves.
Question : Qui exécute réellement un outil ?
Réponse attendue : Le programme Python, après contrôle de la proposition.

## Slide 06 — Un tour transforme une demande en nouvelle information.

00:09–00:11
Objectif : Présenter le cycle complet avant son implémentation.
À dire : Suivons toujours ces quatre moments : proposition, contrôle, exécution, observation.

## Slide 07 — Un outil possède une fonction et un contrat.

00:11–00:13
Objectif : Expliquer le contrat d’un outil.
À dire : Le modèle voit le schéma. Il ne voit pas ni n’exécute directement le corps de la fonction.
Question : À quoi sert le schéma ?
Réponse attendue : À expliquer au modèle comment demander l’outil de manière structurée.

## Slide 08 — Valider les arguments avant de lire les données.

00:13–00:16
Objectif : Montrer un outil réel et lisible.
À dire : La description guide le modèle ; ce code contrôle l’entrée et produit la donnée qui sera utilisée par la suite.

## Slide 09 — Le client masque le fournisseur, pas le comportement attendu.

00:16–00:18
Objectif : Expliquer l’abstraction du client avant de l’utiliser.
À dire : Le reste de l’agent dépend d’un contrat simple. C’est ce qui permet de changer de fournisseur sans réécrire la boucle.
Question : Comment savons-nous que client possède complete ?
Réponse attendue : Le protocole LLMClient définit ce contrat.

## Slide 10 — Définir le contrat, puis injecter le client choisi.

00:18–00:21
Objectif : Rendre complete, mode et client compréhensibles.
À dire : Rien n’est caché : le protocole annonce le contrat et la fonction reçoit l’implémentation choisie.

## Slide 11 — Le modèle propose l’appel ; il ne lit pas encore la clinique.

00:21–00:23
Objectif : Distinguer proposition et exécution.
À dire : Le bloc de gauche est une demande du modèle. Le bloc de droite est le résultat obtenu par Python.
Question : À quel moment connaissons-nous réellement 12,4 °C ?
Réponse attendue : Après l’exécution réussie de get_clinic_status.

## Slide 12 — L’agent avance grâce à deux mémoires différentes.

00:23–00:25
Objectif : Expliquer l’état avant le code d’exécution.
À dire : L’historique sert à poursuivre le raisonnement ; la trace sert à vérifier ce qui s’est réellement passé.
Question : Pourquoi conserver les deux ?
Réponse attendue : Ils servent à des responsabilités différentes : contexte du modèle et preuve d’exécution.

## Slide 13 — Regrouper ce qui permet de continuer et d’auditer.

00:25–00:27
Objectif : Montrer une abstraction d’état simple.
À dire : L’objet AgentState évite de faire circuler quatre variables séparées à chaque fonction.

## Slide 14 — Contrôler, tracer, puis renvoyer l’observation.

00:27–00:30
Objectif : Montrer le cœur de l’aller-retour.
À dire : make_trace condense ici la construction d’une TraceEntry ; la version exécutable conserve tous ses champs.

## Slide 15 — Chaque observation détermine l’information encore nécessaire.

00:30–00:33
Objectif : Faire parcourir la chaîne de décisions.
À dire : À chaque ligne, demandez quelle information manquait avant cet appel et ce que le résultat permet ensuite.

## Slide 16 — La boucle décide quand appeler un outil et quand s’arrêter.

00:33–00:35
Objectif : Expliquer la boucle avant son code.
À dire : Les fonctions précédentes sont maintenant assemblées. Le modèle propose la suite ; Python garde les limites.
Question : Quelles sont les deux sorties possibles d’un tour ?
Réponse attendue : Un ou plusieurs appels d’outils, ou une réponse finale.

## Slide 17 — Assembler les abstractions sans masquer le mécanisme.

00:35–00:38
Objectif : Montrer l’assemblage final.
À dire : Chaque nom correspond à une idée déjà expliquée. La boucle devient lisible parce que les responsabilités sont séparées.

## Slide 18 — Une sortie structurée peut encore être fausse.

00:38–00:40
Objectif : Élargir la validation au-delà du schéma.
À dire : Un modèle peut produire un JSON parfaitement valide avec une température inventée. Il faut comparer avec la trace.
Question : 5,0 est-il un argument valide pour une température ?
Réponse attendue : Oui pour le type ; non pour la cohérence si le capteur a renvoyé 12,4.

## Slide 19 — Refuser une mesure qui ne vient pas de l’observation.

00:40–00:43
Objectif : Montrer un contrôle de provenance réel.
À dire : Le type float ne suffit pas. Cette règle empêche le modèle de modifier silencieusement une observation.

## Slide 20 — Le modèle dit « résolu ». Peut-on accepter sa réponse ?

00:43–00:45
Objectif : Montrer que la réponse finale est aussi contrôlée.
À dire : Une phrase assurée ne remplace ni le dossier ni la revue. Le système doit donc bloquer cette conclusion.
Question : Pourquoi le résultat correct est-il un arrêt ?
Réponse attendue : Parce que les preuves requises pour conclure sont absentes.

## Slide 21 — Lier l’accord au bon incident et à la bonne action.

00:45–00:47
Objectif : Montrer la frontière de décision.
À dire : Demander une revue ne suffit pas. Le programme vérifie la décision, son incident et son action.

## Slide 22 — Un test utile vérifie le chemin, les preuves et l’arrêt.

00:47–00:48
Objectif : Expliquer ce que mesure la suite d’évaluation.
À dire : Nous testons le comportement du système, pas seulement la formulation de la dernière réponse.

## Slide 23 — Un test passe quand le comportement attendu est respecté.

00:48–00:49
Objectif : Lire un cas normal et un refus attendu.
À dire : Le scénario approbation absente est PASS parce que le système produit review_required comme prévu.
Question : Que doit-il arriver si l’on retire la protection correspondante ?
Réponse attendue : Ce test doit échouer.

## Slide 24 — Une architecture en cinq responsabilités.

00:49
Objectif : Consolider les acquis.
À dire : Même sans avoir codé pendant la séance, vous pouvez maintenant lire la boucle, expliquer ses composants et identifier où placer un contrôle.

## Slide 25 — Rejouer la démo, puis explorer l’implémentation complète.

00:49–00:50
Objectif : Donner une suite adaptée à chaque niveau.
À dire : Commencez par la démonstration guidée. Passez ensuite au notebook solution, puis au notebook participant si vous voulez reconstruire les décisions.

## Slide 26 — Une bonne réponse n’est pas une preuve d’exécution.

00:50
Objectif : Clore sur le transfert vers leurs projets.
À dire : Laisser le QR et les ressources affichés.
