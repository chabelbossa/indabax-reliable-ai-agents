from src.tools import (
    HUMAN_REVIEWS,
    INCIDENTS,
    assess_excursion_risk,
    create_incident,
    get_clinic_status,
    request_human_review,
    reset_operations,
    search_cold_chain_sop,
)


def test_critical_clinic_story_reaches_human_approval() -> None:
    reset_operations()
    status = get_clinic_status({"clinic_id": "KCARE-ADJ-01"})
    assert status.ok is True
    assert status.data["temperature_c"] == 12.4

    sop = search_cold_chain_sop({"query": "température supérieure à 8 excursion"})
    assert sop.ok is True
    assert sop.data["id"] == "SOP-TEMP-01"

    risk = assess_excursion_risk(
        {
            "clinic_id": status.data["clinic_id"],
            "temperature_c": status.data["temperature_c"],
            "duration_minutes": status.data["excursion_minutes"],
            "sensor_status": status.data["sensor_status"],
        }
    )
    assert risk.ok is True
    assert risk.data["severity"] == "CRITICAL"
    assert risk.data["human_review_required"] is True

    incident = create_incident(
        {
            "clinic_id": status.data["clinic_id"],
            "severity": risk.data["severity"],
            "summary": "Temperature excursion affecting vaccine lot VX-204.",
        }
    )
    assert incident.ok is True
    assert incident.data["status"] == "AWAITING_HUMAN_REVIEW"

    review = request_human_review(
        {
            "incident_id": incident.data["incident_id"],
            "proposed_action": risk.data["recommended_action"],
            "question": "Approve quarantine and transfer for the affected vaccine stock?",
        }
    )
    assert review.ok is True
    assert review.data["decision"] == "APPROVED"
    assert INCIDENTS[0]["status"] == "HUMAN_APPROVED"
    assert len(HUMAN_REVIEWS) == 1


def test_normal_clinic_does_not_require_human_review() -> None:
    status = get_clinic_status({"clinic_id": "KCARE-OUI-02"})
    risk = assess_excursion_risk(
        {
            "clinic_id": status.data["clinic_id"],
            "temperature_c": status.data["temperature_c"],
            "duration_minutes": status.data["excursion_minutes"],
            "sensor_status": status.data["sensor_status"],
        }
    )
    assert risk.data["severity"] == "LOW"
    assert risk.data["recommended_action"] == "CONTINUE_MONITORING"
    assert risk.data["human_review_required"] is False


def test_offline_sensor_never_claims_stock_is_safe() -> None:
    status = get_clinic_status({"clinic_id": "KCARE-DJO-03"})
    risk = assess_excursion_risk(
        {
            "clinic_id": status.data["clinic_id"],
            "temperature_c": status.data["temperature_c"],
            "duration_minutes": status.data["excursion_minutes"],
            "sensor_status": status.data["sensor_status"],
        }
    )
    assert risk.data["severity"] == "UNKNOWN"
    assert risk.data["recommended_action"] == "MANUAL_INSPECTION"
    assert risk.data["human_review_required"] is True


def test_unknown_clinic_and_unknown_incident_fail_cleanly() -> None:
    reset_operations()
    missing_clinic = get_clinic_status({"clinic_id": "KCARE-XXX-99"})
    assert missing_clinic.ok is False
    assert missing_clinic.error["type"] == "ClinicNotFound"

    missing_incident = request_human_review(
        {
            "incident_id": "INC-999",
            "proposed_action": "MANUAL_INSPECTION",
            "question": "Can an operator inspect this clinic and confirm stock safety?",
        }
    )
    assert missing_incident.ok is False
    assert missing_incident.error["type"] == "IncidentNotFound"


def test_invalid_incident_severity_is_rejected() -> None:
    reset_operations()
    result = create_incident(
        {
            "clinic_id": "KCARE-ADJ-01",
            "severity": "EXTREMELY_URGENT",
            "summary": "Temperature excursion affecting vaccine stock.",
        }
    )
    assert result.ok is False
    assert result.error["type"] == "ValidationError"
    assert INCIDENTS == []


def test_human_operator_rejects_an_action_inconsistent_with_severity() -> None:
    reset_operations()
    incident = create_incident(
        {
            "clinic_id": "KCARE-ADJ-01",
            "severity": "CRITICAL",
            "summary": "Critical temperature excursion affecting vaccine stock.",
        }
    )
    review = request_human_review(
        {
            "incident_id": incident.data["incident_id"],
            "proposed_action": "CONTINUE_MONITORING",
            "question": "Can we continue monitoring without quarantining this critical stock?",
        }
    )
    assert review.ok is True
    assert review.data["decision"] == "REJECTED"
    assert review.data["approved_action"] is None
    assert review.data["expected_action"] == "QUARANTINE_AND_TRANSFER"
    assert INCIDENTS[0]["status"] == "HUMAN_REJECTED"
