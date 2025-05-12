import requests 
import xlsxwriter
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import JsonResponse
from .models import ScrapedData

import csv
import io
import pandas as pd
from django.http import HttpResponse
from .models import ScrapedData

def scrape_website(request):
    if request.method == "POST":
        url = request.POST.get("url")
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            
            data = {
                "title": soup.title.string if soup.title else "No title found",
                "headings": [h.get_text() for h in soup.find_all("h1")],
                "paragraphs": [p.get_text() for p in soup.find_all("p")]
            }
            
            # Simpan hasil ke database
            ScrapedData.objects.create(
                url=url,
                title=data["title"],
                headings="\n".join(data["headings"]),
                paragraphs="\n".join(data["paragraphs"])
            )
            
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({"error": str(e)})
    
    return render(request, "scraper/index.html")

def scraped_list(request):
    data = ScrapedData.objects.all().order_by("-scraped_at")
    return render(request, "scraper/list.html", {"data": data})


# Export data ke CSV
def export_to_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="scraped_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["URL", "Title", "Headings", "Paragraphs", "Scraped At"])

    data = ScrapedData.objects.all()
    for item in data:
        writer.writerow([item.url, item.title, item.headings, item.paragraphs, item.scraped_at])

    return response

# Export data ke Excel
def export_to_excel(request):
    data = list(ScrapedData.objects.values("url", "title", "headings", "paragraphs", "scraped_at"))

    if not data:
        return HttpResponse("Tidak ada data untuk diekspor.", content_type="text/plain")

    # Konversi ke DataFrame
    df = pd.DataFrame(data)

    # Hapus timezone dari kolom "scraped_at"
    if "scraped_at" in df.columns:
        df["scraped_at"] = df["scraped_at"].apply(lambda x: x.replace(tzinfo=None) if pd.notna(x) else x)

    # Buat response dengan tipe file Excel
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="scraped_data.xlsx"'

    # Simpan ke dalam Excel menggunakan XlsxWriter
    with pd.ExcelWriter(response, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="ScrapedData")

    return response