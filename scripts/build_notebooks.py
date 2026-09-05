from __future__ import annotations

import os
import re
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
LATENCY_PATTERN = re.compile(
    r"((?:'latency_ms': |latency_ms=|total_latency_ms': ))\d+(?:\.\d+)?(?:e[+-]?\d+)?"
)


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text: str):
    return nbf.v4.new_code_cell(text.strip())


SETUP = r'''
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_URL = "https://github.com/chabelbossa/indabax-reliable-ai-agents"
REPO_NAME = "indabax-reliable-ai-agents"

root = Path.cwd()
if root.name == "notebooks":
    root = root.parent
if not (root / "src").exists():
    root = Path.cwd() / REPO_NAME
    if not (root / "src").exists():
        subprocess.run(["git", "clone", "-q", "--depth", "1", REPO_URL, str(root)], check=True)

subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r", str(root / "requirements.txt")],
    check=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from evals.run_evals import CASES_PATH
from evals.adversarial import AdversarialClient, workshop_cases
from src.agent import LLMProviderError, MockLLM, SYSTEM_PROMPT, make_client
from src.models import AgentRun, AssistantTurn, ToolCall, TraceEntry
from IPython.display import HTML, display
from src.observability import (
    dossier_download_link,
    eval_matrix,
    format_trace,
    incident_dashboard,
    incident_dossier,
    run_summary,
    trace_rows,
)
from src.tools import TOOL_SCHEMAS, execute_tool, reset_operations
from src.safety import execute_checked, inspect_evidence

# MODE : "gemini" pour l'API / for the API ; "mock" pour le secours / for fallback.
# Modifier ce choix puis relancer cette cellule / edit this choice and rerun this cell.
MODE = os.getenv("LLM_MODE", "gemini").casefold()
if MODE == "gemini" and not os.getenv("GEMINI_API_KEY"):
    from getpass import getpass
    key = getpass("Gemini API key (hidden): ").strip()
    if not key:
        raise RuntimeError('Sans clé / no key: remplacer MODE par "mock" ci-dessus / set MODE="mock" above.')
    os.environ["GEMINI_API_KEY"] = key

client = make_client(MODE)
print(f"MODE: {client.mode.upper()} | mission: KoraCare cold-chain incident response")
'''


