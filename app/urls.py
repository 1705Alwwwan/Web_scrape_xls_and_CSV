from django.urls import path
from . import views

urlpatterns = [
     path("",views.scrape_website, name="scrape_website"),
    path("results/", views.scraped_list, name="scraped_list"),
    path("export/csv/", views.export_to_csv, name="export_to_csv"),
    path("export/excel/", views.export_to_excel, name="export_to_excel"),
    
]
