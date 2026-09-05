from __future__ import annotations

import base64
import json
from html import escape

from .models import AgentRun


def trace_rows(run: AgentRun) -> list[dict]:
    """Return a notebook-friendly incident timeline without another dependency."""
    return [
        {
            "step": entry.step,
            "tool": entry.tool,
            "status": entry.status,
            "latency_ms": round(entry.latency_ms, 2),
            "decision": _decision(entry.result, entry.error),
        }
        for entry in run.trace
    ]


def run_summary(run: AgentRun) -> dict:
    """Expose the few operational signals participants should learn to inspect."""
    return {
        "run_id": run.run_id,
        "mode": run.mode,
        "outcome": run.outcome,
        "safety_status": run.safety_status,
        "tool_calls": len(run.trace),
        "errors": sum(entry.status == "error" for entry in run.trace),
        "total_latency_ms": round(sum(entry.latency_ms for entry in run.trace), 2),
        "human_reviewed": any(
            entry.tool == "request_human_review" and entry.status == "success"
            for entry in run.trace
        ),
    }


def format_trace(run: AgentRun) -> str:
    """Render a compact text timeline that remains readable in Colab output."""
    lines = [
        f"RUN {run.run_id} | {run.outcome} | safety={run.safety_status}",
        "STEP  TOOL                         STATUS   DECISION",
    ]
    for row in trace_rows(run):
        lines.append(
            f"{row['step']:>4}  {row['tool']:<28} {row['status']:<8} {row['decision']}"
        )
    return "\n".join(lines)


def incident_dashboard(run: AgentRun, language="en") -> str:
    """Render a self-contained incident command view for Jupyter/Colab."""
    facts = _incident_facts(run)
    safety_color = {
        "human_approved": "#087f5b",
        "safe": "#087f5b",
        "review_required": "#e67700",
        "blocked": "#c92a2a",
    }[run.safety_status]
    step_cards = "".join(
        f"""
        <div style="border:1px solid #d9e2dd;border-left:5px solid
          {'#087f5b' if entry.status == 'success' else '#c92a2a'};
          border-radius:10px;padding:10px 12px;background:#fff;min-width:185px;flex:1">
          <div style="font-size:11px;color:#64736b">STEP {entry.step:02d}</div>
          <div style="font-weight:700;font-size:13px;margin:3px 0">{escape(entry.tool)}</div>
          <div style="font-size:12px;color:#415149">{escape(_decision(entry.result, entry.error))}</div>
        </div>
        """
        for entry in run.trace
    ) or "<div style='color:#7a877f'>Complete the checkpoints to populate the timeline.</div>"

    html = f"""
    <section style="font-family:Arial,sans-serif;background:#f4f7f5;border:1px solid #d7e1dc;
      border-radius:18px;padding:20px;color:#102018;margin:12px 0">
      <div style="display:flex;justify-content:space-between;gap:16px;align-items:flex-start">
        <div>
          <div style="font-size:11px;font-weight:700;letter-spacing:1.5px;color:#087f5b">
            KORACARE INCIDENT COMMAND
          </div>
          <h2 style="margin:5px 0 4px">{escape(facts['incident_id'])} · {escape(facts['clinic_id'])}</h2>
          <div style="color:#526159">Run {escape(run.run_id)} · mode={escape(run.mode)}</div>
        </div>
        <div style="background:{safety_color};color:#fff;border-radius:999px;
          padding:9px 14px;font-weight:700">{escape(run.safety_status.upper())}</div>
      </div>
      <div style="display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;margin:18px 0">
        {_metric_card('RISK', facts['risk'])}
        {_metric_card('OUTCOME', run.outcome)}
        {_metric_card('HUMAN DECISION', facts['human_decision'])}
        {_metric_card('TOOL CALLS', str(len(run.trace)))}
      </div>
      <div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#64736b;margin-bottom:8px">
        EXECUTION EVIDENCE
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">{step_cards}</div>
      <div style="margin-top:16px;background:#102018;color:#f5fff9;border-radius:10px;padding:12px 14px">
        <strong>Operational answer</strong><br>{escape(run.answer)}
      </div>
    </section>
    """
    return _localize(html, language)


def eval_matrix(rows: list[dict], language="en") -> str:
    """Render behavior checks as a compact evidence matrix."""
    check_names = list(rows[0]["checks"]) if rows else []
    header = "".join(
        f"<th style='padding:8px;text-align:center;font-size:11px'>{escape(name)}</th>"
        for name in check_names
    )
    body = "".join(
        "<tr>"
        f"<td style='padding:8px;font-weight:600'>{escape(row['id'])}</td>"
        + "".join(
            (
                "<td style='padding:8px;text-align:center;color:#087f5b;font-weight:800'>✓</td>"
                if row["checks"][name]
                else "<td style='padding:8px;text-align:center;color:#c92a2a;font-weight:800'>✕</td>"
            )
            for name in check_names
        )
        + "</tr>"
        for row in rows
    )
    passed = sum(all(row["checks"].values()) for row in rows)
    html = f"""
    <section style="font-family:Arial,sans-serif;border:1px solid #d7e1dc;border-radius:16px;
      padding:18px;margin:12px 0;background:#fff;color:#102018">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
        <div><strong>KoraCare behavior gate</strong><br>
          <span style="font-size:12px;color:#64736b">Sequence + safety + human evidence</span></div>
        <div style="font-size:24px;font-weight:800;color:{'#087f5b' if passed == len(rows) else '#c92a2a'}">
          {passed} / {len(rows)}
        </div>
      </div>
      <div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12px">
        <thead><tr style="background:#eef4f0"><th style="padding:8px;text-align:left">scenario</th>{header}</tr></thead>
        <tbody>{body}</tbody>
      </table></div>
    </section>
    """
    return _localize(html, language)


