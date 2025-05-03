{
    'name': "zero_invoiced_customers",
    'version': '1.0.0',
    'summary': "Find zero-invoiced customers from invoices",
    'description': """
        This module identifies inactive customers (rank=0) who have not been invoiced.
        It reports these customers along with their last invoice date, even if outside the selected period.
    """,
    'author': "Irshad K T",
    'website': "https://nomizotech.net/",
    'category': 'Accounting',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}