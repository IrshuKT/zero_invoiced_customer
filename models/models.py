# -*- coding: utf-8 -*-
import base64

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import TableStyle, Table, Spacer, Paragraph, SimpleDocTemplate

from odoo import models, fields, api, _
import io
import xlsxwriter
from odoo.http import request
from datetime import date
from dateutil.relativedelta import relativedelta


#
# try:
#     import xlsxwriter
# except ImportError:
#     _logger.warning("xlsxwriter not installed. Excel export will not work.")


class NonInvoiceCustomer(models.TransientModel):
    _name = 'non.invoiced.customer'
    _description = 'Customers without Invoices'

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: self._default_start_date()
    )

    def _default_start_date(self):
        today = date.today()
        return date(today.year, today.month, 1)
    end_date = fields.Date(
        string='End Date',
        required=True,
        default=lambda self: fields.Date.today()
    )
    report_html = fields.Html(string='Report Preview', store=True)
    partner_id = fields.Many2one('res.partner', string='Customer')
    invoice_count = fields.Integer(string='Invoice Count')
    last_invoice_date = fields.Date(string='Last Invoice Date')
    report_pdf = fields.Binary(string='PDF Report', readonly=True)
    report_excel = fields.Binary(string='Excel Report', readonly=True)
    pdf_filename = fields.Char(string='PDF Filename')
    excel_filename = fields.Char(string='Excel Filename')

    def generate_report(self):
        # Get report data
        report_data = self._get_report_data()

        # Generate HTML report
        html = self._generate_html_report(report_data)

        # Update the report record
        self.write({
            'report_html': html,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_report_data(self):
        """Get all the report data needed for all formats"""
        # Get all customers who were invoiced in the period
        invoiced_customers = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '!=', 'cancel'),
            ('invoice_date', '>=', self.start_date),
            ('invoice_date', '<=', self.end_date),
        ]).mapped('partner_id')

        # Get all active customers
        all_customers = self.env['res.partner'].search([
            ('customer_rank', '>', 0),
            ('active', '=', True),
        ])

        # Find non-invoiced customers
        non_invoiced = all_customers - invoiced_customers

        customers_data = []
        for partner in non_invoiced:
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', '=', 'out_invoice'),
                ('state', '!=', 'cancel'),
            ], order='invoice_date desc')

            customers_data.append({
                'name': partner.name,
                'last_invoice_date': invoices[0].invoice_date if invoices else False,
                'invoice_count': len(invoices),
            })

        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'customers': customers_data,
            'total_count': len(non_invoiced)
        }

    def _generate_html_report(self, data):
        """Generate HTML version of the report"""
        rows = []
        for customer in data['customers']:
            rows.append(f"""
            <tr>
                <td>{customer['name']}</td>
                <td>{customer['last_invoice_date'] or 'Never'}</td>
                <td>{customer['invoice_count']}</td>
            </tr>
            """)

        return f"""
        <h3>Non-Invoiced Customers Report ({data['start_date']} to {data['end_date']})</h3>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Customer</th>
                    <th>Last Invoice Date</th>
                    <th>Total Invoices</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <p>Total Non-Invoiced Customers: {data['total_count']}</p>
        """

    def generate_excel(self):
        data = self._get_report_data()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Non-Invoiced Customers")

        # Formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'border':1
        })
        subtitle_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })
        cell_format = workbook.add_format({'border': 1})
        date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'border': 1
        })

        # === 1) Dynamic Company Name & Report Title & Date Range ===
        company_name = self.env.company.name
        report_title = "Non-Invoiced Customers Details"
        date_range = f"From {data['start_date']} To {data['end_date']}"

        # Merge across columns A:C (0–2)
        worksheet.merge_range(0, 0, 0, 2, company_name, title_format)
        worksheet.merge_range(1, 0, 1, 2, report_title, subtitle_format)
        worksheet.merge_range(2, 0, 2, 2, date_range, subtitle_format)

        # === 2) Column Headers on row 4 (index 3) ===
        headers = ['Customer', 'Last Invoice Date', 'Total Invoices']
        for col, title in enumerate(headers):
            worksheet.write(3, col, title, header_format)

        # === 3) Data Rows starting row 5 (index 4) ===
        for idx, customer in enumerate(data['customers'], start=4):
            worksheet.write(idx, 0, customer['name'], cell_format)
            if customer['last_invoice_date']:
                # write as true date
                worksheet.write_datetime(idx, 1, customer['last_invoice_date'], date_format)
            else:
                worksheet.write(idx, 1, 'Never', cell_format)
            worksheet.write(idx, 2, customer['invoice_count'], cell_format)

        # === 4) Total row after data ===
        total_row = 4 + len(data['customers'])
        worksheet.merge_range(total_row, 0, total_row, 1,
                              "Total Non-Invoiced Customers", header_format)
        worksheet.write(total_row, 2, data['total_count'], header_format)

        # === 5) Fixed Column Widths ===
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 12)

        # Finish up
        workbook.close()
        output.seek(0)

        self.write({
            'report_excel': base64.b64encode(output.read()),
            'excel_filename': f'non_invoiced_customers_{fields.Date.today()}.xlsx',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/report_excel?download=true',
            'target': 'self',
        }

    def generate_pdf(self):
        data = self._get_report_data()
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=20 * mm, rightMargin=20 * mm,
                                topMargin=20 * mm, bottomMargin=20 * mm)

        elements = []
        styles = getSampleStyleSheet()

        # Title Section
        company_name = self.env.company.name
        elements.append(Paragraph(f"<b>{company_name}</b>", styles['Title']))
        elements.append(Paragraph("Non-Invoiced Customers Details", styles['Heading2']))
        elements.append(Paragraph(f"From {data['start_date']} To {data['end_date']}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Table Data
        table_data = [['Customer', 'Last Invoice Date', 'Total Invoices']]
        for customer in data['customers']:
            last_date = customer['last_invoice_date'].strftime('%Y-%m-%d') if customer['last_invoice_date'] else 'Never'
            table_data.append([customer['name'], last_date, str(customer['invoice_count'])])

        # Total row
        table_data.append(['Total Non-Invoiced Customers', '', str(data['total_count'])])

        # Table styling
        table = Table(table_data, colWidths=[90 * mm, 50 * mm, 30 * mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#D7E4BC")),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#D7E4BC")),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)

        self.write({
            'report_pdf': base64.b64encode(buffer.read()),
            'pdf_filename': f'non_invoiced_customers_{fields.Date.today()}.pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/report_pdf?download=true',
            'target': 'self',
        }