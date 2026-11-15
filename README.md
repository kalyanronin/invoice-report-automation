# Invoice & Weekly Report Automation Tool

A Python-based automation pipeline that extracts line-item data from PDF invoices and receipts, validates totals, stores structured records in PostgreSQL, and drafts weekly financial summary emails.

## Why I Built This
Manually typing line items from vendor PDFs and compiling weekly expense summaries was taking nearly two full days every week. This tool automates the extraction, math verification, and email drafting process so final review takes around 20 minutes.

## How It Works
1. **PDF Extraction & Validation:** Uses **Gemini 1.5 Pro** with **Pydantic** schemas to parse unstructured PDF invoices into clean, validated JSON objects.
2. **Database Storage:** Inserts verified invoice records and line items into **PostgreSQL**.
3. **Weekly Summary Generation:** Uses **LlamaIndex** and **Claude 3.5 Sonnet** to query the week's database entries and draft a clear executive summary email for stakeholders.

## Tech Stack
* **Models:** Gemini 1.5 Pro, Claude 3.5 Sonnet
* **Frameworks & Libraries:** Python, Pydantic, LlamaIndex, Psycopg2
* **Database:** PostgreSQL

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com
   cd invoice-report-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your environment variables:**
   ```bash
   export GEMINI_API_KEY="your_gemini_key"
   export ANTHROPIC_API_KEY="your_claude_key"
   export DATABASE_URL="postgresql://user:password@localhost:5432/finance_db"
   ```

4. **Run the pipeline:**
   ```bash
   python main.py --input ./sample_invoices
   ```
