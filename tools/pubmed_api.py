import os
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional

from config.settings import NCBI_API_KEY

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def pubmed_search(term: str, max_results: int) -> Dict[str, Any]:
    """
    Search PubMed for a query (e.g. disease name) and return article metadata.

    Public tool #1: SEARCH
    """
    params = {
        "db": "pubmed",
        "term": term,
        "retmode": "json",
        "retmax": max_results,
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    search_resp = requests.get(f"{BASE_URL}/esearch.fcgi", params=params, timeout=20)
    search_resp.raise_for_status()
    pmids = search_resp.json().get("esearchresult", {}).get("idlist", [])

    if not pmids:
        return {"query": term, "results": []}

    summary_params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "json",
    }
    if NCBI_API_KEY:
        summary_params["api_key"] = NCBI_API_KEY

    summary_resp = requests.get(f"{BASE_URL}/esummary.fcgi", params=summary_params, timeout=20)
    summary_resp.raise_for_status()
    data = summary_resp.json().get("result", {})

    articles: List[Dict[str, Any]] = []
    for uid in data.get("uids", []):
        info = data.get(uid, {})
        articles.append(
            {
                "pmid": uid,
                "title": info.get("title"),
                "journal": info.get("fulljournalname"),
                "pubdate": info.get("pubdate"),
                "pub_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
            }
        )

    return {"query": term, "results": articles}


# -------- INTERNAL HELPER (NOT EXPOSED AS TOOL) -------- #

def _get_pubmed_metadata(pmid: str) -> Dict[str, Any]:
    """
    Internal helper: fetch title, journal, pubdate, abstract for a single PubMed article.

    This replaces the old public pubmed_get_article tool.
    """
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY

    resp = requests.get(f"{BASE_URL}/efetch.fcgi", params=params, timeout=20)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)

    article_node = root.find(".//PubmedArticle/MedlineCitation/Article")
    if article_node is None:
        return {
            "pmid": pmid,
            "title": "",
            "journal": "",
            "pubdate": "",
            "abstract": "",
        }

    title = article_node.findtext("ArticleTitle", default="")
    journal = article_node.findtext("Journal/Title", default="")

    pub_date_node = article_node.find(".//JournalIssue/PubDate")
    if pub_date_node is not None:
        year = pub_date_node.findtext("Year", default="")
        month = pub_date_node.findtext("Month", default="")
        day = pub_date_node.findtext("Day", default="")
        pubdate = " ".join([p for p in [year, month, day] if p])
    else:
        pubdate = ""

    abstract_parts: List[str] = []
    for abs_node in article_node.findall(".//Abstract/AbstractText"):
        label = abs_node.attrib.get("Label")
        text = "".join(abs_node.itertext()).strip()
        if not text:
            continue
        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)

    abstract = "\n\n".join(abstract_parts) if abstract_parts else ""

    return {
        "pmid": pmid,
        "title": title,
        "journal": journal,
        "pubdate": pubdate,
        "abstract": abstract,
    }


# -------- PUBLIC TOOL #2: FULL CONTENT EXTRACTOR -------- #

def pubmed_get_fulltext_from_pmc(pmid: str) -> Dict[str, Any]:
    """
    Public tool #2: EXTRACTION

    Try to get full content for a PubMed article via PubMed Central (PMC), if available.

    Flow:
      1. Map PMID -> PMCID via ELink.
      2. Fetch PMC full-text XML.
      3. Extract body text.
      4. Also attach PubMed metadata (title, journal, pubdate, abstract).

    Returns:
        {
          "pmid": "...",
          "pmcid": "PMC..." or None,
          "has_fulltext": bool,
          "title": "...",
          "journal": "...",
          "pubdate": "...",
          "abstract": "...",
          "fulltext": "...",   # may be empty if not available
          "pubmed_url": "...",
          "pmc_url": "...",
          "message": "...",    # if no fulltext or errors
        }
    """
    # 1) map PMID -> PMCID using elink
    elink_params = {
        "dbfrom": "pubmed",
        "db": "pmc",
        "id": pmid,
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        elink_params["api_key"] = NCBI_API_KEY

    elink_resp = requests.get(f"{BASE_URL}/elink.fcgi", params=elink_params, timeout=20)
    elink_resp.raise_for_status()
    elink_root = ET.fromstring(elink_resp.text)

    pmcid: Optional[str] = None
    for id_node in elink_root.findall(".//LinkSetDb/Link/Id"):
        text = (id_node.text or "").strip()
        if text:
            pmcid = text if text.startswith("PMC") else f"PMC{text}"
            break

    # Fetch basic PubMed metadata (title, journal, pubdate, abstract)
    meta = _get_pubmed_metadata(pmid)

    if not pmcid:
        # no full-text, but still return metadata
        return {
            "pmid": pmid,
            "pmcid": None,
            "has_fulltext": False,
            "title": meta.get("title", ""),
            "journal": meta.get("journal", ""),
            "pubdate": meta.get("pubdate", ""),
            "abstract": meta.get("abstract", ""),
            "fulltext": "",
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pmc_url": None,
            "message": "No PMC full-text link found for this PMID.",
        }

    # 2) Fetch full text from PMC
    efetch_params = {
        "db": "pmc",
        "id": pmcid,
        "retmode": "xml",
    }
    if NCBI_API_KEY:
        efetch_params["api_key"] = NCBI_API_KEY

    efetch_resp = requests.get(f"{BASE_URL}/efetch.fcgi", params=efetch_params, timeout=30)
    efetch_resp.raise_for_status()
    pmc_root = ET.fromstring(efetch_resp.text)

    body_node = pmc_root.find(".//body")
    if body_node is None:
        return {
            "pmid": pmid,
            "pmcid": pmcid,
            "has_fulltext": False,
            "title": meta.get("title", ""),
            "journal": meta.get("journal", ""),
            "pubdate": meta.get("pubdate", ""),
            "abstract": meta.get("abstract", ""),
            "fulltext": "",
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "pmc_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/",
            "message": "PMC record found but no <body> element present.",
        }

    paragraphs: List[str] = []
    for p in body_node.iter():
        if p.tag.endswith("p") or p.tag.endswith("sec"):
            text = "".join(p.itertext()).strip()
            if text:
                paragraphs.append(text)

    fulltext = "\n\n".join(paragraphs) if paragraphs else ""

    return {
        "pmid": pmid,
        "pmcid": pmcid,
        "has_fulltext": bool(fulltext),
        "title": meta.get("title", ""),
        "journal": meta.get("journal", ""),
        "pubdate": meta.get("pubdate", ""),
        "abstract": meta.get("abstract", ""),
        "fulltext": fulltext,
        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "pmc_url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/",
        "message": "" if fulltext else "PMC record found but fulltext body is empty.",
    }
