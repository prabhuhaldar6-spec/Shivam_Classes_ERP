from fpdf import FPDF


def generate_receipt(student_name: str, amount: float, month: str, receipt_no: str) -> str:
    """Builds a simple PDF fee receipt and saves it to disk.
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

    output_path = f"receipt_{receipt_no}.pdf"
    pdf.output(output_path)
    return output_path
