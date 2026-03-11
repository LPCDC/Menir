import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def create_invoice_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Header / Vendor Info
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, height - 2 * cm, "Facture")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, height - 3.5 * cm, "SwissTech Solutions AG")
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 4 * cm, "IDE: CHE-106.832.063")
    c.drawString(2 * cm, height - 4.5 * cm, "Rue de la Gare 15")
    c.drawString(2 * cm, height - 5 * cm, "1003 Lausanne, Suisse")

    # Client Info (BECO)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(12 * cm, height - 3.5 * cm, "BECO Entreprise")
    c.setFont("Helvetica", 10)
    c.drawString(12 * cm, height - 4 * cm, "Avenue de l'Innovation 1")
    c.drawString(12 * cm, height - 4.5 * cm, "1201 Genève")

    # Invoice Details
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 7 * cm, "Date de facturation: 2024-05-15")
    c.drawString(2 * cm, height - 7.5 * cm, "Numéro de facture: INV-2024-0012")
    c.drawString(2 * cm, height - 8 * cm, "Monnaie: CHF")

    # Line Items Header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2 * cm, height - 10 * cm, "Description")
    c.drawString(12 * cm, height - 10 * cm, "TVA")
    c.drawString(15 * cm, height - 10 * cm, "Montant brut")
    
    c.line(2 * cm, height - 10.2 * cm, 19 * cm, height - 10.2 * cm)

    # Line Item 1
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, height - 11 * cm, "Licence Logiciel Annuelle")
    c.drawString(12 * cm, height - 11 * cm, "8.1 %")
    c.drawString(15 * cm, height - 11 * cm, "1200.00")

    # Line Item 2
    c.drawString(2 * cm, height - 11.8 * cm, "Support Technique (Heures)")
    c.drawString(12 * cm, height - 11.8 * cm, "8.1 %")
    c.drawString(15 * cm, height - 11.8 * cm, "300.00")

    c.line(2 * cm, height - 12.2 * cm, 19 * cm, height - 12.2 * cm)

    # Totals
    c.drawString(12 * cm, height - 13 * cm, "Sous-total:")
    c.drawString(15 * cm, height - 13 * cm, "1500.00")
    
    c.drawString(12 * cm, height - 13.8 * cm, "TVA (8.1 %):")
    c.drawString(15 * cm, height - 13.8 * cm, "121.50")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(12 * cm, height - 14.8 * cm, "Montant Total:")
    c.drawString(15 * cm, height - 14.8 * cm, "1621.50")

    # Footer / Payment Details
    c.setFont("Helvetica", 9)
    c.drawString(2 * cm, 4 * cm, "Merci de régler cette facture dans les 30 jours.")
    c.drawString(2 * cm, 3.5 * cm, "Coordonnées bancaires:")
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2 * cm, 3 * cm, "IBAN: CH93 0900 0000 1234 5678 9")
    
    c.save()

if __name__ == "__main__":
    out_dir = "tests/fixtures"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "invoice_beco_sanitized.pdf")
    create_invoice_pdf(out_path)
    print(f"Generated PDF fixture at: {out_path}")