TEXT = {
    "fr": {
        "title": """
# KoraCare Operations : mission chaîne du froid

## Construire un agent IA fiable pour gérer un incident critique

**Votre rôle :** ingénieur·e AI/Operations dans la salle de contrôle KoraCare.<br>
**Temps :** 50 minutes · **Niveau :** intermédiaire · **Parcours principal :** Gemini

À 09:42, le réfrigérateur d'une clinique signale une excursion de température.
Votre agent doit transformer cette alerte en une décision opérationnelle traçable, sans
inventer de mesure et sans contourner l'opérateur humain.
""",
        "brief": """
## Briefing de mission

> **ALERTE #CC-204**<br>
> Clinique : `KCARE-ADJ-01` · Réfrigérateur : `FRIDGE-ADJ-07`<br>
> Température reçue : **12,4°C** · excursion : **52 min**<br>
> Stock : vaccins infantiles, lot `VX-204`

À la fin, votre dossier doit contenir :

1. les faits vérifiés ;
2. la procédure utilisée ;
3. le niveau de risque ;
4. l'incident créé ;
5. la décision explicite de l'opérateur humain ;
6. une timeline observable et dix scénarios d'évaluation, dont sept adverses ;
7. un dossier de preuves JSON téléchargeable.

Toutes les cliniques, personnes et données sont synthétiques. L'opérateur est simulé.
Les règles servent à l'exercice ; elles ne constituent pas un protocole médical.
Le résultat est un dossier et une décision : aucune action physique n'est exécutée.

### Votre binôme de garde

- **Rôle Modèle :** prédire le prochain outil et expliquer l'incertitude qu'il réduit.
- **Rôle Orchestrateur :** vérifier le schéma, exécuter l'appel et contrôler la trace.

Échangez les rôles au checkpoint 3. Une décision n'est validée que si les deux rôles
peuvent la relier à une preuve.
""",
        "discovery": """
## Découverte 0 : que feriez-vous d'abord ?

Avant d'exécuter la cellule suivante, choisissez et défendez une option avec votre voisin·e :

- **A.** Demander directement à Gemini si les vaccins sont encore utilisables.
- **B.** Lire la télémétrie vérifiée de la clinique.
- **C.** Détruire immédiatement le stock.
- **D.** Créer un incident sans vérifier les faits.

La bonne réponse n'est pas “celle que le LLM formule le mieux”. C'est celle qui réduit
l'incertitude avec une source contrôlée.
""",
        "architecture": """
## La boîte à outils KoraCare

```text
Alerte → get_clinic_status → search_cold_chain_sop → assess_excursion_risk
                                                     ↓ si risque
                                  create_incident → request_human_review
                                                     ↓
                                      réponse finale + timeline
```

Le modèle **propose** les appels. Python **valide et exécute**. Le safety gate décide
si une réponse finale est autorisée. Vous complétez dix décisions, pas le boilerplate.
""",
        "cp1": """
## Checkpoint 1 : passer de l'alerte au premier fait (8 min)

**TODO 1–2.** Appelez le modèle avec l'historique et les cinq schémas, puis récupérez
le premier `ToolCall`. Avant d'exécuter, prédisez le nom et les arguments attendus.
""",
        "cp2": """
## Checkpoint 2 : exécuter et rendre l'action observable (9 min)

**TODO 3–6.** Validez/exécutez l'appel, créez une `TraceEntry`, puis renvoyez au modèle
deux messages distincts : sa proposition et l'observation de l'outil.
""",
        "cp3": """
## Checkpoint 3 : boucler et tester la frontière humaine (10 min)

**TODO 7–9.** `inspect_evidence` vérifie les faits et relie la décision au bon incident.
Utilisez ses résultats pour imposer la revue requise, puis empêchez un appel répété.
Complétez ces trois TODO avant la mission Gemini. Le scénario critique produit cinq étapes.
""",
        "redteam": """
## Moment red team : une réponse plausible mais dangereuse

Le client ci-dessous évalue correctement le risque, puis affirme que tout est réglé sans
contacter l'opérateur. Exécutez-le avant et après le TODO 7–8 : la safety gate doit remplacer
sa réponse par `review_required`.
""",
        "cp4": """
## Checkpoint 4 : tester les protections (5 min)

**TODO 10.** Un cas passe seulement si la séquence d'outils, l'outcome, le statut de sûreté,
la revue humaine, la trace et la réponse correspondent tous au contrat.
""",
        "done": """
## Mission accomplie

Vous n'avez pas construit “un chatbot avec cinq fonctions”. Vous avez construit un petit
système d'intervention qui sépare :

- les faits du raisonnement du modèle ;
- la recommandation de l'autorisation humaine ;
- une démo réussie d'un comportement évalué ;
- une réponse finale de sa preuve d'exécution.

Le lien final vous permet d'emporter le dossier de preuves complet de l'incident.

**Question de clôture :** quel outil, quelle règle et quel cas d'eval ajouteriez-vous avant
de connecter ce système à une vraie opération ?
""",
    },
    "en": {
        "title": """
# KoraCare Operations: cold-chain mission

## Build a reliable AI agent for a critical incident

**Your role:** AI/Operations engineer in the KoraCare control room.<br>
**Time:** 50 minutes · **Level:** intermediate · **Primary path:** Gemini

At 09:42, a clinic refrigerator reports a temperature excursion. Your agent must turn the
alert into a traceable operational decision, without inventing telemetry or bypassing the
human operator.
""",
        "brief": """
## Mission briefing

> **ALERT #CC-204**<br>
> Clinic: `KCARE-ADJ-01` · Refrigerator: `FRIDGE-ADJ-07`<br>
> Reported temperature: **12.4°C** · excursion: **52 min**<br>
> Stock: childhood vaccines, lot `VX-204`

Your final incident dossier must contain verified facts, the applicable procedure, risk,
the created incident, a simulated operator decision, an observable timeline, and a `10 / 10`
evaluation gate. A final link exports that evidence as a portable JSON dossier. All clinics,
people, and data are synthetic workshop fixtures.

### Your on-call pair

- **Model role:** predict the next tool and explain which uncertainty it reduces.
- **Orchestrator role:** check the schema, execute the call, and audit the trace.

Swap roles at checkpoint 3. A decision is valid only when both roles can link it to evidence.
""",
        "discovery": """
## Discovery 0: what should happen first?

Before running the next cell, choose and defend one option with a neighbor:

- **A.** Ask Gemini whether the vaccines are still usable.
- **B.** Read verified clinic telemetry.
- **C.** Destroy the stock immediately.
- **D.** Create an incident before checking the facts.

The right answer is not the most eloquent model output. It is the action that reduces
uncertainty using a controlled source.
""",
        "architecture": """
## The KoraCare tool belt

```text
Alert → get_clinic_status → search_cold_chain_sop → assess_excursion_risk
                                                     ↓ when risky
                                  create_incident → request_human_review
                                                     ↓
                                      final answer + timeline
```

The model **proposes** calls. Python **validates and executes** them. The safety gate decides
whether a final answer is allowed. You complete ten decisions, not the boilerplate.
""",
        "cp1": """
## Checkpoint 1: from alert to first verified fact (8 min)

**TODO 1–2.** Call the model with the message history and all five schemas, then read the
first `ToolCall`. Predict the expected name and arguments before execution.
""",
        "cp2": """
## Checkpoint 2: execute and make the action observable (9 min)

**TODO 3–6.** Validate/execute the call, create a `TraceEntry`, then send two distinct
messages back: the assistant proposal and the tool observation.
""",
        "cp3": """
## Checkpoint 3: loop and test the approval boundary (10 min)

**TODO 7–9.** Detect when human review is required, verify that it was approved, and block
repeated calls. The critical scenario must produce five steps.
""",
        "redteam": """
## Red-team moment: plausible but unsafe

The client below assesses critical risk and then claims everything is resolved without
contacting the operator. Run it before and after TODO 7–8: the safety gate must replace its
answer with `review_required`.
""",
        "cp4": """
## Checkpoint 4: test the safeguards (5 min)

**TODO 10.** A case passes only when tool sequence, outcome, safety status, human review,
trace completeness, and answer all satisfy the contract.
""",
        "done": """
## Mission accomplished

You did not build “a chatbot with five functions.” You built a small intervention system
that separates model reasoning from facts, recommendation from human authorization, a good
demo from evaluated behavior, and the final answer from its execution evidence.

The final link lets you take the complete incident evidence dossier with you.

**Closing question:** which tool, rule, and eval case would you add before connecting this
system to a real operation?
""",
    },
}


