"""Build the autonomous French V2: concept, real code, observable result."""
from copy import deepcopy
from pathlib import Path

import build_slides as base
from deck_content import FR, REPO, s


PLAN = []


def add(item, timing, objective, words, question="", answer=""):
    item = deepcopy(item)
    item["notes"] = (
        f"{timing}\nObjectif : {objective}\nÀ dire : {words}"
        + (f"\nQuestion : {question}\nRéponse attendue : {answer}" if question else "")
    )
    PLAN.append(item)


def concepts(label, title, cards, takeaway, timing, objective, words, question="", answer=""):
    add(
        s("cards", label, title, "", cards=cards, takeaway=takeaway),
        timing, objective, words, question, answer,
    )


def python_slide(label, title, code, reading, result, timing, objective, words):
    add(
        s("python", label, title, "", code=code, reading=reading, result=result),
        timing, objective, words,
    )


cover = deepcopy(FR[0])
cover["text"][4] = "Comprendre, construire et vérifier une boucle agentique en Python."
cover["text"][7] = "ATELIER"
add(
    cover, "00:00–00:01", "Annoncer le résultat d’apprentissage.",
    "Nous allons partir d’un modèle qui répond, lui donner des outils, construire sa boucle d’exécution puis vérifier ses décisions.",
)

add(
    s("agenda", "50 MINUTES", "Un concept, son code, puis son comportement observable.", "", rows=[
        ("Comprendre", "Distinguer modèle, outil, agent et application.", "9 min"),
        ("Construire", "Assembler proposition, exécution et observation.", "20 min"),
        ("Fiabiliser", "Valider les preuves et contrôler les actions.", "13 min"),
        ("Évaluer", "Tester les chemins normaux et les refus attendus.", "8 min"),
    ]),
    "00:01–00:02", "Donner la carte de la session.",
    "Chaque bloc commence par l’idée. Le code vient ensuite pour montrer comment cette idée devient un système exécutable.",
)

mission = deepcopy(FR[3])
mission["deliverable"] = "Construire un agent qui rassemble les preuves, prépare l’incident et demande la décision d’un opérateur simulé."
add(
    mission, "00:02–00:04", "Installer un problème concret.",
    "KoraCare est fictif. Nous devons examiner cette alerte sans confondre une réponse plausible avec une exécution prouvée.",
    "Quelle information faut-il vérifier en premier ?", "La mesure actuelle de la clinique.",
)

concepts(
    "COMPRENDRE LE SCÉNARIO", "12,4 °C est une mesure, pas une moyenne.",
    [
        ("Observation", "Le capteur indique 12,4 °C depuis 52 minutes. Son état est OK."),
        ("Règle du lab", "La plage est 2–8 °C. Au-dessus de 8 °C pendant au moins 30 minutes, le cas est CRITICAL."),
        ("Décision attendue", "Consulter la procédure, créer le dossier et obtenir la revue requise avant de conclure."),
    ],
    "Les données, la procédure et l’opérateur sont simulés. Aucune action médicale ou physique n’est exécutée.",
    "00:04–00:06", "Rendre les données et la règle explicites.",
    "La valeur 12,4 n’est ni un seuil ni une moyenne : c’est la mesure lue dans notre jeu de données.",
    "Pourquoi 12,4 °C ne suffit-il pas à lui seul ?", "La durée, l’état du capteur et la procédure comptent aussi.",
)

concepts(
    "1 · DU MODÈLE À L’AGENT", "Un modèle produit une proposition. Une application agit.",
    [
        ("Modèle", "Il reçoit des messages et prédit une réponse : du texte ou un appel structuré."),
        ("Outil", "C’est une fonction écrite par le développeur : lire une donnée, appliquer une règle ou créer un dossier."),
        ("Agent", "C’est l’application qui fait alterner le modèle et les outils jusqu’à une réponse ou un arrêt."),
    ],
    "Le modèle ne découvre pas les fonctions tout seul : l’application lui transmet leurs descriptions.",
    "00:06–00:09", "Poser le vocabulaire avant le code.",
    "Le modèle propose. Notre code décide ce qui est autorisé, exécute les fonctions et conserve les preuves.",
    "Qui exécute réellement un outil ?", "Le programme Python, après contrôle de la proposition.",
)

