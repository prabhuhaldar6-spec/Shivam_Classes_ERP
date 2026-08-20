from fpdf import FPDF


def generate_receipt(
    student_name: str,
    amount: float,
    month: str,
    receipt_no: str,
    total_fee: float = None,
    remaining: float = None,
) -> str:
    """Builds a simple PDF fee receipt and saves it to disk.
    total_fee/remaining are optional — pass them to show the running
    balance on the receipt itself.
    Returns the file path so the caller can upload it or offer it for download.
    """
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Fee Receipt", ln=True, align="C")

    pdf.set_font("Helvetica", "", 12)
    pdf.ln(8)
    pdf.cell(0, 8, f"Receipt No: {receipt_no}", ln=True)
    pdf.cell(0, 8, f"Student Name: {student_name}", ln=True)
    pdf.cell(0, 8, f"Month: {month}", ln=True)
    pdf.cell(0, 8, f"Amount Paid: Rs. {amount}", ln=True)

    if total_fee is not None and remaining is not None:
        pdf.ln(4)
        pdf.cell(0, 8, f"Total Fee: Rs. {total_fee}", ln=True)
        pdf.cell(0, 8, f"Remaining Balance: Rs. {remaining}", ln=True)

    output_path = f"receipt_{receipt_no}.pdf"
    pdf.output(output_path)
    return output_path