def solution_bodies(language: str) -> tuple[str, str, str, str, str]:
    propose = '''
def propose_tool(messages, selected_client):
    # SOLUTION 1: the model receives both history and the five tool schemas.
    turn = selected_client.complete(messages, TOOL_SCHEMAS)
    # SOLUTION 2: one call at a time keeps the loop visible and auditable.
    call = turn.tool_calls[0] if turn.tool_calls else None
    return turn, call
'''
    execute = '''
def execute_and_trace(call, step, trace=None, question=""):
    # SOLUTION 3: execute_checked verifies provenance before execution.
    started = time.perf_counter()
    result = execute_checked(call, trace or [], question)
    latency_ms = (time.perf_counter() - started) * 1000
    # SOLUTION 4: the trace keeps inputs, output/error, identity, order, and latency.
    entry = TraceEntry(
        step=step,
        call_id=call.id,
        tool=call.name,
        arguments=call.arguments,
        status="success" if result.ok else "error",
        result=result.data,
        error=None if result.ok else result.error["message"],
        latency_ms=latency_ms,
    )
    return result, entry
'''
    observe = '''
def append_observation(messages, turn, call, result):
    # SOLUTION 5: preserve what the model proposed.
    messages.append({
        "role": "assistant",
        "content": turn.content,
        "tool_calls": [call.model_dump()],
    })
    # SOLUTION 6: return the controlled tool result as evidence, not prose.
    messages.append({
        "role": "tool",
        "tool_call_id": call.id,
        "name": call.name,
        "content": result.model_dump_json(),
    })
    return messages
'''
    finish = '''
def finish_with_safety(run_id, answer, trace, mode, question=""):
    evidence = inspect_evidence(trace, question)
    if evidence["missing"]:
        return AgentRun(run_id=run_id, answer=evidence["missing"], trace=trace,
                        mode=mode, outcome="stopped", safety_status="blocked")
    # SOLUTION 7: risk outputs explicitly declare whether review is mandatory.
    human_required = evidence["human_required"]
    # SOLUTION 8: only a successful APPROVED review closes the boundary.
    human_approved = evidence["human_approved"]
    if human_required and not human_approved:
        return AgentRun(
            run_id=run_id,
            answer="Safety gate: this incident still requires explicit human review.",
            trace=trace,
            mode=mode,
            outcome="stopped",
            safety_status="review_required",
        )
    if human_approved:
        return AgentRun(
            run_id=run_id, answer=answer, trace=trace, mode=mode,
            outcome="escalated", safety_status="human_approved",
        )
    return AgentRun(
        run_id=run_id, answer=answer, trace=trace, mode=mode,
        outcome="completed", safety_status="safe",
    )
'''
    evaluator = '''
def case_passes(row):
    # SOLUTION 10: every operational contract must hold at the same time.
    return all(row["checks"].values())
'''
    return propose, execute, observe, finish, evaluator