add(
    s("loop", "LE MÉCANISME", "Un tour transforme une demande en nouvelle information.", "",
      nodes=[
          ("Le modèle propose", "Une réponse ou un appel d’outil à partir de l’historique."),
          ("Python contrôle", "Le nom, les arguments et les règles d’autorisation."),
          ("L’outil s’exécute", "Une fonction renvoie une donnée ou une erreur."),
      ],
      observation="Le résultat devient une observation dans l’historique.",
      return_label="Un nouveau tour peut commencer.",
      stop="Le résultat d’un outil n’est pas automatiquement la réponse finale.",
      exit="Lorsque le modèle répond, Python vérifie les preuves avant de rendre la conclusion."),
    "00:09–00:11", "Présenter le cycle complet avant son implémentation.",
    "Suivons toujours ces quatre moments : proposition, contrôle, exécution, observation.",
)

concepts(
    "2 · DONNER DES OUTILS", "Un outil possède une fonction et un contrat.",
    [
        ("La fonction", "Elle contient le comportement réel. Ici, elle lit les données locales d’une clinique."),
        ("Le schéma", "Il décrit au modèle le nom, le but et les arguments autorisés."),
        ("Le résultat", "Il distingue une réussite avec des données d’un échec explicite."),
    ],
    "Le schéma guide le modèle ; la validation et l’exécution restent dans Python.",
    "00:11–00:13", "Expliquer le contrat d’un outil.",
    "Le modèle voit le schéma. Il ne voit pas ni n’exécute directement le corps de la fonction.",
    "À quoi sert le schéma ?", "À expliquer au modèle comment demander l’outil de manière structurée.",
)

python_slide(
    "PYTHON RÉEL · LE CONTRAT", "Valider les arguments avant de lire les données.",
    '''class ClinicStatusInput(BaseModel):
    clinic_id: str = Field(
        pattern=r"^KCARE-[A-Z]{3}-\\d{2}$"
    )

def get_clinic_status(arguments: dict) -> ToolResult:
    values = ClinicStatusInput.model_validate(arguments)
    clinics = json.loads(CLINICS_PATH.read_text())
    clinic = next(
        (row for row in clinics
         if row["clinic_id"] == values.clinic_id),
        None,
    )
    if clinic is None:
        return ToolResult(ok=False, error={
            "type": "ClinicNotFound",
            "message": f"Unknown clinic: {values.clinic_id}",
        })
    return ToolResult(ok=True, data=clinic)''',
    [
        "ClinicStatusInput impose le format de l’identifiant.",
        "La fonction cherche ensuite la clinique dans un fichier local.",
        "Le résultat annonce clairement succès ou erreur.",
    ],
    "Entrée : KCARE-ADJ-01 → Sortie : 12,4 °C · 52 min · capteur OK",
    "00:13–00:16", "Montrer un outil réel et lisible.",
    "La description guide le modèle ; ce code contrôle l’entrée et produit la donnée qui sera utilisée par la suite.",
)

concepts(
    "3 · PARLER AU MODÈLE", "Le client masque le fournisseur, pas le comportement attendu.",
    [
        ("Une interface stable", "Tous les clients exposent mode et complete(messages, tools)."),
        ("Plusieurs implémentations", "Gemini appelle une API ; MockLLM produit un scénario déterministe hors ligne."),
        ("Une dépendance explicite", "La fonction reçoit client en argument. Elle n’a pas besoin de savoir comment il a été créé."),
    ],
    "complete est une méthode appelée avec des parenthèses ; mode est un attribut lu sans parenthèses.",
    "00:16–00:18", "Expliquer l’abstraction du client avant de l’utiliser.",
    "Le reste de l’agent dépend d’un contrat simple. C’est ce qui permet de changer de fournisseur sans réécrire la boucle.",
    "Comment savons-nous que client possède complete ?", "Le protocole LLMClient définit ce contrat.",
)

