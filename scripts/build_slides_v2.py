"""French V2: participatory walkthrough; no participant coding required."""
from copy import deepcopy
import os
from pathlib import Path
import build_slides as base
from deck_content import FR, s, REPO

PLAN = []

def add(item, minutes, say, question, answer, action='Rester sur la présentation.'):
    item = deepcopy(item)
    item['notes'] = f"{minutes}\nÀ dire : {say}\nQuestion : {question}\nRéponse attendue : {answer}\nAction : {action}"
    PLAN.append(item)

def code(title, snippet, explanation, result, question, answer, minutes, say, action='Rester sur la présentation.'):
    add(s('pseudo', 'LIRE → PRÉDIRE → EXPLIQUER', title, '', code=snippet,
          explanation=explanation, result=result, question=question), minutes, say, question, answer, action)

def cards(title, values, takeaway, minutes, say, question, answer):
    add(s('cards','ATELIER GUIDÉ · V2',title,'',cards=values,takeaway=takeaway),minutes,say,question,answer)

cover=deepcopy(FR[0])
cover['text'][4]='Comprendre la boucle avec du pseudo-code, puis vérifier ses décisions.'
cover['text'][7]='ATELIER · V2'
add(cover,'00–01 min','Aujourd’hui, on va raisonner ensemble comme les concepteurs d’un agent. Vous n’avez pas besoin de taper du code pour participer.','Que faudrait-il vérifier avant de faire confiance à une réponse ?','Les données et les actions réellement exécutées.')
add(s('agenda','NOTRE PARCOURS · 50 MINUTES','Vous prenez les décisions. Nous suivons leurs effets.','',rows=[
('Partir de l’alerte','Comprendre les faits et répartir les rôles.','7 min'),
('Faire un aller-retour avec l’IA','Lire un appel, exécuter un outil, renvoyer le résultat.','20 min'),
('Construire et protéger la boucle','Jouer la mission, puis provoquer deux erreurs.','14 min'),
('Vérifier et réutiliser','Lire des tests et expliquer une règle pour son métier.','9 min')]),'01–02 min','On lit quelques lignes, vous prédisez la suite, puis on regarde le résultat. Le notebook sert à montrer le même mécanisme en Python.','Faut-il installer Python pour suivre ?','Non. Slides et votes suffisent ; Colab est facultatif.')
mission=deepcopy(FR[3]); mission['deliverable']='Préparez un dossier justifié par des faits et une décision d’opérateur simulé.'
add(mission,'02–04 min','Nous jouons l’équipe de garde de KoraCare. Une alerte arrive. Nous devons enquêter avant de conclure.','12,4 °C est-il un seuil ou une mesure ?','Une mesure du capteur dans notre jeu de données fictif.')
cards('12,4 °C : une mesure, pas une moyenne.',[
('Ce que l’on observe','Le capteur indique 12,4 °C. L’excursion dure 52 minutes. Son état est OK.'),
('La règle de cet exercice','La plage de référence est 2–8 °C. Au-dessus de 8 °C pendant au moins 30 minutes, le cas est critique.'),
('Ce que l’on doit faire','Consulter la procédure, qualifier le risque et obtenir la revue requise. La proposition de transfert reste simulée.')],
'Données et règles fictives du lab : aucune intervention physique ni décision médicale réelle.', '04–06 min','La valeur 12,4 est comparée à une plage, pas à une moyenne. On doit aussi regarder la durée.','Pourquoi la température seule ne suffit-elle pas ?','La règle dépend aussi de la durée et de la fiabilité du capteur.')
cards('Trois rôles à garder en tête.',[
('Le modèle propose','Il reçoit une demande et un contexte. Il propose une réponse ou un appel d’outil.'),
('Python contrôle et exécute','Notre programme vérifie la demande, appelle la fonction et conserve son résultat.'),
('L’opérateur décide','Pour ce cas critique, un opérateur doit approuver l’action proposée. Son rôle est simulé dans le lab.')],
'Un appel proposé par le modèle ne constitue pas une action déjà exécutée.', '06–07 min','Gardez ces trois rôles. Quand quelque chose se passe, nous allons demander qui en est responsable.','Qui lit réellement la mesure ?','La fonction exécutée par Python, sur nos données locales.')
code('Commencer par une conversation.',
'demande ← « Examine l’alerte KCARE-ADJ-01 »\nhistorique ← [consigne, demande]\nréponse ← interroger_IA(historique, outils = [])\nafficher(réponse.texte)',
'← signifie « conserver la valeur ».\n\nL’historique contient les messages.\nUne liste vide [] signifie : aucun outil disponible.\n\ninterroger_IA est un nom pédagogique.',
'Exemple illustratif : « Il me faut une mesure et la procédure. » La formulation réelle peut varier.',
'L’IA peut-elle vérifier le capteur ici ?','Non. Elle peut répondre, mais aucun outil ne lui donne accès au capteur.','07–09 min',
'On commence comme un chatbot. Nous lui avons donné une question, mais aucun moyen de consulter nos données.')
code('Définir une fonction ne la lance pas.',
'DÉFINIR lire_clinique(identifiant) :\n    RENVOYER données_locales[identifiant]\n\nmesure ← lire_clinique("KCARE-ADJ-01")\nafficher(mesure)',
'DÉFINIR prépare une recette.\n\nL’appel avec un identifiant l’exécute.\n\nLa valeur renvoyée est stockée dans mesure. Ici, les données sont locales et fictives.',
'Après l’appel : température = 12,4 °C ; durée = 52 min ; capteur = OK.',
'À quelle ligne le travail se fait-il ?','À mesure ← lire_clinique(...). La définition seule ne lit rien.','09–11 min',
'Une cellule de définition prépare le travail. Une autre cellule doit appeler la fonction pour que quelque chose se passe.')
code('Expliquer au modèle l’outil disponible.',
'outil ← {\n  nom : "get_clinic_status",\n  description : "Lire l’état d’une clinique",\n  argument : clinic_id, texte obligatoire\n}\noutils ← [outil]',
'Un schéma décrit le nom, le rôle et les arguments attendus.\n\nclinic_id veut dire « identifiant de clinique ».\n\nLe développeur écrit la fonction et cette description.',
'Le modèle voit une description de l’outil. Python conserve la fonction à exécuter.',
'Le modèle devine-t-il nos fonctions cachées ?','Non. L’application lui transmet explicitement leurs descriptions.','11–13 min',
'Nous devons présenter les outils au modèle, comme je dois vous présenter les fonctions avant de vous demander de les utiliser.')
code('Avec l’outil, la réponse peut devenir une demande.',
'réponse ← interroger_IA(historique, outils)\n\nappel proposé :\n    nom = "get_clinic_status"\n    arguments = {clinic_id: "KCARE-ADJ-01"}',
'Un appel contient le nom de l’outil et les valeurs à lui transmettre.\n\nLes accolades regroupent des champs nommés.\n\nLe modèle propose. Rien n’est encore exécuté.',
'Proposition illustrative du premier tour. La mesure sera connue après exécution.',
'Avons-nous déjà lu la température ?','Non : nous avons seulement une demande structurée.','13–15 min',
'La nouveauté, c’est cette demande structurée. Elle sera interprétée et contrôlée par notre programme.')
code('Python retrouve la fonction et vérifie l’appel.',
'SI outil inconnu OU arguments invalides :\n    arrêter avec une erreur explicite\nSINON :\n    fonction ← registre[appel.nom]\n    résultat ← fonction(appel.arguments)\n    conserver le résultat dans la trace',
'Le registre relie un nom à une fonction Python déjà écrite.\n\nLa validation contrôle les champs obligatoires et leurs types.\n\nCette écriture simplifie le passage des arguments.',
'get_clinic_status reçoit clinic_id et renvoie 12,4 °C, 52 min, capteur OK.',
'Un appel bien écrit est-il toujours cohérent ?','Non. Il faut aussi vérifier la clinique visée et la provenance des valeurs.','15–17 min',
'On retrouve la fonction autorisée. On ne transforme pas librement le texte du modèle en code exécutable.')
code('Renvoyer le résultat au modèle.',
'ajouter(historique, proposition_du_modèle)\najouter(historique, résultat_de_l’outil)\n\nsuite ← interroger_IA(historique, outils)',
'Le modèle ne voit pas spontanément ce qui s’est passé dans Python.\n\nNous ajoutons sa demande puis la réponse de l’outil, liées au même appel.\n\nC’est un nouvel appel à l’IA.',
'Le nouveau contexte contient la mesure réellement lue. Le modèle peut demander la procédure.',
'Que perd-on si le résultat n’est pas ajouté ?','Le modèle n’a pas l’observation ; il ne peut pas fonder la suite sur cette mesure.','17–19 min',
'Voici le lien essentiel. Exécuter un outil ne suffit pas : le résultat doit revenir dans la conversation.')
cards('Prédisez le prochain outil.',[
('Ce que nous savons','Clinique KCARE-ADJ-01 ; température 12,4 °C ; durée 52 min ; capteur OK.'),
('Trois propositions','A. Déclarer le stock sûr.\n\nB. Chercher la procédure.\n\nC. Inventer une température normale.')],
'Votez, puis justifiez votre choix avec une information qui manque encore.', '19–21 min','Laissez trente secondes au binôme, puis prenez deux justifications.','A, B ou C ? Pourquoi ?','B. Il manque la procédure. La mesure seule ne permet pas de conclure.')
code('Construire la boucle : le modèle choisit la suite.',
'RÉPÉTER au maximum 8 tours :\n    réponse ← interroger_IA(historique, outils)\n    SI réponse contient un appel :\n        exécuter avec contrôles et tracer\n        ajouter appel et résultat à l’historique\n    SINON :\n        vérifier les preuves puis conclure ou bloquer\n        TERMINER\nARRÊTER si la limite est atteinte',
'Un tour = une nouvelle proposition du modèle.\n\nUne observation prépare le tour suivant.\n\nLes contrôles et l’arrêt restent sous la responsabilité du programme.',
'Vue simplifiée : un appel à la fois. Les erreurs et répétitions seront détaillées ensuite.',
'Qu’est-ce qui décide de la prochaine étape ?','Le modèle propose à partir de l’historique ; le programme autorise ou bloque.','21–23 min',
'On ne code pas cinq étapes aveugles. Le modèle reçoit les observations, puis propose la suite dans les limites fixées.')
code('Dans le notebook, qui est client ?',
'client ← créer_client(mode_choisi)\n\nclient.mode\nclient.complete(messages, outils)',
'client est une variable qui garde un objet.\n\n.mode est un attribut : une valeur que l’on lit.\n\n.complete(...) est une méthode : une fonction que l’on appelle sur cet objet.',
'Le contrat fourni annonce mode et complete avant leur utilisation. selected_client désigne le client reçu en paramètre.',
'mode et complete sont-ils tous les deux des méthodes ?','Non : mode est un attribut, complete est une méthode. Les parenthèses indiquent l’appel.','23–25 min',
'Personne n’est censé deviner cela. Notre code définit ce contrat. Le pseudo-code interroger_IA correspond à complete dans le notebook.')
code('Faire le lien avec les vraies lignes Python.',
'# Python réel : noms définis dans le notebook\ndef propose_tool(messages, selected_client):\n    turn = selected_client.complete(\n        messages, TOOL_SCHEMAS\n    )\n    calls = turn.tool_calls\n    call = calls[0] if calls else None\n    return turn, call',
'messages : l’historique reçu.\nselected_client : le client reçu.\nTOOL_SCHEMAS : les descriptions fournies.\n\nturn : la réponse.\ntool_calls : la liste d’appels proposés.\n[0] : le premier ; None : aucun.',
'Cette cellule définit la fonction. Une cellule suivante l’appelle avec l’historique et le client choisi.',
'D’où vient selected_client dans cette fonction ?','De l’argument transmis quand on appelle propose_tool ; ce nom est local à la fonction.','25–27 min',
'Voici le seul petit pont de syntaxe dont nous avons besoin. Lisez le sens. Vous n’avez pas à le recopier.',
'Démo facultative de 2 minutes à la place de l’explication : notebook solution, contrat client puis premier appel. Si le setup ne fonctionne pas, rester sur la slide.')
tools=deepcopy(FR[8]); tools['title']='Jouons la mission complète.'
add(tools,'27–30 min','Une personne joue le modèle, une autre Python. Après chaque résultat, le groupe propose l’outil suivant.','Après la qualification critique, quelle suite faut-il justifier ?','Créer le dossier puis demander la revue pour cet incident et cette action.','Annoncer les résultats : mesure ; procédure ; CRITICAL ; identifiant d’incident ; décision simulée. Aucun ordinateur requis.')
code('Appliquer une règle connue, sans la réinventer.',
'SI capteur indisponible :\n    risque ← INCONNU ; demander une inspection\nSINON SI température > 8 ET durée ≥ 30 :\n    risque ← CRITIQUE\n    proposition ← QUARANTINE_AND_TRANSFER\n    revue_humaine_requise ← vrai',
'Extrait des règles du lab, pas toute la fonction.\n\nassess_excursion_risk applique ces règles déterministes.\n\nLe modèle choisit de l’appeler ; il ne fixe pas le seuil.',
'12,4 > 8 et 52 ≥ 30 : le cas est CRITICAL et exige une revue. Aucun transfert réel.',
'Qui calcule ici le niveau de risque ?','L’outil Python. Le modèle lui transmet les mesures déjà vérifiées.','30–32 min',
'Nous séparons l’interprétation de la demande et l’application des règles. Le seuil est fixé par le scénario.')
code('Première panne : la mesure a changé en route.',
'mesure_observée ← 12,4\nvaleur_proposée ← 5\n\nSI valeur_proposée ≠ mesure_observée :\n    refuser l’appel\n    tracer « mesure altérée »\n    arrêter proprement',
'5 est bien un nombre : le type est valide.\n\nMais cette valeur ne correspond pas au résultat du capteur.\n\nIl faut vérifier la provenance, pas seulement le format.',
'Le calcul du risque est refusé. Un argument numérique valide peut être factuellement faux.',
'Pourquoi une simple validation de type ne suffit-elle pas ?','Elle accepterait 5. Le contrôle de cohérence doit comparer avec les données réellement observées.','32–34 min',
'Faites voter : accepter ou refuser ? Puis demandez quelle preuve permet de trancher.')
fail=deepcopy(FR[13])
add(fail,'34–36 min','Lisez la phrase du modèle. Laissez le groupe voter avant de commenter les preuves manquantes.','Peut-on accepter « résolu » ?','Non. Le cas exige une revue, mais aucun accord correspondant n’a été enregistré.')
code('Autoriser la conclusion à partir des preuves.',
'SI preuves insuffisantes :\n    bloquer la conclusion\nSINON SI revue requise ET accord non conforme :\n    arrêter : revue requise\nSINON :\n    rendre le compte rendu avec ses preuves',
'Accord conforme = APPROVED, pour le bon incident et la bonne action.\n\nLes mesures et la gravité doivent aussi être cohérentes.\n\nUne demande d’accord ne vaut pas approbation.',
'Cas critique approuvé : dossier escaladé avec décision enregistrée. Cela ne prouve pas un transfert physique.',
'Un accord pour un autre incident suffit-il ?','Non. La décision doit correspondre au dossier de cette exécution et à l’action proposée.','36–38 min',
'Le dernier message n’est pas la preuve. C’est l’historique des opérations réussies qui permet d’autoriser la conclusion.')
code('Éviter une boucle sans fin.',
'SI même outil ET mêmes arguments déjà exécutés :\n    arrêter : appel répété\nSI outil en erreur :\n    tracer l’erreur puis arrêter\nSI 8 tours atteints :\n    arrêter : limite atteinte',
'Une répétition est ici un appel strictement identique.\n\nLa limite de tours borne aussi les autres boucles.\n\nCes arrêts sont des protections du programme.',
'Dans ce lab, les erreurs d’outils provoquent un arrêt contrôlé ; elles ne déclenchent pas une réparation automatique.',
'Pourquoi garder une limite même avec l’anti-répétition ?','Le modèle pourrait varier les arguments et continuer indéfiniment.','38–40 min',
'Ce choix est volontairement simple. Un autre produit pourrait prévoir des reprises, avec des limites explicites.')
add(s('table','LA TRACE','Retrouver la preuve derrière chaque étape.','',headers=['Étape','Information conservée','Ce que l’on vérifie'],widths=[4.4,7.1,6],row_height=1.2,table_size=23,rows=[
('Mesure','12,4 °C ; 52 min ; capteur OK','Les faits viennent de l’outil.'),
('Risque','CRITICAL ; revue requise','Les arguments reprennent les faits.'),
('Incident','Identifiant du dossier créé','Le dossier correspond à la clinique.'),
('Revue','Décision et action approuvée','L’accord vise ce même incident.')],takeaway='Exemple de parcours simulé. La trace réelle garde aussi arguments, erreurs et durée.'),'40–41 min','La trace est notre journal de preuve. Choisissez une ligne et expliquez à quoi elle sert.','Trace et historique sont-ils identiques ?','L’historique est transmis au modèle ; la trace sert à contrôler et examiner l’exécution.')
evalslide=deepcopy(FR[14]); add(evalslide,'41–43 min','Un arrêt attendu peut faire passer un test. Faisons la différence entre réussite de la mission et réussite du test.','Pourquoi missing_approval peut-il être PASS ?','Parce que le comportement attendu est de refuser la conclusion sans approbation.')
code('Un test compare le comportement à une attente.',
'POUR chaque scénario préparé :\n    résultat ← lancer_agent(scénario)\n    vérifier outils, arguments et preuves\n    vérifier arrêt ou conclusion attendue\n    PASS ← toutes les vérifications sont vraies',
'Une évaluation décrit à l’avance ce qui doit arriver.\n\nLes dix scénarios du lab utilisent un simulateur déterministe.\n\nIls testent les protections, pas la qualité générale de Gemini.',
'10/10 signifie que ces dix cas passent. Cela ne garantit ni tous les futurs cas ni les choix du modèle live.',
'Que devrait-il arriver si on retire une protection ?','Le test qui dépend de cette protection doit échouer. Sinon, il ne la vérifie pas assez bien.','43–45 min',
'Faites proposer un nouveau cas : par exemple une approbation donnée pour le mauvais incident.')
cards('Si Gemini ne répond pas, on garde le fil.',[
('Gemini','L’IA produit de nouvelles propositions. La connexion, la clé et le service doivent fonctionner.'),
('Mock','Un simulateur suit des réponses préparées. Il permet d’observer les mêmes contrôles ; ce n’est pas une IA en direct.'),
('Sans notebook','On joue les rôles avec ces slides : proposition, contrôle, résultat, suite. Tout le raisonnement reste visible.')],
'Si l’API bloque : annoncer le changement, choisir mock dans le setup, puis relancer les cellules dans l’ordre.', '45–46 min','Le mode doit être annoncé. Une simulation est utile, mais nous ne la présentons pas comme une réponse live.','Qu’évaluons-nous encore en mock ?','L’orchestration, les preuves, les validations et les conditions d’arrêt.')
resources=s('resources','REPARTIR AVEC LES SUPPORTS','Le notebook prolonge ce que vous venez d’expliquer.','',links=[
('La V2 et son guide d’animation','Reprendre les pseudo-codes et les questions du groupe.',REPO+'/tree/main/slides'),
('Notebook solution français · ouvrir dans Colab','Observer les cellules déjà complétées ; exécuter dans l’ordre.', 'https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-fr.ipynb'),
('Notebook participant français · pour s’exercer ensuite','Compléter les quatre décisions d’orchestration à votre rythme.','https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb')])
add(resources,'46–48 min','Pour refaire la démonstration, prenez la solution. Pour écrire les quatre décisions vous-mêmes, prenez le notebook participant.','Que lancer après une cellule qui définit une fonction ?','La cellule qui appelle cette fonction ; une définition seule ne produit pas le résultat.','Afficher les liens cliquables. Colab facultatif : navigateur, connexion et compte Google ; pas d’installation Python sur Windows.')
closing=deepcopy(FR[-1]); closing['title']='Pouvez-vous expliquer un agent avec vos mots ?'; closing['prompt']='Nommez un outil, son résultat et une raison de bloquer la suite.'
closing['example']='En binôme : une personne raconte la boucle ; l’autre demande « quelle preuve ? ».'
add(closing,'48–50 min','Prenez une minute à deux. Puis recueillez deux exemples.','Dans votre métier, quel appel doit exiger un accord ?','Une action concrète, un accord identifiable et un test qui bloque son absence.')

