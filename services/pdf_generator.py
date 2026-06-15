import os
from datetime import datetime, timezone
from fpdf import FPDF


def generate_promotions_report(
    promotions: list,
    filename: str = "promotions_report.pdf",
) -> str:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Promotions Report", ln=True, align="C")

    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 10, f"Generated: {generated_at}", ln=True)
    pdf.cell(0, 10, f"Total promotions: {len(promotions)}", ln=True)

    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(20, 10, "ID", border=1)
    pdf.cell(60, 10, "Title", border=1)
    pdf.cell(30, 10, "Original Price", border=1)
    pdf.cell(35, 10, "Discounted Price", border=1)
    pdf.cell(25, 10, "Discount %", border=1)
    pdf.cell(20, 10, "Active", border=1, ln=True)

    pdf.set_font("Helvetica", "", 9)
    now = datetime.now(timezone.utc)
    for promotion in promotions:
        is_active = "Yes" if promotion.starts_at <= now <= promotion.ends_at else "No"

        pdf.cell(20, 10, str(promotion.id), border=1)
        title = promotion.title[:30] if len(promotion.title) > 30 else promotion.title
        pdf.cell(60, 10, title, border=1)
        pdf.cell(30, 10, f"${promotion.original_price:.2f}", border=1)
        pdf.cell(35, 10, f"${promotion.discounted_price:.2f}", border=1)
        pdf.cell(25, 10, f"{promotion.discount_percent}%", border=1)
        pdf.cell(20, 10, is_active, border=1, ln=True)

    filepath = f"./uploads/{filename}"
    os.makedirs("./uploads", exist_ok=True)
    pdf.output(filepath)

    return filepath