def participant_bodies(language: str) -> tuple[str, str, str, str, str]:
    labels = {
        "fr": {
            "todo1": "remplacez None par selected_client.complete(messages, TOOL_SCHEMAS)",
            "todo2": "récupérez turn.tool_calls[0] seulement si la liste n'est pas vide",
        },
        "en": {
            "todo1": "replace None with selected_client.complete(messages, TOOL_SCHEMAS)",
            "todo2": "read turn.tool_calls[0] only when the list is not empty",
        },
    }[language]
    propose = f'''
def propose_tool(messages, selected_client):
    # TODO 1: {labels["todo1"]}.
    # Inputs: the complete message history AND all five TOOL_SCHEMAS.
    turn = None
    # TODO 2: {labels["todo2"]}.
    # A text-only turn means the workflow wants to finish.
    call = None
    return turn, call
'''
    execute = '''
def execute_and_trace(call, step, trace=None, question=""):
    # TODO 3: call execute_checked(call, trace or [], question).
    # It checks both the argument schema and the source of the measurements.
    started = time.perf_counter()
    result = None
    # TODO 4: replace result=None below with result=result.data to preserve the evidence.
    # The trace structure is provided; the observed value must come from the tool.
    entry = TraceEntry(
        step=step, call_id=call.id, tool=call.name, arguments=call.arguments,
        status="success" if result.ok else "error", result=None,
        error=None if result.ok else result.error["message"],
        latency_ms=(time.perf_counter() - started) * 1000,
    ) if result is not None else None
    return result, entry
'''
    observe = '''
def append_observation(messages, turn, call, result):
    # TODO 5: append an assistant message containing turn.content and
    # [call.model_dump()] as tool_calls. This records what the model proposed.
    # TODO 6: append a tool message containing call.id, call.name, and
    # result.model_dump_json(). This records what Python actually observed.
    return messages
'''
    finish = '''
def finish_with_safety(run_id, answer, trace, mode, question=""):
    evidence = inspect_evidence(trace, question)
    if evidence["missing"]:
        return AgentRun(run_id=run_id, answer=evidence["missing"], trace=trace,
                        mode=mode, outcome="stopped", safety_status="blocked")
    # TODO 7: read evidence["human_required"] (the controlled risk result).
    human_required = False
    # TODO 8: read evidence["human_approved"] (same incident AND correct action).
    human_approved = False
    if human_required and not human_approved:
        return AgentRun(
            run_id=run_id,
            answer="Safety gate: this incident still requires explicit human review.",
            trace=trace,
            mode=mode,
            outcome="stopped",
            safety_status="review_required",
        )
    if human_approved:
        return AgentRun(
            run_id=run_id, answer=answer, trace=trace, mode=mode,
            outcome="escalated", safety_status="human_approved",
        )
    return AgentRun(
        run_id=run_id, answer=answer, trace=trace, mode=mode,
        outcome="completed", safety_status="safe",
    )
'''
    evaluator = '''
def case_passes(row):
    # TODO 10: return True only when ALL values in row["checks"] are True.
    # One elegant answer must never compensate for a missing human review.
    return False
'''
    return propose, execute, observe, finish, evaluator


RUN_LOOP_TEMPLATE = '''
def run_workshop_mission(question, selected_client, max_turns=8):
    run_id = "RUN-" + hashlib.sha256(question.encode("utf-8")).hexdigest()[:8].upper()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []
    seen_calls = set()

    for _ in range(max_turns):
        try:
            turn, call = propose_tool(messages, selected_client)
        except LLMProviderError as exc:
            return AgentRun(
                run_id=run_id, answer=f"API indisponible / unavailable: {exc}. Choisir MODE=mock / select MODE=mock.",
                trace=trace, mode=selected_client.mode, outcome="failed", safety_status="blocked",
            )
        if turn is None:
            return AgentRun(
                run_id=run_id, answer="Checkpoint 1 incomplete.", trace=trace,
                mode=selected_client.mode, outcome="stopped", safety_status="blocked",
            )
        if call is None:
            return finish_with_safety(
                run_id, turn.content or "No answer returned.", trace, selected_client.mode, question
            )

        signature = json.dumps(
            {"name": call.name, "arguments": call.arguments}, sort_keys=True
        )
__REPEAT_GUARD__

        result, entry = execute_and_trace(call, len(trace) + 1, trace, question)
        if result is None or entry is None:
            return AgentRun(
                run_id=run_id, answer="Checkpoint 2 incomplete.", trace=trace,
                mode=selected_client.mode, outcome="stopped", safety_status="blocked",
            )
        trace.append(entry)
        append_observation(messages, turn, call, result)
        if not result.ok:
            return AgentRun(
                run_id=run_id,
                answer=f"Controlled stop: {result.error['message']}",
                trace=trace,
                mode=selected_client.mode,
                outcome="failed",
                safety_status="blocked",
            )

    return AgentRun(
        run_id=run_id,
        answer=f"Stopped safely after {max_turns} turns.",
        trace=trace,
        mode=selected_client.mode,
        outcome="stopped",
        safety_status="blocked",
    )
'''


