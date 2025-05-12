from django.db import models

class ScrapedData(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=255, null=True, blank=True)
    headings = models.TextField(null=True, blank=True)
    paragraphs = models.TextField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url
