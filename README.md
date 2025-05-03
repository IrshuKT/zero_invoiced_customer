# Non-Invoiced Customers Report - Odoo Module

This Odoo module provides detailed reports for customers who have not received any invoices during a specified date range. The report can be generated in **HTML (preview)**, **Excel (.xlsx)**, or **PDF (.pdf)** format.

## Features

- Filter by custom start and end date
- View report in HTML inside Odoo
- Export report as Excel or PDF
- Shows customer name, last invoice date, and total invoices
- Displays a summary total at the bottom
- Dynamic formatting with styled headers, totals, and borders

## Usage

1. Go to the **Non-Invoiced Customers** menu.
2. Select a **Start Date** and **End Date**.
3. Click on:
   - **Generate** to view the HTML preview
   - **Excel** to download an `.xlsx` file
   - **PDF** to download a `.pdf` file

## Technical Details

- **Model**: `non.invoiced.customer`
- **Languages**: Python (no QWeb templates used)
- **Libraries Used**:
  - [`xlsxwriter`](https://xlsxwriter.readthedocs.io/)
  - [`reportlab`](https://www.reportlab.com/opensource/)

## File Structure

non_invoiced_customer/
├── manifest.py
├── models/
│ └── non_invoiced_customer.py
├── views/
│ └── non_invoiced_customer_view.xml
└── README.md


## Installation

1. Place the module inside your custom addons directory:
   ```bash
   cp -r non_invoiced_customer /odoo/custom_addons/
    Search for "Non-Invoiced Customers" in the menu and use the wizard.

Requirements

Make sure these Python libraries are available in your environment:

pip install xlsxwriter reportlab

Screenshots
HTML Preview
<img width="931" alt="html view" src="https://github.com/user-attachments/assets/e8156536-7fd7-4147-a6b6-e1dfed562a8a" />

Excel Export
<img width="960" alt="excel preview" src="https://github.com/user-attachments/assets/bb877d70-3d4e-4c73-b0f0-794c0fff878f" />

PDF Report
<img width="695" alt="pdf previes" src="https://github.com/user-attachments/assets/5459b376-beea-4fa3-9623-0771716427d0" />

	
	
License

This module is released under the MIT License.
