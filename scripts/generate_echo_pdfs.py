from reportlab.pdfgen import canvas
import os

def create_pdf(filename, content):
    path = os.path.join("tests", "fixtures", "echo_test", filename)
    c = canvas.Canvas(path)
    textobject = c.beginText()
    textobject.setTextOrigin(100, 750)
    textobject.setFont("Helvetica", 12)
    for line in content.split('\n'):
        textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()
    print(f"Created {path}")

os.makedirs(os.path.join("tests", "fixtures", "echo_test"), exist_ok=True)

create_pdf("IMG_4587.pdf", "FACTURE\nCreditor: Ana Paula\nAmount: 150.00 CHF\nDate: 2026-03-10")
create_pdf("scan_001.pdf", "INVOICE\nSupplier: Pierre Mulller\nTotal: 250.00 CHF\nDate: 2026-03-11")
create_pdf("document.pdf", "Subject: General Update\n\nHello,\nThis is a random letter about Swiss weather.\nNo clients or amounts mentioned here.\nBest regards.")
