# tools/clinicaltrials.py
import time
import requests
from typing import Dict, Any, List

CT_BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

# Simple in-memory caches
_CT_SEARCH_CACHE: Dict[str, Any] = {}
_CT_STUDY_CACHE: Dict[str, Any] = {}


def clinicaltrials_search(condition: str, max_results: int) -> Dict[str, Any]:
    """
    Search ClinicalTrials.gov for studies matching a condition/disease.

    Args:
        condition: Disease or condition name (e.g. "type 2 diabetes").
        max_results: Max number of trials to return.

    Returns:
        {
          "query": "...",
          "count": <int>,
          "results": [ { ... }, ... ],
          "error": null | "message"
        }
    """
    condition = condition.strip()
    if max_results <= 0:
        max_results = 1
    max_results = min(max_results, 50)

    cache_key = f"{condition}::{max_results}"
    if cache_key in _CT_SEARCH_CACHE:
        return _CT_SEARCH_CACHE[cache_key]

    params = {
        "query.term": condition,
        "pageSize": max_results,
    }

    attempts = 0
    last_error: str | None = None
    data: Dict[str, Any] | None = None

    while attempts < 2:
        attempts += 1
        try:
            resp = requests.get(CT_BASE_URL, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            last_error = None
            break
        except requests.exceptions.RequestException as e:
            last_error = f"Error calling ClinicalTrials.gov search API: {e}"
            time.sleep(1.0)  # small backoff then retry

    if data is None:
        result = {
            "query": condition,
            "count": 0,
            "results": [],
            "error": last_error or "Unknown error calling ClinicalTrials.gov search API.",
        }
        _CT_SEARCH_CACHE[cache_key] = result
        return result

    studies: List[Dict[str, Any]] = []

    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})

        # IDs & titles
        ident = protocol.get("identificationModule", {})
        nct_id = ident.get("nctId")
        brief_title = ident.get("briefTitle")
        official_title = ident.get("officialTitle")

        # Status
        status_module = protocol.get("statusModule", {})
        overall_status = status_module.get("overallStatus")

        # Conditions
        conditions_module = protocol.get("conditionsModule", {})
        conditions = conditions_module.get("conditions", [])

        # Design / phase
        design_module = protocol.get("designModule", {})
        phases = design_module.get("phases", [])
        study_type = design_module.get("studyType")

        # Dates
        start_date = status_module.get("startDateStruct", {}).get("date")
        completion_date = status_module.get("completionDateStruct", {}).get("date")

        studies.append(
            {
                "nct_id": nct_id,
                "brief_title": brief_title,
                "official_title": official_title,
                "overall_status": overall_status,
                "conditions": conditions,
                "phases": phases,
                "study_type": study_type,
                "start_date": start_date,
                "completion_date": completion_date,
                "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else None,
            }
        )

    result = {
        "query": condition,
        "count": len(studies),
        "results": studies,
        "error": None,
    }
    _CT_SEARCH_CACHE[cache_key] = result
    return result


def clinicaltrials_get_full_content(nct_id: str) -> Dict[str, Any]:
    """
    Get rich 'full content' for a ClinicalTrials.gov study.

    This includes:
      - titles, status, phase, type
      - detailed description & brief summary
      - eligibility criteria
      - arms & interventions
      - primary/secondary/other outcomes
      - locations (if present)
      - and the raw JSON if you want to mine more later.

    Returns:
        {
          "nct_id": "...",
          "brief_title": "...",
          ...
          "raw": { ... },
          "error": null | "message"
        }
    """
    nct_id = nct_id.strip()
    if not nct_id:
        return {
            "nct_id": nct_id,
            "error": "Empty NCT ID.",
        }

    if nct_id in _CT_STUDY_CACHE:
        return _CT_STUDY_CACHE[nct_id]

    url = f"{CT_BASE_URL}/{nct_id}"

    attempts = 0
    last_error: str | None = None
    data: Dict[str, Any] | None = None

    while attempts < 2:
        attempts += 1
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            last_error = None
            break
        except requests.exceptions.RequestException as e:
            last_error = f"Error calling ClinicalTrials.gov study API for {nct_id}: {e}"
            time.sleep(1.0)  # small backoff then retry

    if data is None:
        result = {
            "nct_id": nct_id,
            "error": last_error or "Unknown error calling ClinicalTrials.gov study API.",
        }
        _CT_STUDY_CACHE[nct_id] = result
        return result

    protocol = data.get("protocolSection", {})

    # Identification
    identification = protocol.get("identificationModule", {})
    brief_title = identification.get("briefTitle")
    official_title = identification.get("officialTitle")

    # Status
    status_module = protocol.get("statusModule", {})
    overall_status = status_module.get("overallStatus")
    start_date = status_module.get("startDateStruct", {}).get("date")
    completion_date = status_module.get("completionDateStruct", {}).get("date")

    # Conditions
    conditions_module = protocol.get("conditionsModule", {})
    conditions = conditions_module.get("conditions", [])

    # Description
    description_module = protocol.get("descriptionModule", {})
    brief_summary = description_module.get("briefSummary")
    detailed_description = description_module.get("detailedDescription")

    # Eligibility
    eligibility_module = protocol.get("eligibilityModule", {})
    eligibility_criteria = eligibility_module.get("eligibilityCriteria")
    healthy_volunteers = eligibility_module.get("healthyVolunteers")
    sex = eligibility_module.get("sex")
    minimum_age = eligibility_module.get("minimumAge")
    maximum_age = eligibility_module.get("maximumAge")

    # Design
    design_module = protocol.get("designModule", {})
    study_type = design_module.get("studyType")
    phases = design_module.get("phases", [])
    allocation = design_module.get("allocation")
    intervention_model = design_module.get("interventionModel")
    masking = design_module.get("masking")
    primary_purpose = design_module.get("primaryPurpose")

    # Arms & Interventions
    arms_module = protocol.get("armsInterventionsModule", {})
    arm_groups = arms_module.get("armGroups", [])
    interventions = arms_module.get("interventions", [])

    # Outcomes
    outcomes_module = protocol.get("outcomesModule", {})
    primary_outcomes = outcomes_module.get("primaryOutcomes", [])
    secondary_outcomes = outcomes_module.get("secondaryOutcomes", [])
    other_outcomes = outcomes_module.get("otherOutcomes", [])

    # Locations
    contacts_locations_module = protocol.get("contactsLocationsModule", {})
    locations = contacts_locations_module.get("locations", [])

    result = {
        "nct_id": nct_id,
        "brief_title": brief_title,
        "official_title": official_title,
        "overall_status": overall_status,
        "conditions": conditions,
        "study_type": study_type,
        "phases": phases,
        "allocation": allocation,
        "intervention_model": intervention_model,
        "masking": masking,
        "primary_purpose": primary_purpose,
        "start_date": start_date,
        "completion_date": completion_date,
        "brief_summary": brief_summary,
        "detailed_description": detailed_description,
        "eligibility_criteria": eligibility_criteria,
        "healthy_volunteers": healthy_volunteers,
        "sex": sex,
        "minimum_age": minimum_age,
        "maximum_age": maximum_age,
        "arm_groups": arm_groups,
        "interventions": interventions,
        "primary_outcomes": primary_outcomes,
        "secondary_outcomes": secondary_outcomes,
        "other_outcomes": other_outcomes,
        "locations": locations,
        "url": f"https://clinicaltrials.gov/study/{nct_id}",
        "raw": data,
        "error": None,
    }
    _CT_STUDY_CACHE[nct_id] = result
    return result
