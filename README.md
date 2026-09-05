# Building Reliable AI Agents

**Tool Calling, Orchestration and Evaluation in Practice**<br>
Deep Learning IndabaX Benin 2026. Educational lab by BOSSA Chabel

[![Ouvrir le notebook participant en français](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb)
[![Open the English participant notebook](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-en.ipynb)

## La mission

À 09:42, le réfrigérateur d'une clinique fictive au Bénin signale **12,4°C depuis
52 minutes**. Les vaccins ne peuvent être déclarés sûrs sur la seule parole d'un
LLM. Pendant 50 minutes, les participants deviennent l'équipe AI/Operations de
**KoraCare** et construisent le copilote qui doit :

1. vérifier la télémétrie ;
2. retrouver la procédure applicable ;
3. qualifier le risque ;
4. ouvrir un incident ;
5. obtenir une décision explicite d'un opérateur simulé ;
6. produire une timeline et tester dix scénarios, dont sept erreurs volontaires ;
7. déverrouiller un dossier de preuves JSON téléchargeable.

L'architecture est fournie. Les participants complètent dix décisions
d'orchestration réparties en quatre checkpoints. Le français est le parcours
principal ; une version anglaise équivalente est disponible.

> A good answer is not evidence of a safe execution.

KoraCare, les cliniques, les personnes et les données sont entièrement
synthétiques. Ce lab enseigne l'ingénierie de systèmes IA ; il ne fournit aucun
avis médical ou pharmaceutique. Aucun humain externe n'est contacté et aucune
action physique n'est exécutée. Le résultat est un dossier d'incident simulé.

## Ce que vous allez apprendre

- Distinguer la proposition du LLM de l'exécution contrôlée par Python.
- Orchestrer une boucle multi-outils sans framework agentique.
- Valider des arguments et arrêter proprement une exécution invalide.
- Imposer une frontière human-in-the-loop pour les décisions critiques.
- Lire une timeline : étapes, arguments, résultats, erreurs et latence.
- Évaluer une séquence et un résultat de sûreté, pas seulement le texte final.

## Prérequis

- Python : fonctions, boucles, dictionnaires et JSON.
- Python 3.10+ en local, ou Google Colab.
- Une clé Gemini gratuite pour le parcours live normal.
- Aucune clé pour le fallback mock déterministe.

Aucun Docker, GPU, frontend, vector store, framework d'agents ou base de données
externe n'est nécessaire.

## Démarrage dans Colab

1. Ouvrir le [notebook participant français](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb) ou le [notebook anglais](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-en.ipynb).
2. Exécuter la cellule de setup. `MODE=gemini` demande la clé avec `getpass` sans l'afficher.
3. Traiter l'alerte KoraCare et compléter les dix TODOs.
4. Utiliser la [solution française](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-fr.ipynb) ou la [solution anglaise](https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-en.ipynb) dès qu'un checkpoint bloque le groupe.

## Démarrage local

```bash
git clone https://github.com/chabelbossa/indabax-reliable-ai-agents.git
cd indabax-reliable-ai-agents
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m evals.run_evals
```

Résultat attendu : `10 / 10 incident scenarios passed`.

## Gemini et plan de secours

Créer une clé dans [Google AI Studio](https://aistudio.google.com/apikey), puis :

```bash
export LLM_MODE=gemini
export GEMINI_API_KEY='your-key-here'
```

La clé n'est ni stockée ni affichée par le notebook. En cas de quota ou de réseau
instable, le passage au fallback est explicite :

```bash
export LLM_MODE=mock
```

Dans **Colab**, remplacer plutôt la ligne `MODE = ...` du setup par
`MODE = "mock"`, puis relancer cette cellule, la mission et les évaluations.
Le dossier déjà cloné est réutilisé. Le mock évite l'API ; le premier accès à Colab
et l'installation des dépendances demandent toujours Internet.

Les limites Gemini sont par projet, pas par clé. Préparer une clé par binôme et
limiter les appels réels à la mission ; les dix évaluations sont déterministes.
Le modèle configuré est `gemini-3.7-flash`. Le test live vérifie son accès effectif.

Le mode sélectionné est toujours affiché. Le mock exécute exactement le même
workflow métier et reste la référence déterministe des evals ; il n'est jamais
présenté silencieusement comme une réponse Gemini.

Avant le workshop, vérifier le chemin live complet avec une clé fraîche déjà
présente dans l'environnement :

```bash
python scripts/smoke_gemini.py
```

Le script ne lit que `GEMINI_API_KEY`, ne l'affiche jamais et refuse de basculer
silencieusement vers le mock. Le succès exige les cinq outils et une décision
simulée `APPROVED` correspondant à l'incident et à l'action recommandée. Il charge
les définitions du notebook distribué, pas une boucle de démonstration différente.

## Les cinq outils

| Outil | Responsabilité | Frontière de fiabilité |
|---|---|---|
| `get_clinic_status` | Lire une télémétrie synthétique | Aucune mesure inventée |
| `search_cold_chain_sop` | Consulter une procédure locale | Source vérifiable, miss explicite |
| `assess_excursion_risk` | Appliquer des seuils déterministes | Décision reproductible |
| `create_incident` | Créer un incident en mémoire | Schéma et sévérité validés |
| `request_human_review` | Contacter l'opérateur simulé | Approbation explicite avant action critique |

Chaque outil retourne la même enveloppe `ok/data/error`. Pour un risque `HIGH`,
`CRITICAL` ou `UNKNOWN`, la safety gate interdit une résolution finale tant que
`request_human_review` n'a pas produit une décision `APPROVED`.
L'opérateur simulé rejette aussi une action incompatible avec la sévérité ; un
appel humain n'est donc pas une approbation automatique.

## Observabilité et evals

Le tableau de contrôle Colab expose l'identifiant du run, le dossier d'incident,
le risque, la décision humaine et une timeline de chaque `call_id`. Une seconde
matrice visualise les checks réussis ou manquants sur les dix evals, qui vérifient
simultanément :

- la séquence exacte d'outils ;
- l'outcome du run ;
- le statut de sûreté ;
- la présence ou l'absence correcte d'une revue humaine ;
- la complétude de la trace ;
- le résultat opérationnel attendu.

Les cas adverses couvrent l'absence de preuve, la mesure altérée, l'approbation
absente ou rejetée, le mauvais incident, l'appel répété et la panne API. Retirer
une protection doit faire échouer le scénario associé. Un score ne garantit que
les cas testés, pas une sûreté générale.

Quand la mission critique est approuvée et que les dix scénarios passent, le
notebook déverrouille un dossier JSON portable contenant les faits, les cinq
appels, la décision simulée, la matrice et le contre-exemple choisi par le binôme.
Le téléchargement crée le fichier chez le participant ; aucune clé n'y est incluse.
Après une correction tardive, relancer la mission puis l'évaluation pour actualiser
le dossier. Les sorties enregistrées dans les notebooks sont toutes en mock.

```bash
python -m pytest -q
python -m evals.run_evals
python scripts/build_notebooks.py
```

## Déroulé des 50 minutes

Le [runbook animateur français](FACILITATOR_RUNBOOK_FR.md) fournit les questions
exactes, les votes, les signaux de compréhension et les parcours 50/35 minutes.

| Temps | Activité |
|---:|---|
| 0–4 min | Comparer les usages de ChatGPT en 2022 et en 2026 |
| 4–10 min | LLM, application, outil, boucle et workflow |
| 10–14 min | Mission, première décision et ouverture du notebook |
| 14–22 min | Checkpoint 1 : proposer le premier appel |
| 22–31 min | Checkpoint 2 : exécuter, observer et tracer |
| 31–41 min | Checkpoint 3 : contrôles et contre-exemple choisi |
| 41–46 min | Checkpoint 4 : dix scénarios métier et adverses |
| 46–50 min | Dossier, explication du contre-exemple et transfert |

## Structure du dépôt

```text
notebooks/  parcours et solutions FR/EN préexécutés
src/        schémas, cinq outils, boucle, observabilité, adaptateur Gemini
data/       télémétrie et procédures synthétiques transparentes
evals/      trois chemins métier et sept clients adverses ; cas simples conservés en tests
tests/      tests outils, orchestration, Gemini et observabilité
slides/     decks IndabaX bilingues
scripts/    génération reproductible des notebooks et des decks
```

## Présentations

- [PowerPoint français](slides/indabax-reliable-ai-agents-fr.pptx) et [PDF français](slides/indabax-reliable-ai-agents-fr.pdf)
- [English PowerPoint](slides/indabax-reliable-ai-agents-en.pptx) and [English PDF](slides/indabax-reliable-ai-agents-en.pdf)

Pour reconstruire les supports : installer `requirements-build.txt`, placer le
template officiel fourni dans le dossier parent,
puis lancer `python scripts/build_slides.py`. LibreOffice (`soffice`) est nécessaire
pour les PDF. Le format, le blason et les couleurs viennent du template ; Arial sert
de police sans-serif portable et les PDF embarquent leurs polices. Seize slides avec
notes d'animation sont fournies dans chaque langue.

## Dépannage

- **Pas de clé :** choisir `MODE = "mock"` dans le setup Colab, ou `LLM_MODE=mock` en local.
- **Erreur 429/réseau :** annoncer le passage au mock ; ne jamais changer de mode silencieusement.
- **Checkpoint bloqué :** ouvrir immédiatement la solution dans la même langue.
- **Notebook hors du dépôt :** la cellule de setup clone automatiquement le repository public.

## Contact et licence

- GitHub : [chabelbossa](https://github.com/chabelbossa)
- LinkedIn : [Chabel Holdo Bossa](https://www.linkedin.com/in/chabel-holdo-bossa/)
- Licence : MIT