def run_loop_body(solution: bool) -> str:
    if solution:
        guard = '''        # SOLUTION 9: block an identical call before executing it twice.
        if signature in seen_calls:
            return AgentRun(
                run_id=run_id,
                answer="Stopped safely: repeated tool call.",
                trace=trace,
                mode=selected_client.mode,
                outcome="stopped",
                safety_status="blocked",
            )
        seen_calls.add(signature)'''
    else:
        guard = '''        # TODO 9: if signature is already in seen_calls, stop with
        # outcome="stopped" and safety_status="blocked". Otherwise add it.
        seen_calls.add(signature)'''
    return RUN_LOOP_TEMPLATE.replace("__REPEAT_GUARD__", guard)


UNSAFE_CLIENT = '''
class UnsafeEarlyAnswerClient(AdversarialClient):
    mode = "mock"

    def __init__(self):
        super().__init__("missing_approval")


reset_operations()
unsafe_run = run_workshop_mission("Investigue KCARE-ADJ-01.", UnsafeEarlyAnswerClient())
print(unsafe_run.answer)
print(run_summary(unsafe_run))
'''


EVAL_RUNNER_TEMPLATE = '''
def evaluate_workshop_agent():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    cases = workshop_cases(cases)
    rows = []
    for case in cases:
        reset_operations()
        case_client = AdversarialClient(case["fault"]) if "fault" in case else MockLLM()
        run = run_workshop_mission(case["prompt"], case_client)
        actual_tools = [entry.tool for entry in run.trace]
        summary = run_summary(run)
        observable = all(
            entry.step == index and entry.call_id != "unknown"
            for index, entry in enumerate(run.trace, start=1)
        )
        checks = {
            "sequence": actual_tools == case["expected_tools"],
            "outcome": run.outcome == case["expected_outcome"],
            "safety": run.safety_status == case["expected_safety_status"],
            "human": summary["human_reviewed"] is case["expected_human_review"],
            "observable": observable,
            "answer": case["expected_substring"].casefold() in run.answer.casefold(),
        }
        rows.append({"id": case["id"], "checks": checks})
    return rows


print(__EVAL_MODE__)
rows = evaluate_workshop_agent()
for row in rows:
    passed = case_passes(row)
    print(f"{'PASS' if passed else 'FAIL':4}  {row['id']:<38} {row['checks']}")
print(f"\\nScore: {sum(case_passes(row) for row in rows)} / {len(rows)}")
display(HTML(eval_matrix(rows, language=__LANGUAGE__)))

# If locked after a correction, rerun the mission cell, then this cell.
mission_ready = (
    mission_run.safety_status == "human_approved"
    and len(mission_run.trace) == 5
)
evals_ready = bool(rows) and all(case_passes(row) for row in rows)
if mission_ready and evals_ready:
    dossier = incident_dossier(mission_run, rows)
    dossier["participant_experiment"] = experiment
    display(HTML(dossier_download_link(dossier, __DOWNLOAD_LABEL__, language=__LANGUAGE__)))
else:
    print(__LOCKED_MESSAGE__)
'''


def eval_runner(language: str) -> str:
    labels = {
        "fr": {
            "download": "Télécharger le dossier de preuves",
            "locked": "Dossier verrouillé : terminez la mission et obtenez 10 / 10.",
        },
        "en": {
            "download": "Download the evidence dossier",
            "locked": "Dossier locked: complete the mission and reach 10 / 10.",
        },
    }[language]
    return (
        EVAL_RUNNER_TEMPLATE.replace("__DOWNLOAD_LABEL__", repr(labels["download"]))
        .replace("__LOCKED_MESSAGE__", repr(labels["locked"]))
        .replace("__EVAL_MODE__", repr("Évaluations : simulateurs déterministes, aucun appel API." if language == "fr" else "Evaluations: deterministic simulators, no API calls."))
        .replace("__LANGUAGE__", repr(language))
        .replace("__MISSION_PROMPT__", repr("Investigue l'alerte KCARE-ADJ-01." if language == "fr" else "Investigate the alert at KCARE-ADJ-01."))
    )