python_slide(
    "PYTHON RÉEL · L’INTERFACE", "Définir le contrat, puis injecter le client choisi.",
    '''class LLMClient(Protocol):
    mode: str

    def complete(
        self,
        messages: list[dict],
        tools: list[dict],
    ) -> AssistantTurn: ...

def ask_model(
    state: AgentState,
    client: LLMClient,
) -> AssistantTurn:
    return client.complete(
        state.messages,
        TOOL_SCHEMAS,
    )''',
    [
        "LLMClient annonce les membres disponibles.",
        "client est le paramètre reçu par ask_model.",
        "TOOL_SCHEMAS présente les cinq outils au modèle.",
    ],
    "Même fonction avec Gemini ou MockLLM ; seul l’objet client change.",
    "00:18–00:21", "Rendre complete, mode et client compréhensibles.",
    "Rien n’est caché : le protocole annonce le contrat et la fonction reçoit l’implémentation choisie.",
)

add(
    s("tool_call", "SORTIE DU MODÈLE", "Le modèle propose l’appel ; il ne lit pas encore la clinique.", "",
      labels=["1. AssistantTurn renvoyé", "2. Après exécution de l’outil"],
      code=[
          '{\n  "name": "get_clinic_status",\n  "arguments": {\n    "clinic_id": "KCARE-ADJ-01"\n  }\n}',
          '{\n  "ok": true,\n  "data": {\n    "temperature_c": 12.4,\n    "excursion_minutes": 52\n  }\n}',
      ],
      captions=[
          "Le modèle choisit un nom connu et prépare ses arguments.",
          "Python valide l’appel, exécute la fonction et obtient cette observation.",
      ],
      footnote="Représentation normalisée du scénario simulé ; les valeurs viennent du jeu de données local."),
    "00:21–00:23", "Distinguer proposition et exécution.",
    "Le bloc de gauche est une demande du modèle. Le bloc de droite est le résultat obtenu par Python.",
    "À quel moment connaissons-nous réellement 12,4 °C ?", "Après l’exécution réussie de get_clinic_status.",
)

concepts(
    "4 · CONSERVER L’ÉTAT", "L’agent avance grâce à deux mémoires différentes.",
    [
        ("Historique", "Les messages transmis au modèle : demande, appels proposés et résultats des outils."),
        ("Trace", "Le journal de contrôle : outil, arguments, statut, résultat, erreur et durée."),
        ("Appels déjà vus", "Une empreinte des demandes exécutées permet de bloquer une répétition exacte."),
    ],
    "Sans observation dans l’historique, le modèle ne sait pas ce que l’outil vient de trouver.",
    "00:23–00:25", "Expliquer l’état avant le code d’exécution.",
    "L’historique sert à poursuivre le raisonnement ; la trace sert à vérifier ce qui s’est réellement passé.",
    "Pourquoi conserver les deux ?", "Ils servent à des responsabilités différentes : contexte du modèle et preuve d’exécution.",
)

python_slide(
    "PYTHON RÉEL · L’ÉTAT", "Regrouper ce qui permet de continuer et d’auditer.",
    '''@dataclass
class AgentState:
    question: str
    messages: list[dict]
    trace: list[TraceEntry] = field(
        default_factory=list
    )
    seen_calls: set[str] = field(
        default_factory=set
    )

def create_state(question: str) -> AgentState:
    return AgentState(
        question=question,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )''',
    [
        "La question et les messages lancent la conversation.",
        "La trace est vide au départ.",
        "seen_calls permettra de reconnaître une répétition.",
    ],
    "État initial : 2 messages · 0 outil exécuté · 0 trace",
    "00:25–00:27", "Montrer une abstraction d’état simple.",
    "L’objet AgentState évite de faire circuler quatre variables séparées à chaque fonction.",
)

python_slide(
    "PYTHON RÉEL · EXÉCUTION", "Contrôler, tracer, puis renvoyer l’observation.",
    '''def execute_and_observe(state, call) -> bool:
    signature = json.dumps({
        "name": call.name,
        "arguments": call.arguments,
    }, sort_keys=True)
    if signature in state.seen_calls:
        raise RuntimeError("Repeated tool call blocked")
    state.seen_calls.add(signature)

    started = time.perf_counter()
    result = execute_checked(
        call, state.trace, state.question
    )
    state.trace.append(
        make_trace(state, call, result, started)
    )
    state.messages.append({
        "role": "tool",
        "tool_call_id": call.id,
        "name": call.name,
        "content": result.model_dump_json(),
    })
    return result.ok''',
    [
        "L’empreinte bloque un appel identique déjà exécuté.",
        "execute_checked applique les validations avant l’outil.",
        "Le résultat va dans la trace et dans l’historique.",
    ],
    "Une observation réussie devient le contexte du tour suivant.",
    "00:27–00:30", "Montrer le cœur de l’aller-retour.",
    "make_trace condense ici la construction d’une TraceEntry ; la version exécutable conserve tous ses champs.",
)

