"""Visible contracts and predict/run/observe exercises for the bilingual workshop."""
import re


def clean(source):
    return re.sub(r"# SOLUTION \d+:", "# Fourni / Provided:", source)


def common_cells(language, base):
    markdown, code = base.markdown, base.code
    fr = language == "fr"
    def say(french, english):
        return french if fr else english
    return [
        markdown(base.TEXT[language]["title"]),
        markdown(say("""
## Le parcours : parler → demander un outil → observer → contrôler → tester

Vous complétez **quatre décisions**, une par checkpoint. Les fonctions de trace et
les formats de données sont fournis. Chaque définition est suivie d'une cellule à lancer.
Exécuter `def ...` prépare une fonction : cela ne l'appelle pas encore.

Dans Colab : faites une copie dans Drive, puis avancez de haut en bas avec ▶.
Après une modification, relancez la définition **et** la cellule qui l'utilise.
Ne lancez pas tout avant d'avoir suivi les étapes. Travaillez en binôme.
""", """
## The path: chat → request a tool → observe → control → test

Complete **four decisions**, one per checkpoint. Trace helpers and data formats are
provided. Every definition is followed by a cell to run. Executing `def ...` prepares
a function: it does not call it yet.

In Colab: save a copy in Drive, then use ▶ from top to bottom. After editing a function,
rerun its definition **and** the cell that uses it. Do not run everything before following
the steps. Work in pairs.
""")),
        markdown(base.TEXT[language]["brief"] + say(
            '\nDans les règles fictives du lab, la plage est 2–8 °C. Les 12,4 °C sont la mesure actuelle ; les 52 minutes sont la durée hors plage. Il ne s’agit pas d’une moyenne.',
            '\nThe fictional lab uses a 2–8 °C range. 12.4 °C is the current reading; 52 minutes is the time outside that range, not an average.')),
        markdown(base.SETUP_GUIDE[language]),
        code(base.SETUP),
        markdown(say("""
## Les objets fournis : voici ce que vous pouvez utiliser

Le setup importe `make_client` depuis `src.agent`, puis fait `client = make_client(MODE)`.
`make_client("gemini")` crée un `GeminiLLM` ; `make_client("mock")` crée un `MockLLM`.
Ces classes sont fournies dans le dépôt, pas à inventer.

| Expression | Entrée ou résultat |
| --- | --- |
| `client.mode` | Attribut texte : `"gemini"` ou `"mock"`. Aucune parenthèse. |
| `client.complete(messages, tools)` | Méthode : reçoit l'historique et la liste des schémas d'outils ; retourne un `AssistantTurn`. |
| `turn.content` | Texte produit, ou `None`. |
| `turn.tool_calls` | Liste des appels proposés ; peut être vide. |
| `call.id`, `call.name`, `call.arguments` | Identifiant, nom de l'outil et dictionnaire d'arguments. |
| `TOOL_SCHEMAS` | Description des cinq outils : noms, usages, paramètres attendus. |

`selected_client` sera simplement le **paramètre** qui reçoit ce même objet dans nos
fonctions. Exemple : `propose_tool(messages, client)` transmet `client` au paramètre
`selected_client`. Ce nom ne crée aucun modèle.

La cellule suivante inspecte l'objet ; elle n'appelle pas l'API.
""", """
## Provided objects: what you can use

Setup imports `make_client` from `src.agent`, then calls `client = make_client(MODE)`.
`make_client("gemini")` creates a `GeminiLLM`; `make_client("mock")` creates a `MockLLM`.
These classes are provided in the repository.

| Expression | Input or result |
| --- | --- |
| `client.mode` | Text attribute: `"gemini"` or `"mock"`. No parentheses. |
| `client.complete(messages, tools)` | Method: receives history and tool schemas, returns an `AssistantTurn`. |
| `turn.content` | Generated text, or `None`. |
| `turn.tool_calls` | List of proposed calls; may be empty. |
| `call.id`, `call.name`, `call.arguments` | Identifier, tool name and argument dictionary. |
| `TOOL_SCHEMAS` | Five tool descriptions: names, purpose and expected parameters. |

`selected_client` is the **parameter** receiving this object in our functions.
`propose_tool(messages, client)` passes `client` into `selected_client`; the name does
not create a model. The next cell inspects the object without calling the API.
""")),
        code('''
print("class:", type(client).__name__)
print("mode:", client.mode)
print("complete:", callable(client.complete))
print(json.dumps(TOOL_SCHEMAS[0], indent=2, ensure_ascii=False))
'''),
        markdown(say("""
## Première interaction : un chatbot sans outils

**Prédisez :** peut-il connaître la température actuelle de cette clinique sans capteur ?
Lancez la cellule. En Gemini, c'est un appel réel avec `tools=[]` : aucun outil disponible.
En mock, nous affichons un texte de secours écrit à l'avance, clairement annoncé.
Vous pouvez changer la question en Gemini ; le texte de secours, lui, ne s'adapte pas.
Une réponse explique une démarche ; elle ne prouve aucune lecture de capteur.
""", """
## First interaction: a chatbot without tools

**Predict:** can it know the clinic's current temperature without a sensor?
Run the cell. In Gemini this is a real call with `tools=[]`: no tools available.
In mock we show an explicitly labelled, prerecorded fallback text. You may edit the
question in Gemini; the fallback text does not adapt. An explanation proves no sensor reading.
""")),
        code(f'''
chat_question = {say("Une alerte arrive à KCARE-ADJ-01. Sans accès à un capteur, que peux-tu vérifier et que te manque-t-il ? Réponds en deux phrases.", "An alert arrived at KCARE-ADJ-01. Without sensor access, what can you verify and what is missing? Answer in two sentences.")!r}
print("MODE:", client.mode.upper())
if client.mode == "gemini":
    try:
        chat_turn = client.complete([{{"role": "user", "content": chat_question}}], [])
        print(chat_turn.content)
        print("tool_calls:", len(chat_turn.tool_calls))
    except LLMProviderError as exc:
        print("API:", exc, '→ MODE = "mock", puis relancer / then rerun setup.')
else:
    print({say("TEXTE DE SECOURS FIXE — aucun appel IA. Je peux décrire la démarche. Pour connaître l'état actuel, il me faut la mesure du capteur et la procédure applicable.", "FIXED FALLBACK TEXT — no AI call. I can describe the process. To know the current state I need a sensor reading and the applicable procedure.")!r})
'''),
    ]


