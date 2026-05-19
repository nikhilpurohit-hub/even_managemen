from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
import io

def generate_certificate(participant_name, event_name, date):
    if not os.path.exists('certificates'):
        os.makedirs('certificates')

    safe_name = "".join([c for c in participant_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    safe_event = "".join([c for c in event_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    filename = f"certificates/{safe_name}_{safe_event}_certificate.pdf".replace(" ", "_")

    c = canvas.Canvas(filename, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background gradient effect
    c.setFillColor(HexColor('#0f0c29'))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Decorative top/bottom bars
    c.setFillColor(HexColor('#302b63'))
    c.rect(0, height - 1.2*inch, width, 1.2*inch, fill=1, stroke=0)
    c.setFillColor(HexColor('#302b63'))
    c.rect(0, 0, width, 1.2*inch, fill=1, stroke=0)

    # Outer border
    c.setStrokeColor(HexColor('#c8a951'))
    c.setLineWidth(5)
    c.rect(0.4*inch, 0.4*inch, width - 0.8*inch, height - 0.8*inch)

    # Inner border
    c.setStrokeColor(HexColor('#ffffff'))
    c.setLineWidth(1.5)
    c.rect(0.55*inch, 0.55*inch, width - 1.1*inch, height - 1.1*inch)

    # Corner decorations
    gold = HexColor('#c8a951')
    for x, y in [(0.5*inch, height-0.5*inch), (width-0.5*inch, height-0.5*inch),
                 (0.5*inch, 0.5*inch), (width-0.5*inch, 0.5*inch)]:
        c.setFillColor(gold)
        c.circle(x, y, 0.1*inch, fill=1, stroke=0)

    # Header text
    c.setFillColor(HexColor('#c8a951'))
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(width/2, height - 0.8*inch, "✦  CERTIFICATE OF PARTICIPATION  ✦")

    # Divider
    c.setStrokeColor(HexColor('#c8a951'))
    c.setLineWidth(1)
    c.line(2*inch, height - 1.5*inch, width - 2*inch, height - 1.5*inch)

    # "This certifies that"
    c.setFillColor(white)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 2.2*inch, "This is to proudly certify that")

    # Participant Name
    c.setFillColor(HexColor('#f6d365'))
    c.setFont("Helvetica-Bold", 38)
    c.drawCentredString(width/2, height - 3.2*inch, participant_name)

    # Underline
    name_width = c.stringWidth(participant_name, "Helvetica-Bold", 38)
    c.setStrokeColor(HexColor('#c8a951'))
    c.setLineWidth(1.5)
    c.line(width/2 - name_width/2, height - 3.4*inch, width/2 + name_width/2, height - 3.4*inch)

    # Body text
    c.setFillColor(white)
    c.setFont("Helvetica", 15)
    c.drawCentredString(width/2, height - 4.1*inch, "has successfully participated in")

    # Event name
    c.setFillColor(HexColor('#a8edea'))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 5.0*inch, event_name)

    # Date
    c.setFillColor(white)
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 5.7*inch, f"Held on: {date}")

    # Divider
    c.setStrokeColor(HexColor('#c8a951'))
    c.setLineWidth(1)
    c.line(2*inch, 1.4*inch, width - 2*inch, 1.4*inch)

    # Signature lines
    c.setStrokeColor(white)
    c.setLineWidth(1)
    c.line(1.5*inch, 1.1*inch, 3.5*inch, 1.1*inch)
    c.setFillColor(HexColor('#c8a951'))
    c.setFont("Helvetica", 11)
    c.drawCentredString(2.5*inch, 0.85*inch, "Event Organizer")

    c.line(width-3.5*inch, 1.1*inch, width-1.5*inch, 1.1*inch)
    c.drawCentredString(width-2.5*inch, 0.85*inch, "Authorized Signatory")

    c.save()
    return filename


def generate_participant_report_pdf(event_name, event_date, participants):
    """Generate a PDF list of all participants for an event."""
    if not os.path.exists('reports'):
        os.makedirs('reports')

    safe_event = "".join([c for c in event_name if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    filename = f"reports/{safe_event}_participants.pdf".replace(" ", "_")

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph(f"<b>Participant Report: {event_name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))

    subtitle = Paragraph(f"Event Date: {event_date} | Total Participants: {len(participants)}", styles['Normal'])
    elements.append(subtitle)
    elements.append(Spacer(1, 0.2*inch))

    table_data = [["#", "Name", "Email", "Phone", "Registered At"]]
    for i, p in enumerate(participants, 1):
        table_data.append([str(i), p[2], p[3], p[4] or "-", p[5]])

    table = Table(table_data, colWidths=[0.4*inch, 1.8*inch, 2.2*inch, 1.2*inch, 1.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#302b63')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f0f0f0'), colors.white]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    doc.build(elements)
    return filename
