from urllib.parse import urlencode
import requests
import json

from karapp.tools.rss.base import RssSearchTool

class RadioFranceSearchTool(RssSearchTool):

    def __init__(self):
        super().__init__()
        self.name = 'Radio France'

    @classmethod
    def search(cls, keyword):
        rss_provider = "https://radio-france-rss.aerion.workers.dev/"
        """Recherche les flux RSS d'une émission Radio France."""
        params = {"query": keyword}
        url = rss_provider + 'search/' + "?" + urlencode(params)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = json.loads(response.text)
        results = []

        for item in data:
            results.append({
                "titre": item.get("title"),
                "url_page": item.get("path"),
                "description": item.get("standfirst"),
                "image": item.get("imgUrl"),
                "flux_rss": item.get("rssUrl"),
            })
        return results