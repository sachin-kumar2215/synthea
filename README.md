# 🚀 Disease-to-Synthea Agentic Pipeline
> Automatically generate **Synthea GMF JSON** modules from trusted biomedical evidence

This project implements an agentic workflow that:

🧠 Fetches real evidence from PubMed, PMC & ClinicalTrials.gov  
📄 Extracts additional facts from local PDFs  
🧬 Converts findings into a **Synthea Generic Module**  
👨‍⚕️ Generates synthetic patient data using Synthea

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🏗 Architecture](#-architecture)
- [📂 Project Structure](#-project-structure)
- [⚙️ Setup Guide](#️-setup-guide)
- [🧠 Agents & Behavior](#-agents--behavior)
- [🛠 Tools](#-tools)
- [🖥 CLI Usage](#-cli-usage)
- [🧬 Generate Patients with Synthea](#-generate-patients-with-synthea)
- [🏁 Quick Start Summary](#-quick-start-summary)
- [📌 Notes for Production](#-notes-for-production)

---

## ✨ Features

| Capability | Description |
|-----------|-------------|
| 📰 Automated Literature Extraction | PubMed + PMC full text |
| 🧪 Clinical Protocol Retrieval | ClinicalTrials.gov API v2 |
| 📄 PDF Mining | Local research PDF ingestion |
| 🔒 No Hallucination | Must rely only on fetched evidence |
| ✔ JSON Validated | Safe-mode JSON validation tool |
| ⚙ CLI Pipeline | One command runs entire workflow |

---

## 🏗 Architecture

DiseaseToSyntheaPipeline
│
├── disease_profile_agent
│ ├── PubMed + PMC API tools
│ ├── ClinicalTrials.gov API tools
│ └── PDF extractor
│
└── synthea_module_generator_agent
├── Reads state["disease_profile"]
├── Generates safe GMF JSON
└── Validates via JSON tool

## 📂 Project Structure

synthea/
├── agents/
│ ├── disease_profile.py
│ ├── synthea_module.py
│ └── pipeline_agent.py
├── tools/
│ ├── pubmed_api.py
│ ├── clinicaltrials.py
│ ├── pdf_extractor.py
│ └── json_validator.py
├── config/
│ └── settings.py
├── main.py
├── .env
└── requirements.txt

## ⚙️ Setup Guide

### 1️⃣ Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.\.venv\Scripts\activate       # Windows

2️⃣ Install Requirements
pip install -r requirements.txt

3️⃣ Add Environment Variables (.env)
NCBI_API_KEY=YOUR_NCBI_API_KEY
GOOGLE_API_KEY=YOUR_GOOGLE_GENAI_API_KEY

⚠ Do NOT commit .env to version control


🧠 Agents & Behavior
🔹 Disease Profile Agent

* Prevalence and demographics
* Risk factors and etiology
* Symptoms and diagnosis
* Treatments and outcomes

🛑 No hallucinated medical facts
📌 Saves output to: session.state["disease_profile"]


🔹 Synthea Module Generator Agent

Safe-mode JSON enforcement:

✔ Allowed Synthea state types
✔ direct_transition only
✔ Placeholder codes if unavailable
✔ Internal JSON validation loop