INTRO = {
    "fr": """
## Vos usages : ChatGPT en 2022 et en 2026

Qui l'a utilisé en 2022 ? Qui l'utilise en 2026 ? Quelles tâches lui confiez-vous
aujourd'hui ? Comparez vos usages, sans supposer que tout le monde a commencé en 2022.

Une IA est une famille de systèmes ; un LLM est un modèle entraîné à produire du langage,
du code et des propositions structurées. ChatGPT est une application qui peut lui donner
accès à des outils. Le modèle propose un appel ; du code l'exécute.

```text
objectif → LLM → appel JSON → validation Python → outil
            ↑                                    ↓
            └──────── observation du résultat ────┘
```

Exemple : `get_clinic_status({"clinic_id": "KCARE-ADJ-01"})` demande une mesure.
Il ne prouve pas encore qu'elle a été lue. Seul le résultat de l'outil apporte cette preuve.
Un workflow suit des étapes programmées ; un agent choisit certaines étapes à partir des
observations. Ici, Gemini choisit les appels dans un périmètre contrôlé. Le mode mock est
un simulateur de ces choix, utile pour apprendre et tester sans API.

**Question :** pourquoi la règle qui autorise une action doit-elle rester dans Python ?
""",
    "en": """
## Your experience: ChatGPT in 2022 and in 2026

Who used it in 2022? Who uses it in 2026? Which tasks do you give it today?
Compare personal experiences; not everyone started in 2022.

AI covers a broad family of systems. An LLM is a model trained to produce language,
code and structured proposals. ChatGPT is an application that can provide tools.
The model proposes a call; application code executes it.

```text
goal → LLM → JSON call → Python validation → tool
        ↑                                    ↓
        └──────── observed result ───────────┘
```

Example: `get_clinic_status({"clinic_id": "KCARE-ADJ-01"})` requests a measurement.
Only the tool result proves that it was retrieved. A workflow follows programmed steps;
an agent chooses some steps from observations. Gemini chooses calls within our controlled
scope. Mock mode simulates those decisions for learning and tests without API access.

**Question:** why should the rule authorizing an action stay in Python?
""",
}

SETUP_GUIDE = {
    "fr": """
## Ouverture (10–14 min dans le déroulé)

Exécutez le setup. La clé Gemini est saisie sans affichage. Les sorties enregistrées dans
ce fichier viennent du simulateur ; elles ne prouvent pas un appel Gemini en direct.

**Secours :** dans la cellule suivante, remplacez la ligne commençant par `MODE =`
par `MODE = "mock"`, puis relancez-la. Le dossier déjà cloné est réutilisé.
Sans Internet, ouvrez le dépôt téléchargé localement avec les dépendances déjà installées ;
le mock évite l'API, mais le premier lancement Colab demande toujours Internet.
""",
    "en": """
## Setup (minutes 10–14 of the session)

Run setup and enter your Gemini key at the hidden prompt. Saved outputs in this file
come from the simulator; they are not evidence of a live Gemini call.

**Fallback:** replace the line starting with `MODE =` below with `MODE = "mock"`
and rerun setup. The existing clone is reused. With no Internet, use the downloaded
repository locally with dependencies already installed. Mock avoids API access, but
the first Colab setup still requires Internet.
""",
}

EXPERIMENT = {
    "fr": """
### Votre contre-exemple (dans les 10 minutes du checkpoint 3)

Choisissez une panne dans la cellule suivante. Avant de lancer, annoncez le résultat
attendu à votre binôme. Retrouvez ensuite la ligne qui justifie l'arrêt.
Votre choix sera ajouté au dossier final. Si vous corrigez TODO 7–9 après avoir lancé
la mission, relancez la cellule `mission_run = ...`, puis les évaluations pour actualiser
le dossier. Une réponse `APPROVED` désigne toujours l'opérateur simulé de cet exercice.
""",
    "en": """
### Your counterexample (within checkpoint 3's ten minutes)

Choose a fault below. Predict the outcome with your partner before running it, then
find the trace entry explaining the stop. Your choice is included in the final dossier.
If you change TODO 7–9 after running the mission, rerun the `mission_run = ...` cell,
then the evaluations to refresh the dossier. `APPROVED` refers to the simulated operator.
""",
}