def exercise_cells(solution, language, base):
    markdown, code = base.markdown, base.code
    fr = language == "fr"
    def say(french, english):
        return french if fr else english
    propose, execute, observe, finish, evaluator = map(clean, base.solution_bodies(language))
    marker = "SOLUTION" if solution else "TODO"
    propose = f'''
def propose_tool(messages, selected_client):
    # {marker} 1: {say("demander un tour avec l'historique et TOOL_SCHEMAS.", "request a turn with history and TOOL_SCHEMAS.")}
    turn = {"selected_client.complete(messages, TOOL_SCHEMAS)" if solution else "None"}
    call = turn.tool_calls[0] if turn is not None and turn.tool_calls else None
    return turn, call
'''
    observe = f'''
def append_observation(messages, turn, call, result):
    assistant_message = {{
        "role": "assistant", "content": turn.content,
        "tool_calls": [call.model_dump()],
    }}
    tool_message = {{
        "role": "tool", "tool_call_id": call.id,
        "name": call.name, "content": result.model_dump_json(),
    }}
    # {marker} 2: {say("ajouter les DEUX messages dans cet ordre avec messages.extend(...).", "append BOTH messages in this order using messages.extend(...).")}
    {"messages.extend([assistant_message, tool_message])" if solution else "pass"}
    return messages
'''
    finish = finish.replace('    if human_required and not human_approved:',
        f'    # {marker} 3: ' + say('bloquer si la revue est requise et non approuvée.', 'block when review is required but not approved.') +
        '\n    if ' + ('human_required and not human_approved' if solution else 'False') + ':')
    evaluator = f'''
def case_passes(row):
    # {marker} 4: {say("tous les booléens de row['checks'] doivent être vrais : utiliser all(...).", "all booleans in row['checks'] must be true: use all(...).")}
    return {"all(row['checks'].values())" if solution else "False"}
'''
    prompt = say("Alerte KCARE-ADJ-01 : prends en charge l'excursion de température, applique la procédure et escalade si nécessaire.", "Investigate the temperature alert at KCARE-ADJ-01, apply the procedure and escalate when required.")
    return [
        markdown(say("""
## Checkpoint 1 : donner des outils au modèle — TODO 1

Nous ajoutons maintenant `TOOL_SCHEMAS` à l'appel du client. Complétez une seule ligne
avec la méthode présentée plus haut : `selected_client.complete(messages, TOOL_SCHEMAS)`.
La sélection du premier appel est fournie. Une liste vide signifie qu'il n'a pas proposé d'outil.

**Prédisez** le nom de l'outil et son argument. Exécutez la définition, puis la cellule
juste dessous : c'est elle qui appelle votre fonction avec `client`, Gemini ou mock.
En Gemini, le résultat peut varier ; on l'observe avant de poursuivre.
""", """
## Checkpoint 1: give the model tools — TODO 1

Pass `TOOL_SCHEMAS` to the client. Complete one line using the method introduced above:
`selected_client.complete(messages, TOOL_SCHEMAS)`. Selecting the first call is provided.
An empty list means no tool was proposed.

**Predict** the tool name and argument. Run the definition and then the next cell, which
calls your function with `client`, Gemini or mock. Gemini output may vary; inspect it first.
""")),
        code(propose),
        code(f'''
preview_messages = [
    {{"role": "system", "content": SYSTEM_PROMPT}},
    {{"role": "user", "content": {prompt!r}}},
]
preview_turn, preview_call = None, None
print("MODE:", client.mode.upper())
try:
    preview_turn, preview_call = propose_tool(preview_messages, client)
    if preview_turn is None:
        print({say("TODO 1 incomplet : relancez la définition corrigée puis cette cellule.", "TODO 1 incomplete: rerun the corrected definition then this cell.")!r})
    else:
        print("content:", preview_turn.content)
        print("tool_calls:", [c.model_dump() for c in preview_turn.tool_calls])
except LLMProviderError as exc:
    print("API:", exc, '→ MODE = "mock", puis relancer / then rerun setup.')
'''),
        markdown(say("""
## Checkpoint 2 : exécuter et observer — TODO 2

L'appel proposé n'est pas encore exécuté. La fonction ci-dessous est **fournie** : lancez-la.
`execute_checked(call, trace, question)` contrôle les arguments et leur provenance, puis
exécute l'outil. Il retourne un `ToolResult` : `ok` (succès), `data` (résultat), `error`
(erreur éventuelle). `TraceEntry` conserve l'appel et ce résultat pour pouvoir les relire.
Nous ne demandons pas de reconstruire ce format.

Ensuite, observez la température et l'entrée de trace. `model_dump()` convertit un objet
de données en dictionnaire ; `model_dump_json()` le convertit en texte JSON. Ce sont des
méthodes de Pydantic, utilisées ici dans le code fourni.
""", """
## Checkpoint 2: execute and observe — TODO 2

A proposed call has not executed yet. The next function is **provided**: run it.
`execute_checked(call, trace, question)` checks arguments and provenance, then executes.
It returns a `ToolResult`: `ok` (success), `data` (result), `error` (possible failure).
`TraceEntry` records the call and result. You do not have to reconstruct that format.

Inspect the reading and trace. `model_dump()` converts a data object to a dictionary;
`model_dump_json()` converts it to JSON text. These are Pydantic methods used by provided code.
""")),
        code(execute),
        code(f'''
preview_result, preview_entry = None, None
if preview_call is None:
    print({say("Revenez au checkpoint 1 : aucun appel disponible.", "Return to checkpoint 1: no call available.")!r})
else:
    preview_result, preview_entry = execute_and_trace(preview_call, 1, [], {prompt!r})
    print("ok:", preview_result.ok)
    print("data:", preview_result.data)
    print("error:", preview_result.error)
    print("trace:", preview_entry.model_dump())
'''),
        markdown(say("""
### Faire parvenir l'observation au prochain tour

Le modèle reçoit uniquement les messages transmis à `complete`. Afficher la trace ne
lui transmet rien. Les deux messages sont construits pour vous : `assistant_message`
conserve la proposition, `tool_message` contient la réponse reliée par `tool_call_id`.
**TODO 2 :** ajoutez-les avec `messages.extend([assistant_message, tool_message])`.

Relancez la définition puis la cellule suivante. Elle repart d'une copie de l'historique
initial pour éviter les doublons. **Avant de lancer :** que devrait demander le modèle
après avoir reçu 12,4 °C et 52 minutes ? Repérez la recherche de procédure.
""", """
### Return the observation to the next turn

The model only receives messages passed to `complete`. Displaying a trace sends it nothing.
Both messages are provided: `assistant_message` records the proposal; `tool_message`
contains the response linked by `tool_call_id`. **TODO 2:** append them with
`messages.extend([assistant_message, tool_message])`.

Rerun the definition and the next cell. It copies the initial history to prevent duplicate
observations. **Predict:** what should the model request after receiving 12.4 °C and
52 minutes? Look for the procedure lookup.
""")),
        code(observe),
        code(f'''
if preview_result is None or not preview_result.ok:
    print({say("Il faut d'abord un résultat d'outil réussi.", "A successful tool result is needed first.")!r})
else:
    observed_messages = list(preview_messages)
    append_observation(observed_messages, preview_turn, preview_call, preview_result)
    print("roles:", [m["role"] for m in observed_messages])
    if len(observed_messages) != len(preview_messages) + 2:
        print({say("TODO 2 incomplet : deux messages doivent être ajoutés.", "TODO 2 incomplete: append both messages.")!r})
    else:
        print("observation:", observed_messages[-1])
        try:
            next_turn, next_call = propose_tool(observed_messages, client)
            print("MODE:", client.mode.upper())
            print("next tool:", next_call.name if next_call else None)
            print("content:", next_turn.content if next_turn else None)
        except LLMProviderError as exc:
            print("API:", exc, '→ MODE = "mock", puis relancer / then rerun setup.')
'''),
        markdown(say("""
## Checkpoint 3 : une boucle, puis une frontière humaine — TODO 3

La boucle ci-dessous est **fournie**. Elle répète ce que vous venez de faire :
proposer → contrôler/exécuter → tracer → ajouter l'observation → recommencer.
Un appel identique est bloqué ; huit tours maximum empêchent une boucle sans fin.

`inspect_evidence(trace, question)` retourne `missing` (preuve manquante ou `None`),
`human_required` (revue requise), `human_approved` (accord pour le bon incident et la bonne action).
`AgentRun` est le résultat final : `answer`, `trace`, `mode`, `outcome`, `safety_status`.
Leur construction est fournie. **Seule la condition du TODO 3 est à compléter.**

Premier passage : gardez `if False`, lancez les deux définitions, puis le contre-exemple.
**Votez :** peut-on accepter une conclusion sans l'approbation requise ?
La solution contient déjà la protection ; la cellule de comparaison montre les deux cas.
""", """
## Checkpoint 3: a loop and a human boundary — TODO 3

The loop is **provided**. It repeats what you just did:
propose → check/execute → trace → append observation → repeat.
Identical calls are blocked; a maximum of eight turns prevents an endless loop.

`inspect_evidence(trace, question)` returns `missing` (missing evidence or `None`),
`human_required` (review needed), `human_approved` (correct incident and action approved).
`AgentRun` contains `answer`, `trace`, `mode`, `outcome`, `safety_status`.
Construction is provided. **Only the TODO 3 condition needs editing.**

First pass: keep `if False`, run both definitions and the counterexample.
**Vote:** can a conclusion without required approval be accepted?
The solution already includes the gate; the comparison cell shows both cases.
""")),
        code(finish),
        code(clean(base.run_loop_body(True))),
        code(base.UNSAFE_CLIENT),
        markdown(say("""
### Corriger puis rejouer exactement la même faute

Remplacez `False` dans TODO 3 par `human_required and not human_approved`.
Relancez `finish_with_safety`, puis le contre-exemple au-dessus : le statut attendu est
`review_required`. Les checkpoints 1 et 2 doivent être terminés, sinon l'arrêt vient d'eux.

La comparaison suivante retire volontairement le contrôle dans une copie temporaire,
puis rejoue avec votre fonction. Le client adverse est un simulateur fourni : il conclut
après trois outils et omet l'approbation. Aucun appel Gemini ici. `safe` dans le cas sans
protection est le **mauvais classement** que nous voulons empêcher.
""", """
### Fix and replay the same fault

Replace `False` in TODO 3 with `human_required and not human_approved`.
Rerun `finish_with_safety`, then the counterexample above: expect `review_required`.
Checkpoints 1 and 2 must be completed or they cause the stop instead.

The comparison below removes the gate in a temporary copy and then uses your function.
The provided adversarial simulator concludes after three tools without approval.
No Gemini call is made. `safe` without the gate is the **incorrect classification** to prevent.
""")),
        code('''
def compare_approval_gate():
    global finish_with_safety
    original = finish_with_safety
    def without_gate(*args, **kwargs):
        run = original(*args, **kwargs)
        if run.safety_status == "review_required":
            return run.model_copy(update={"outcome": "completed", "safety_status": "safe"})
        return run
    try:
        finish_with_safety = without_gate
        reset_operations()
        before = run_workshop_mission("Investigue KCARE-ADJ-01.", UnsafeEarlyAnswerClient())
    finally:
        finish_with_safety = original
    reset_operations()
    after = run_workshop_mission("Investigue KCARE-ADJ-01.", UnsafeEarlyAnswerClient())
    print("Sans contrôle / Without gate:", before.outcome, before.safety_status)
    print("Votre contrôle / Your gate:", after.outcome, after.safety_status)
    print(format_trace(after))

compare_approval_gate()
'''),
        markdown(say("""
### La mission complète avec votre client

Vos quatre fonctions sont reliées par la boucle fournie. Lancez la mission et comparez
la trace avec les cinq étapes : mesure, procédure, risque, incident, revue.
Avec Gemini, les appels sont réels ; avec mock, les choix sont simulés. Les outils métier
et l'opérateur restent fictifs dans les deux modes. Une décision `APPROVED` autorise la
proposition simulée ; elle ne signifie ni stock déclaré utilisable ni réparation effectuée.
""", """
### Full mission with your client

The provided loop connects your functions. Run it and compare the trace with the five
steps: reading, procedure, risk, incident, review. Gemini makes real model calls;
mock simulates the choices. Business tools and operator are fictional in both modes.
`APPROVED` authorizes the simulated proposal; it does not certify stock or repair equipment.
""")),
        code(f'''
reset_operations()
print("MODE:", client.mode.upper())
mission_run = run_workshop_mission({prompt!r}, client)
print(mission_run.answer)
print(format_trace(mission_run))
print(run_summary(mission_run))
display(HTML(incident_dashboard(mission_run, language={language!r})))
'''),
        markdown(say("""
### Votre contre-exemple

Choisissez `altered_measurement` (12,4 remplacé par 5), `rejected_approval` (action refusée)
ou `repeat` (appel répété). Prédisez l'arrêt puis retrouvez sa raison dans la trace.
Ces clients adverses et les protections correspondantes sont fournis ; vous les testez.
Exécutez cette cellule au moins une fois : elle prépare `experiment` pour le dossier final.
""", """
### Your counterexample

Choose `altered_measurement` (12.4 replaced by 5), `rejected_approval` (action rejected)
or `repeat` (repeated call). Predict the stop, then find its reason in the trace.
Adversarial clients and corresponding guards are provided; you test them.
Run this cell at least once: it prepares `experiment` for the final dossier.
""")),
        code('''
fault = "rejected_approval"  # "altered_measurement", "repeat"
reset_operations()
experiment_run = run_workshop_mission("Investigue KCARE-ADJ-01.", AdversarialClient(fault))
print("MODE: MOCK — scénario adverse / adversarial scenario")
print(format_trace(experiment_run))
print(experiment_run.answer)
experiment = {"fault": fault, "observed_status": experiment_run.safety_status}
'''),
        markdown(say("""
## Checkpoint 4 : prouver le comportement — TODO 4

Un cas `row` contient un nom `id` et un dictionnaire `checks` de booléens.
Exemple : `{"id": "exemple", "checks": {"sequence": True, "human": False}}` doit échouer.
`row["checks"].values()` donne les booléens ; `all(...)` exige qu'ils soient tous vrais.
Complétez la fonction puis exécutez le mini-test juste dessous avant les dix scénarios.
Un `PASS` peut signifier que l'agent a correctement **refusé** de continuer.
""", """
## Checkpoint 4: prove the behavior — TODO 4

Each `row` has an `id` and a `checks` dictionary of booleans.
`{"id": "example", "checks": {"sequence": True, "human": False}}` must fail.
`row["checks"].values()` yields the booleans; `all(...)` requires all of them to be true.
Complete the function, run the mini-test below, then run the ten scenarios.
A `PASS` can mean the agent correctly **refused** to continue.
""")),
        code(evaluator),
        code('''
print("Attendu / Expected True:", case_passes({"checks": {"sequence": True, "human": True}}))
print("Attendu / Expected False:", case_passes({"checks": {"sequence": True, "human": False}}))
'''),
        code(base.eval_runner(language)),
        markdown(say("""
## Ce que vous emportez

Le dossier réunit les faits, les appels, la décision simulée et les dix évaluations.
Si le dossier reste verrouillé : corrigez les TODO, relancez leurs définitions, la mission,
votre contre-exemple et les évaluations dans cet ordre. La solution FR/EN peut débloquer
un checkpoint, mais expliquez la ligne copiée avant de continuer.

**À expliquer avec vos mots :** qui propose ? qui exécute ? pourquoi l'accord manquant
bloque-t-il ? quel test le prouve ? Quelle règle ajouteriez-vous dans votre métier ?
""", """
## What you take away

The dossier contains facts, calls, the simulated decision and ten evaluations.
If locked: fix the TODOs, rerun their definitions, the mission, your counterexample and
evaluations in that order. Use the FR/EN solution to unblock a checkpoint, then explain
the copied line before continuing.

**Explain in your own words:** who proposes? who executes? why does missing approval
block the run? which test proves it? What rule would you add for your own work?
""")),
    ]