add(
    s("table", "LA MISSION COMPLÈTE", "Chaque observation détermine l’information encore nécessaire.", "",
      headers=["Tour", "Appel exécuté", "Observation utile"], widths=[2.0,6.5,9.0],
      row_height=1.05, table_size=22, mono_column=1,
      rows=[
          ("1", "get_clinic_status", "12,4 °C · 52 min · capteur OK"),
          ("2", "search_cold_chain_sop", "Seuil de 8 °C pendant 30 min"),
          ("3", "assess_excursion_risk", "CRITICAL · revue humaine requise"),
          ("4", "create_incident", "Dossier INC-001 créé"),
          ("5", "request_human_review", "APPROVED pour l’action proposée"),
      ],
      takeaway="Après ces cinq observations, la conclusion peut être reliée à des preuves."),
    "00:30–00:33", "Faire parcourir la chaîne de décisions.",
    "À chaque ligne, demandez quelle information manquait avant cet appel et ce que le résultat permet ensuite.",
)

concepts(
    "5 · ORCHESTRER", "La boucle décide quand appeler un outil et quand s’arrêter.",
    [
        ("Si un appel est proposé", "Le programme ajoute la proposition, exécute chaque appel autorisé et renvoie son résultat."),
        ("Si une réponse est proposée", "Le programme examine les preuves avant de la rendre."),
        ("Si rien n’aboutit", "Une limite de tours produit un arrêt explicite au lieu d’une boucle infinie."),
    ],
    "L’agent n’est pas une fonction magique : c’est cette boucle autour du modèle et des outils.",
    "00:33–00:35", "Expliquer la boucle avant son code.",
    "Les fonctions précédentes sont maintenant assemblées. Le modèle propose la suite ; Python garde les limites.",
    "Quelles sont les deux sorties possibles d’un tour ?", "Un ou plusieurs appels d’outils, ou une réponse finale.",
)

python_slide(
    "PYTHON RÉEL · LA BOUCLE", "Assembler les abstractions sans masquer le mécanisme.",
    '''def run_agent(question, client, max_turns=8):
    state = create_state(question)
    for _ in range(max_turns):
        turn = ask_model(state, client)
        if not turn.tool_calls:
            return finish(
                state, turn.content or "No answer"
            )

        state.messages.append({
            "role": "assistant",
            "content": turn.content,
            "tool_calls": [
                call.model_dump()
                for call in turn.tool_calls
            ],
        })
        for call in turn.tool_calls:
            if not execute_and_observe(state, call):
                return {"status": "blocked"}

    return {"status": "blocked",
            "reason": "turn_limit"}''',
    [
        "create_state prépare le contexte.",
        "ask_model produit chaque nouvelle proposition.",
        "execute_and_observe relie outil et observation.",
        "finish contrôle la réponse finale.",
    ],
    "La démo exécutable suit cinq appels puis retourne status = approved.",
    "00:35–00:38", "Montrer l’assemblage final.",
    "Chaque nom correspond à une idée déjà expliquée. La boucle devient lisible parce que les responsabilités sont séparées.",
)

concepts(
    "6 · FIABILISER", "Une sortie structurée peut encore être fausse.",
    [
        ("Validation de forme", "L’outil existe, les champs sont présents et les types sont acceptables."),
        ("Cohérence des preuves", "Les valeurs proposées correspondent aux observations réellement obtenues."),
        ("Autorisation", "Les actions sensibles exigent la décision prévue pour le bon incident."),
    ],
    "La sûreté ne tient pas dans le prompt : elle s’appuie aussi sur des contrôles déterministes.",
    "00:38–00:40", "Élargir la validation au-delà du schéma.",
    "Un modèle peut produire un JSON parfaitement valide avec une température inventée. Il faut comparer avec la trace.",
    "5,0 est-il un argument valide pour une température ?", "Oui pour le type ; non pour la cohérence si le capteur a renvoyé 12,4.",
)

