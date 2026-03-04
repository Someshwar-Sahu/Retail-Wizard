import os
import qrcode
from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, 'Retail Wizard', 0, 1, 'C')
        
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Inventory & Point of Sale System', 0, 1, 'C')
        self.cell(0, 5, 'Gandhinagar, Gujarat, India', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_invoice_pdf(invoice_id, customer, payment, items, total,
                         amount_received=0, change_returned=0, card_last4=None,
                         delivery_pincode=None, delivery_address=None, delivery_fee=0.0):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.dirname(current_dir)
    
    static_dir = os.path.join(app_dir, 'static')
    pdf_folder = os.path.join(static_dir, 'bills', 'pdfs')
    qr_folder = os.path.join(static_dir, 'bills', 'qrcodes')
    
    os.makedirs(pdf_folder, exist_ok=True)
    os.makedirs(qr_folder, exist_ok=True)

    pdf_filename = f"invoice_{invoice_id}.pdf"
    qr_filename = f"qr_{invoice_id}.png"
    
    full_pdf_path = os.path.join(pdf_folder, pdf_filename)
    full_qr_path = os.path.join(qr_folder, qr_filename)

    is_upi = str(payment).strip().upper() == "UPI"

    pdf_path = f"bills/pdfs/{pdf_filename}"
    qr_path = f"bills/qrcodes/{qr_filename}" if is_upi else None

    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, f"Invoice #: {invoice_id}")
    pdf.set_font("Arial", "", 10)
    pdf.cell(90, 8, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'R')

    pdf.cell(100, 6, f"Customer: {customer}")
    pdf.cell(90, 6, f"Payment Mode: {payment}", 0, 1, 'R')

    if card_last4 and card_last4 != "0000":
        pdf.cell(190, 6, f"Card Ending: **** {card_last4}", 0, 1, 'R')
        
    pdf.ln(4)

    if delivery_pincode:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 6, "Delivery To:", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 6, f"{delivery_address}\nPIN Code: {delivery_pincode}")
        pdf.ln(4)

    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(90, 8, "Item", 1, 0, 'L', fill=True)
    pdf.cell(25, 8, "Qty", 1, 0, 'C', fill=True)
    pdf.cell(35, 8, "Price", 1, 0, 'R', fill=True)
    pdf.cell(40, 8, "Total", 1, 1, 'R', fill=True)

    pdf.set_font("Arial", "", 10)
    subtotal = 0
    for name, qty, price in items:
        item_total = qty * price
        subtotal += item_total
        pdf.cell(90, 8, name, 1)
        pdf.cell(25, 8, str(qty), 1, 0, 'C')
        pdf.cell(35, 8, f"Rs. {price:.2f}", 1, 0, 'R')
        pdf.cell(40, 8, f"Rs. {item_total:.2f}", 1, 1, 'R')

    pdf.ln(5)

    if delivery_fee > 0:
        pdf.set_font("Arial", "", 10)
        pdf.cell(150, 6, "Subtotal:", 0, 0, 'R')
        pdf.cell(40, 6, f"Rs. {subtotal:.2f}", 0, 1, 'R')
        
        pdf.cell(150, 6, f"Delivery Fee (PIN {delivery_pincode}):", 0, 0, 'R')
        pdf.cell(40, 6, f"Rs. {delivery_fee:.2f}", 0, 1, 'R')

    pdf.set_font("Arial", "B", 12)
    pdf.cell(150, 10, "Grand Total:", 0, 0, 'R')
    pdf.cell(40, 10, f"Rs. {total:.2f}", 0, 1, 'R')

    if str(payment).strip().upper() == "CASH":
        pdf.set_font("Arial", "", 10)
        pdf.cell(150, 6, "Amount Received:", 0, 0, 'R')
        pdf.cell(40, 6, f"{amount_received:.2f}", 0, 1, 'R')
        
        pdf.cell(150, 6, "Change Returned:", 0, 0, 'R')
        pdf.cell(40, 6, f"{change_returned:.2f}", 0, 1, 'R')

    if is_upi:
        if pdf.get_y() > 230:
            pdf.add_page()

        upi_id = "demo_account@upi"
        payee_name = "Retail Wizard"
        payee_name_encoded = payee_name.replace(" ", "%20")
        qr_data = f"upi://pay?pa={upi_id}&pn={payee_name_encoded}&am={total:.2f}&cu=INR"

        qr_img = qrcode.make(qr_data)
        qr_img.save(full_qr_path)

        pdf.image(full_qr_path, x=15, y=pdf.get_y() + 5, w=30)
        pdf.set_y(pdf.get_y() + 15)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(40, 5, "Scan to Pay", 0, 1, 'C')

    pdf.output(full_pdf_path)

    return pdf_path, qr_path