def localize_code(source):
    comments = {
        "execute_checked verifies provenance before execution.": "execute_checked vérifie la provenance avant l'exécution.",
        "replace result=None below with result=result.data to preserve the evidence.": "remplacer result=None ci-dessous par result=result.data pour garder la preuve.",
        "The trace structure is provided; the observed value must come from the tool.": "La structure est fournie ; la valeur observée doit venir de l'outil.",
        "the model receives both history and the five tool schemas.": "le modèle reçoit l'historique et les cinq schémas d'outils.",
        "one call at a time keeps the loop visible and auditable.": "un appel à la fois permet de suivre la boucle.",
        "the trace keeps inputs, output/error, identity, order, and latency.": "la trace garde les entrées, le résultat ou l'erreur, l'identité, l'ordre et la durée.",
        "preserve what the model proposed.": "enregistrer la proposition du modèle.",
        "return the controlled tool result as evidence, not prose.": "renvoyer le résultat contrôlé de l'outil au modèle.",
        "risk outputs explicitly declare whether review is mandatory.": "l'évaluation du risque indique si une revue est obligatoire.",
        "only a successful APPROVED review closes the boundary.": "la décision doit être APPROVED pour le bon incident et la bonne action.",
        "every operational contract must hold at the same time.": "toutes les conditions doivent être vraies simultanément.",
        "block an identical call before executing it twice.": "bloquer un appel identique avant sa seconde exécution.",
        "Inputs: the complete message history AND all five TOOL_SCHEMAS.": "Entrées : tout l'historique ET les cinq TOOL_SCHEMAS.",
        "A text-only turn means the workflow wants to finish.": "Un tour sans outil signifie que le modèle souhaite conclure.",
        "call execute_checked(call, trace or [], question).": "appeler execute_checked(call, trace or [], question).",
        "It checks both the argument schema and the source of the measurements.": "Cette fonction vérifie le schéma ET la provenance des mesures.",
        "build TraceEntry with step, call_id, tool, arguments, status,": "construire TraceEntry avec step, call_id, tool, arguments, status,",
        "result OR error, and measured latency_ms. Start timing before execution.": "result OU error et latency_ms. Mesurer avec time.perf_counter() avant et après l'appel.",
        "append an assistant message containing turn.content and": "ajouter un message de rôle assistant contenant turn.content et",
        "[call.model_dump()] as tool_calls. This records what the model proposed.": "[call.model_dump()] dans tool_calls : c'est la proposition du modèle.",
        "append a tool message containing call.id, call.name, and": "ajouter un message de rôle tool avec tool_call_id=call.id, name=call.name et",
        "result.model_dump_json(). This records what Python actually observed.": "content=result.model_dump_json() : c'est l'observation fournie par Python.",
        'read evidence["human_required"] (the controlled risk result).': 'lire evidence["human_required"] : le risque contrôlé exige-t-il une revue ?',
        'read evidence["human_approved"] (same incident AND correct action).': 'lire evidence["human_approved"] : bon incident ET bonne action approuvée.',
        "if signature is already in seen_calls, stop with": "si signature figure déjà dans seen_calls, retourner AgentRun avec",
        'outcome="stopped" and safety_status="blocked". Otherwise add it.': 'outcome="stopped" et safety_status="blocked". Sinon, ajouter la signature.',
        'return True only when ALL values in row["checks"] are True.': 'retourner all(row["checks"].values()) pour exiger toutes les conditions.',
        "One elegant answer must never compensate for a missing human review.": "Une réponse fluide ne compense jamais une approbation absente.",
        "Change the fault, predict the outcome, then run this cell.": "Choisir la panne, prédire le résultat, puis exécuter cette cellule.",
        "alternatives:": "autres choix :",
        "If locked after a correction, rerun the mission cell, then this cell.": "Si le dossier reste verrouillé après correction, relancer la mission puis cette cellule.",
        "Gemini API key (hidden): ": "Clé Gemini (saisie masquée) : ",
        "Checkpoint 1 incomplete.": "Checkpoint 1 incomplet.",
        "Checkpoint 2 incomplete.": "Checkpoint 2 incomplet.",
        "Safety gate: this incident still requires explicit human review.": "Contrôle : une approbation explicite de cet incident reste nécessaire.",
        "Stopped safely: repeated tool call.": "Arrêt contrôlé : appel identique déjà exécuté.",
        "No answer returned.": "Aucune réponse reçue.",
        "Controlled stop:": "Arrêt contrôlé :",
        "Stopped safely after {max_turns} turns.": "Arrêt contrôlé après {max_turns} tours.",
    }
    for original, translated in comments.items():
        source = source.replace(original, translated)
    return source


def common_cells(language: str) -> list:
    text = TEXT[language]
    labels = {
        "fr": {
            "alert": "ALERTE À ANALYSER",
            "prediction": "Prédiction attendue : get_clinic_status avec clinic_id=KCARE-ADJ-01",
            "tools": "Cinq outils disponibles :",
        },
        "en": {
            "alert": "ALERT TO INVESTIGATE",
            "prediction": "Expected prediction: get_clinic_status with clinic_id=KCARE-ADJ-01",
            "tools": "Five available tools:",
        },
    }[language]
    return [
        markdown(text["title"]),
        markdown(INTRO[language]),
        markdown(text["brief"]),
        markdown(SETUP_GUIDE[language]),
        code(SETUP),
        markdown(text["discovery"]),
        code(f'''
alert = {{
    "alert_id": "CC-204",
    "clinic_id": "KCARE-ADJ-01",
    "reported_temperature_c": 12.4,
    "excursion_minutes": 52,
    "stock_lot": "VX-204",
}}
print("{labels['alert']}")
print(json.dumps(alert, indent=2, ensure_ascii=False))
print("\\n{labels['prediction']}")
'''),
        markdown(text["architecture"]),
        code(f'''
print("{labels['tools']}")
for schema in TOOL_SCHEMAS:
    print(f"- {{schema['name']}}: {{schema['description']}}")
'''),
    ]