python_slide(
    "PYTHON RÉEL · PREUVE", "Refuser une mesure qui ne vient pas de l’observation.",
    '''if call.name == "assess_excursion_risk":
    status = latest(trace, "get_clinic_status")
    sop = latest(trace, "search_cold_chain_sop")
    if not status or not sop:
        return "Telemetry and SOP required"

    expected = {
        "clinic_id": status["clinic_id"],
        "temperature_c": status["temperature_c"],
        "duration_minutes": status[
            "excursion_minutes"
        ],
        "sensor_status": status["sensor_status"],
    }
    if any(call.arguments.get(key) != value
           for key, value in expected.items()):
        return "Arguments differ from telemetry"''',
    [
        "Le calcul exige d’abord mesure et procédure.",
        "expected est construit depuis la trace.",
        "Chaque argument proposé doit correspondre à cette preuve.",
    ],
    "Proposition temperature_c = 5,0 → appel refusé ; mesure observée = 12,4",
    "00:40–00:43", "Montrer un contrôle de provenance réel.",
    "Le type float ne suffit pas. Cette règle empêche le modèle de modifier silencieusement une observation.",
)

add(
    deepcopy(FR[13]),
    "00:43–00:45", "Montrer que la réponse finale est aussi contrôlée.",
    "Une phrase assurée ne remplace ni le dossier ni la revue. Le système doit donc bloquer cette conclusion.",
    "Pourquoi le résultat correct est-il un arrêt ?", "Parce que les preuves requises pour conclure sont absentes.",
)

python_slide(
    "PYTHON RÉEL · HUMAN-IN-THE-LOOP", "Lier l’accord au bon incident et à la bonne action.",
    '''approved = bool(
    risk["human_review_required"]
    and incident
    and review
    and review["incident_id"]
        == incident["incident_id"]
    and review["decision"] == "APPROVED"
    and review["approved_action"]
        == risk["recommended_action"]
)

if risk["human_review_required"] and not approved:
    return {"status": "review_required"}''',
    [
        "L’accord doit exister et être explicite.",
        "Il doit viser le dossier de cette exécution.",
        "L’action approuvée doit être celle recommandée.",
    ],
    "APPROVED pour un autre incident ou une autre action → conclusion bloquée",
    "00:45–00:47", "Montrer la frontière de décision.",
    "Demander une revue ne suffit pas. Le programme vérifie la décision, son incident et son action.",
)

concepts(
    "7 · ÉVALUER", "Un test utile vérifie le chemin, les preuves et l’arrêt.",
    [
        ("Chemin normal", "Les cinq outils sont appelés dans l’ordre et l’accord conforme permet la conclusion."),
        ("Décision fautive", "Mesure altérée, incident incohérent ou approbation absente doivent être refusés."),
        ("Résultat attendu", "Un scénario d’erreur passe lorsque le système produit précisément l’arrêt attendu."),
    ],
    "10/10 signifie que dix comportements décrits passent ; ce n’est pas une garantie universelle.",
    "00:47–00:48", "Expliquer ce que mesure la suite d’évaluation.",
    "Nous testons le comportement du système, pas seulement la formulation de la dernière réponse.",
)

add(
    deepcopy(FR[14]),
    "00:48–00:49", "Lire un cas normal et un refus attendu.",
    "Le scénario approbation absente est PASS parce que le système produit review_required comme prévu.",
    "Que doit-il arriver si l’on retire la protection correspondante ?", "Ce test doit échouer.",
)

concepts(
    "CE QUE VOUS SAVEZ RECONSTRUIRE", "Une architecture en cinq responsabilités.",
    [
        ("1. Décrire", "Présenter au modèle des outils avec un contrat clair."),
        ("2. Orchestrer", "Alterner propositions, contrôles, exécutions et observations."),
        ("3. Prouver", "Conserver une trace et vérifier la provenance des arguments."),
        ("4. Autoriser", "Exiger une décision humaine liée à l’action sensible."),
        ("5. Évaluer", "Tester les réussites, les erreurs et les refus attendus."),
    ],
    "Le code de démonstration reprend ces cinq responsabilités dans des fonctions séparées.",
    "00:49", "Consolider les acquis.",
    "Même sans avoir codé pendant la séance, vous pouvez maintenant lire la boucle, expliquer ses composants et identifier où placer un contrôle.",
)

