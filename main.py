import os
import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai
import anthropic
import psycopg2

# 1. Define strict data schemas for invoice validation
class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class InvoiceData(BaseModel):
    vendor_name: str
    invoice_number: str
    invoice_date: str
    line_items: List[LineItem]
    subtotal: float
    tax: float
    grand_total: float = Field(description="Must equal subtotal + tax")

# 2. Extract structured data from PDF using Gemini 1.5 Pro
def extract_invoice(pdf_path: str) -> InvoiceData:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    uploaded_file = genai.upload_file(pdf_path)
    prompt = (
        "Extract all invoice details and line items from this document. "
        "Verify that line item totals and the grand total match the math."
    )
    
    response = model.generate_content(
        [uploaded_file, prompt],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=InvoiceData,
        ),
    )
    return InvoiceData.model_validate_json(response.text)

# 3. Save validated records to PostgreSQL
def save_to_postgres(invoice: InvoiceData):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO invoices (vendor_name, invoice_number, invoice_date, grand_total, raw_items)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (invoice_number) DO NOTHING;
        """,
        (
            invoice.vendor_name,
            invoice.invoice_number,
            invoice.invoice_date,
            invoice.grand_total,
            json.dumps([item.model_dump() for item in invoice.line_items]),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()

# 4. Generate weekly executive email using Claude 3.5 Sonnet
def draft_weekly_summary(invoices: List[InvoiceData]) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    summary_payload = json.dumps([inv.model_dump() for inv in invoices], indent=2)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=600,
        messages=[
            {
                "role": "user",
                "content": (
                    "Write a concise weekly financial summary email for stakeholders based on "
                    f"these verified invoices. Highlight total spend and top vendors:\n\n{summary_payload}"
                ),
            }
        ],
    )
    return message.content[0].text

if __name__ == "__main__":
    sample_dir = Path("./sample_invoices")
    processed_invoices = []
    
    if sample_dir.exists():
        for pdf_file in sample_dir.glob("*.pdf"):
            data = extract_invoice(str(pdf_file))
            save_to_postgres(data)
            processed_invoices.append(data)
            
    if processed_invoices:
        email_draft = draft_weekly_summary(processed_invoices)
        print("--- WEEKLY EXECUTIVE SUMMARY ---\n")
        print(email_draft)