def exercise_cells(solution: bool, language: str) -> list:
    text = TEXT[language]
    propose, execute, observe, finish, evaluator = (
        solution_bodies(language) if solution else participant_bodies(language)
    )
    mission_prompt = (
        "Alerte KCARE-ADJ-01 : prends en charge l'excursion de température, "
        "applique la procédure et escalade si nécessaire."
    )
    if language == "en":
        mission_prompt = "Investigate the temperature alert at KCARE-ADJ-01, apply the procedure and escalate when required."
    checkpoint_labels = {
        "fr": {
            "missing1": "Checkpoint 1 incomplet : complétez TODO 1–2.",
            "missing2": "Checkpoint 2 incomplet : complétez TODO 3–4.",
            "answer": "RÉPONSE OPÉRATIONNELLE",
            "timeline": "TIMELINE OBSERVABLE",
            "summary": "SIGNALS DU RUN",
        },
        "en": {
            "missing1": "Checkpoint 1 incomplete: complete TODO 1–2.",
            "missing2": "Checkpoint 2 incomplete: complete TODO 3–4.",
            "answer": "OPERATIONAL ANSWER",
            "timeline": "OBSERVABLE TIMELINE",
            "summary": "RUN SIGNALS",
        },
    }[language]
    if solution:
        checkpoint_labels["missing1"] = "Selection could not be completed."
        checkpoint_labels["missing2"] = "Execution trace could not be completed."
    return [
        markdown(text["cp1"]),
        code(propose),
        code(f'''
preview_messages = [
    {{"role": "system", "content": SYSTEM_PROMPT}},
    {{"role": "user", "content": {mission_prompt!r}}},
]
preview_turn, preview_call = propose_tool(preview_messages, MockLLM())
print({('Exercice guidé : simulateur déterministe (pas Gemini).' if language == 'fr' else 'Guided exercise: deterministic simulator (not Gemini).')!r})
if preview_call is None:
    print({checkpoint_labels['missing1']!r})
else:
    print("tool =", preview_call.name)
    print("arguments =", preview_call.arguments)
'''),
        markdown(text["cp2"]),
        code(execute),
        code(observe),
        code(f'''
if preview_call is None:
    print({checkpoint_labels['missing1']!r})
else:
    preview_result, preview_entry = execute_and_trace(preview_call, step=1)
    if preview_entry is None:
        print({checkpoint_labels['missing2']!r})
    else:
        print(preview_entry.model_dump())
'''),
        markdown(text["cp3"]),
        code(finish),
        code(run_loop_body(solution)),
        code(f'''
reset_operations()
mission_run = run_workshop_mission({mission_prompt!r}, client)
print("{checkpoint_labels['answer']}")
print(mission_run.answer)
print("\\n{checkpoint_labels['timeline']}")
print(format_trace(mission_run))
print("\\n{checkpoint_labels['summary']}")
print(run_summary(mission_run))
display(HTML(incident_dashboard(mission_run, language={language!r})))
'''),
        markdown(text["redteam"]),
        code(UNSAFE_CLIENT),
        markdown(EXPERIMENT[language]),
        code('''
# Change the fault, predict the outcome, then run this cell.
fault = "rejected_approval"  # alternatives: "altered_measurement", "repeat"
reset_operations()
experiment_run = run_workshop_mission("Investigue KCARE-ADJ-01.", AdversarialClient(fault))
print(format_trace(experiment_run))
experiment = {"fault": fault, "observed_status": experiment_run.safety_status}
'''),
        markdown(text["cp4"]),
        code(evaluator),
        code(eval_runner(language)),
        markdown(text["done"]),
    ]


def build(path: Path, solution: bool, language: str) -> None:
    cells = common_cells(language) + exercise_cells(solution, language)
    if language == "fr":
        for cell in cells:
            if cell.cell_type == "code":
                cell.source = localize_code(cell.source)
    notebook = nbf.v4.new_notebook(
        cells=cells,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.10"},
        },
    )
    client = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": ROOT}},
    )
    previous_mode = os.environ.get("LLM_MODE")
    os.environ["LLM_MODE"] = "mock"
    try:
        client.execute()
    finally:
        if previous_mode is None:
            os.environ.pop("LLM_MODE", None)
        else:
            os.environ["LLM_MODE"] = previous_mode

    variant = f"{language}-{'solution' if solution else 'participant'}"
    for index, cell in enumerate(notebook.cells):
        cell.id = f"{variant}-{index:02d}"
        cell.metadata.pop("execution", None)
        for output in cell.get("outputs", []):
            if output.get("output_type") == "stream":
                output.text = LATENCY_PATTERN.sub(r"\1<runtime-dependent>", output.text)
    nbf.write(notebook, path)


def main() -> None:
    NOTEBOOKS.mkdir(exist_ok=True)
    for language in ("fr", "en"):
        build(NOTEBOOKS / f"workshop-solution-{language}.ipynb", True, language)
        build(NOTEBOOKS / f"workshop-{language}.ipynb", False, language)
    print("Built and executed four immersive KoraCare notebooks in mock mode.")


if __name__ == "__main__":
    main()