add(
    s("resources", "RESSOURCES", "Rejouer la démo, puis explorer l’implémentation complète.", "", links=[
        ("Démonstration Python guidée", "Le code court et exécutable utilisé dans cette présentation.", REPO + "/blob/main/examples/guided_demo.py"),
        ("Notebook solution français", "La mission complète, déjà assemblée, dans Google Colab.", "https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-fr.ipynb"),
        ("Notebook participant français", "Les quatre décisions à compléter pour pratiquer après la session.", "https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb"),
    ]),
    "00:49–00:50", "Donner une suite adaptée à chaque niveau.",
    "Commencez par la démonstration guidée. Passez ensuite au notebook solution, puis au notebook participant si vous voulez reconstruire les décisions.",
)

closing = deepcopy(FR[-1])
closing["title"] = "Une bonne réponse n’est pas une preuve d’exécution."
closing["prompt"] = "Quel outil, quelle preuve et quelle autorisation votre prochain agent devra-t-il posséder ?"
closing["example"] = "Commencez petit : un outil déterministe, une trace lisible et un cas qui doit être refusé."
add(closing, "00:50", "Clore sur le transfert vers leurs projets.", "Laisser le QR et les ressources affichés.")


ORIGINAL_RENDER = base.render


def render(slide, item):
    if item["kind"] != "python":
        return ORIGINAL_RENDER(slide, item)
    base.text(slide, item["label"], 1.25, .78, 17.5, .4, 19, base.GREEN, True)
    base.text(slide, item["title"], 1.25, 1.45, 17.5, 1.3, 40, bold=True)
    base.box(slide, 1.25, 3.0, 10.9, 6.4, base.INK)
    line_count = len(item["code"].splitlines())
    if line_count > 24:
        font_size = 11
    elif line_count > 20:
        font_size = 12
    elif line_count > 16:
        font_size = 14
    else:
        font_size = 17
    base.text(slide, item["code"], 1.55, 3.25, 10.3, 5.95, font_size, "FFFFFF", mono=True)
    base.text(slide, "CE QUE FAIT CE CODE", 12.65, 3.0, 6.1, .5, 18, base.GREEN, True)
    for index, value in enumerate(item["reading"], start=1):
        y = 3.8 + (index - 1) * 1.15
        base.box(slide, 12.65, y, .58, .58, base.GREEN)
        base.text(slide, str(index), 12.65, y + .08, .58, .4, 19, "FFFFFF", True, align=base.PP_ALIGN.CENTER)
        base.text(slide, value, 13.5, y, 5.25, .9, 22)
    base.box(slide, 12.65, 7.8, 6.1, 1.55, base.PALE)
    base.text(slide, item["result"], 12.95, 7.98, 5.5, 1.15, 18, base.GREEN, True)


if __name__ == "__main__":
    base.SOURCE = base.OFFICIAL_TEMPLATE
    base.render = render
    deck = base.build_deck("fr", plan=PLAN, suffix="-v2")
    print(deck)
    print(base.convert_to_pdf(deck))

    guide = [
        "# Guide d’animation — présentation française V2\n",
        "La présentation est autonome : chaque notion est expliquée avant le code qui l’applique. Les blocs marqués « Python réel » correspondent à l’architecture exécutable de `examples/guided_demo.py` ou aux contrôles utilisés par le projet.\n",
        "Le public n’a pas besoin de coder pendant la séance. Il doit cependant pouvoir distinguer modèle, outil, agent, historique et trace ; lire la boucle ; expliquer les contrôles ; et proposer un scénario de test.\n",
    ]
    for index, item in enumerate(PLAN, start=1):
        guide.append(f"## Slide {index:02d} — {item.get('title', 'Couverture')}\n\n{item['notes']}\n")
    (base.ROOT / "slides/GUIDE_ANIMATION_V2_FR.md").write_text(
        "\n".join(guide), encoding="utf-8"
    )