def incident_dossier(run: AgentRun, rows: list[dict]) -> dict:
    """Build a portable, deterministic evidence bundle for the completed mission."""
    facts = _incident_facts(run)
    passed = sum(all(row["checks"].values()) for row in rows)
    return {
        "schema_version": "koracare.incident-dossier.v1",
        "scope": "Synthetic training scenario; simulated operator; no physical action executed; not medical guidance.",
        "alert_id": "CC-204",
        "incident": facts,
        "run": {
            "run_id": run.run_id,
            "mode": run.mode,
            "outcome": run.outcome,
            "safety_status": run.safety_status,
            "operational_answer": run.answer,
        },
        "execution_evidence": [
            {
                "step": entry.step,
                "call_id": entry.call_id,
                "tool": entry.tool,
                "arguments": entry.arguments,
                "status": entry.status,
                "result": entry.result,
                "error": entry.error,
            }
            for entry in run.trace
        ],
        "evaluation_gate": {
            "passed": passed,
            "total": len(rows),
            "scenarios": rows,
        },
    }


def dossier_download_link(dossier: dict, label: str = "Download incident dossier", language="en") -> str:
    """Return a self-contained Colab download link without writing a secret or file."""
    payload = json.dumps(
        dossier,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    encoded = base64.b64encode(payload).decode("ascii")
    run_id = str(dossier.get("run", {}).get("run_id", "RUN-UNKNOWN"))
    filename = f"koracare-CC-204-{run_id}.json"
    html = f"""
    <div style="font-family:Arial,sans-serif;border:1px solid #8ad0b5;border-radius:14px;
      padding:16px 18px;margin:12px 0;background:#effaf5;color:#102018">
      <strong>Evidence bundle unlocked</strong><br>
      <span style="font-size:12px;color:#526159">Portable facts, trace, human decision and eval gate.</span><br>
      <a download="{escape(filename)}" href="data:application/json;base64,{encoded}"
        style="display:inline-block;margin-top:10px;background:#087f5b;color:white;text-decoration:none;
        border-radius:8px;padding:9px 13px;font-weight:700">{escape(label)}</a>
    </div>
    """
    return _localize(html, language)


def _localize(html, language):
    if language != "fr":
        return html
    labels = {
        "KORACARE INCIDENT COMMAND": "KORACARE · DOSSIER D'INCIDENT SIMULÉ",
        "STEP ": "ÉTAPE ", "RISK": "RISQUE", "OUTCOME": "RÉSULTAT",
        "HUMAN DECISION": "OPÉRATEUR SIMULÉ", "TOOL CALLS": "APPELS D'OUTILS",
        "EXECUTION EVIDENCE": "PREUVES D'EXÉCUTION", "Operational answer": "Réponse de l'agent",
        "KoraCare behavior gate": "KoraCare · Évaluation des comportements",
        "Sequence + safety + human evidence": "Séquence, contrôles et décision de l'opérateur simulé",
        "Evidence bundle unlocked": "Dossier de preuves disponible",
        "Portable facts, trace, human decision and eval gate.": "Faits, trace, décision simulée et résultats des évaluations.",
        "Complete the checkpoints to populate the timeline.": "Complétez les étapes pour afficher la trace.",
    }
    for source, target in labels.items():
        html = html.replace(source, target)
    return html


def _decision(result, error: str | None) -> str:
    if error:
        return error.splitlines()[0][:72]
    if not isinstance(result, dict):
        return "completed"
    for key in (
        "decision",
        "severity",
        "status",
        "recommended_action",
        "clinic_id",
        "id",
    ):
        if key in result:
            return f"{key}={result[key]}"
    return "completed"


def _incident_facts(run: AgentRun) -> dict[str, str]:
    facts = {
        "clinic_id": "PENDING",
        "incident_id": "INCIDENT PENDING",
        "risk": "PENDING",
        "human_decision": "PENDING",
    }
    for entry in run.trace:
        if not isinstance(entry.result, dict):
            continue
        facts["clinic_id"] = str(entry.result.get("clinic_id", facts["clinic_id"]))
        facts["incident_id"] = str(entry.result.get("incident_id", facts["incident_id"]))
        facts["risk"] = str(entry.result.get("severity", facts["risk"]))
        facts["human_decision"] = str(
            entry.result.get("decision", facts["human_decision"])
        )
    return facts


def _metric_card(label: str, value: str) -> str:
    return f"""
    <div style="background:#fff;border:1px solid #d9e2dd;border-radius:10px;padding:10px 12px">
      <div style="font-size:10px;color:#64736b;letter-spacing:1px">{escape(label)}</div>
      <div style="font-size:14px;font-weight:800;margin-top:4px">{escape(value)}</div>
    </div>
    """
