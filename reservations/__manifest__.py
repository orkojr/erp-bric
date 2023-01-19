{
    'name': "Reservations",
    'description': 'Permet les reservations dans une agence de voyage.',
    'author': 'Jordan Kamga Wafo',
    'depends': ['base','website','contacts','mail','calendar','website_forum',],
    'category': 'website',
    'license' : 'LGPL-3',
    'data': [
        'security/reservation_security.xml',
        'security/ir.model.access.csv',
        'data/auto.xml',
        'views/hotel_view.xml',
        'views/classe_view.xml',
        'views/categorie_view.xml',
        'views/chambre_view.xml',
        'views/client_view.xml',
        'views/reservation_view.xml',
        'views/consommation_view.xml',
        'views/prestation_view.xml',
        'report/report.xml',
        'report/hotel_detail.xml',
        'report/facture.xml',
        
    ],
    'application': True,
}