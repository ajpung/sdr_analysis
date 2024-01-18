from weasyprint import HTML


def create_report(html: str, out_path: str):
    HTML(html).write_pdf(out_path)