original_render = base.render

def render(slide, item):
    if item['kind'] != 'pseudo':
        return original_render(slide,item)
    base.text(slide,item['label'],1.25,.78,17.5,.4,19,base.GREEN,True)
    base.text(slide,item['title'],1.25,1.45,17.5,1.35,40,bold=True)
    base.text(slide,'PYTHON RÉEL' if item['code'].startswith('# Python') else 'PSEUDO-CODE · À LIRE, PAS À COPIER',1.25,2.85,10.8,.45,17,base.MUTED,True)
    base.box(slide,1.25,3.45,10.7,4.4,base.INK)
    base.text(slide,item['code'],1.55,3.75,10.1,3.95,22,'FFFFFF',mono=True)
    base.text(slide,'COMMENT LE LIRE',12.45,2.85,6.3,.45,17,base.GREEN,True)
    base.text(slide,item['explanation'],12.45,3.5,6.3,4.5,24)
    base.box(slide,1.25,8.05,17.5,1.0,base.PALE)
    base.text(slide,item['result'],1.55,8.23,16.9,.78,22,base.GREEN,True)
    base.text(slide,'À VOUS · '+item['question'],1.25,9.4,17.5,.8,24,bold=True)

if __name__=='__main__':
    base.SOURCE = Path(os.environ.get('INDABAX_DECK_TEMPLATE', str(base.OFFICIAL_TEMPLATE)))
    base.render=render
    deck=base.build_deck('fr',plan=PLAN,suffix='-v2')
    print(deck)
    print(base.convert_to_pdf(deck))
    guide=['# Guide d’animation — V2 française\n',
      'Parcours de 50 minutes sans saisie de code obligatoire. La pratique repose sur les prédictions, les votes et le jeu de rôles. Les pseudo-codes simplifient le programme et ne sont pas exécutables. Le seul extrait Python réel est explicitement signalé.\n',
      'Avant la session : ouvrir le PDF et, si souhaité, préparer le notebook solution en mock. Garder le mode affiché. Une démo facultative remplace les deux minutes de la slide 15 ; elle ne s’ajoute pas au programme. Ne pas attendre une installation ou une clé pour commencer.\n',
      'Si le groupe est à l’aise : lui faire commenter les lignes et proposer un contre-exemple. Si le groupe hésite : lire chaque ligne en français puis demander qui agit. Si le temps manque : raccourcir les interventions aux slides 12 et 16, garder les erreurs et les évaluations.\n',
      'Ce que l’on envoie : PDF V2 pour tous ; lien du notebook solution pour rejouer ; notebook participant pour pratiquer ensuite. Aucun code à copier depuis les slides. Sur Windows sans Python, le parcours slides suffit ; Colab est facultatif. Hors connexion, utiliser le PDF téléchargé.\n']
    for i,item in enumerate(PLAN,1):
        title=item.get('title','Construire des agents IA fiables')
        guide.append(f'## Slide {i:02d} — {title}\n\n'+item['notes']+'\n')
    (base.ROOT/'slides/GUIDE_ANIMATION_V2_FR.md').write_text('\n'.join(guide))
