# 🚀 Disease-to-Synthea Agentic Pipeline
> Automatically generate **Synthea GMF JSON** modules from trusted biomedical evidence

This project implements an **agentic workflow** that:

🧠 Fetches real evidence from PubMed, PMC & ClinicalTrials.gov  
📄 Extracts additional facts from local PDFs  
🧬 Converts findings into a **Synthea Generic Module**  
👨‍⚕️ Generates **synthetic patient data** using Synthea

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
|----------|-------------|
| 📰 Automated Literature Extraction | PubMed + PMC full text |
| 🧪 Clinical Protocol Retrieval | ClinicalTrials.gov API v2 |
| 📄 PDF Mining | Local research PDF ingestion |
| 🔒 No Hallucination Mode | Must rely only on fetched evidence |
| ✔ JSON Validated | Safe-mode JSON generator w/ tool |
| ⚙ Full CLI Integration | One command runs entire pipeline |

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
└── Validates via json tool

yaml
Copy code

---

## 📂 Project Structure

your-project/
├── agents/
│ ├── disease_profile.py
│ ├── synthea_module.py
│ └── pipeline_agent.py
├── tools/
│ ├── pubmed_api.py
│ ├── clinicaltrials.py
│ ├── pdf_extractor.py
│ └── json_validator.py
├── config/settings.py
├── main.py
├── .env
└── requirements.txt

yaml
Copy code

---

## ⚙️ Setup Guide

### 1️⃣ Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.\.venv\Scripts\activate       # Windows
2️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
3️⃣ Configure environment variables: .env
dotenv
Copy code
NCBI_API_KEY=YOUR_NCBI_API_KEY
GOOGLE_API_KEY=YOUR_GOOGLE_GENAI_API_KEY
⚠️ Keep this file secret — do not commit to GitHub.

🧠 Agents & Behavior
🔹 Disease Profile Agent
Produces a numbered disease profile including:

Prevalence, demographics

Risk factors, etiology, symptoms

Diagnosis, natural history

Treatments & outcomes

🛑 Rule: Must use tools — no invented medical statistics

➡ Output stored in: session.state["disease_profile"]

🔹 Synthea Module Generator Agent
Safe-mode JSON enforcement:

✔ Only allowed Synthea state types
✔ Only direct_transition
✔ Uses placeholders if codes not sourced
✔ Validates JSON before final output

Example placeholder:

json
Copy code
"code": "999999",
"display": "Placeholder SNOMED Concept"
🔹 Root Orchestrator Agent
Runs the entire pipeline:

Build disease profile → store in session state

Generate Synthea JSON → validate → stream final output

🛠 Tools Overview
Tool	Purpose
pubmed_search	Find research metadata
pubmed_get_fulltext_from_pmc	Download and parse PMC full-text
clinicaltrials_search	Find registered clinical trials
clinicaltrials_get_full_content	Full eligibility + arms + results
extract_text_from_pdfs_in_folder	Mine disease data from PDFs
validate_json	Ensures final JSON is valid

🖥 CLI Usage
Run project:

bash
Copy code
python main.py
Example query:

cpp
Copy code
you> Build a disease profile for "Malaria" and generate a Synthea module.
Output example:

json
Copy code
{"name":"Malaria_Module","gmf_version":2,"states":{ ... }}
Exit:

shell
Copy code
you> exit
🧬 Generate Patients with Synthea
bash
Copy code
git clone https://github.com/synthetichealth/synthea.git
cd synthea
./gradlew build -x test
Add your module to:

css
Copy code
src/main/resources/modules/my_custom_module.json
Run Synthea:

bash
Copy code
./gradlew run
Output:

lua
Copy code
output/
 ├─ fhir/
 ├─ csv/
 └─ cda/
🏁 Quick Start Summary
Step	Command
Setup	pip install -r requirements.txt
Run full pipeline	python main.py
Generate patients	./gradlew run

🎉 Synthetic patient data ready for analytics!

📌 Notes for Production
Use real secret storage (Vault / AWS Secrets Manager)

Logging support is included — adjust verbosity as needed

Extend with new tools for more diseases / data sources

🤝 Contributing
PRs welcome — especially enhancements in:

Code mapping (SNOMED/RxNorm)

Clinical workflow logic

Advanced validation rules

📜 License
MIT License — free for research & commercial use.

yaml
Copy code

---

If you want, I can also:
✔ Add a **badge section** (license, Python version, last commit)  
✔ Embed **architecture image** once you send me the PNG  
✔ Add example **input → output screenshots**  
✔ Provide a **GIF demo** for CLI workflow  

Would you like me to include those enhancements too?






