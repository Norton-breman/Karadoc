import requests
import json
from bs4 import BeautifulSoup

from karapp.tools.rss.base import RssSearchTool


class MpdSearchTool(RssSearchTool):

    def __init__(self):
        super().__init__()
        self.name = 'My Podcast Data'

    @classmethod
    def search(cls, keyword):
        url = f"https://api.mypodcastdata.com/api/shows/searchbykeywords/{keyword}"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = json.loads(response.text)
        resultats = []

        for item in data['shows']:
            titre = item.get("title")
            url_page = item.get("link")
            desc = item.get("description")
            image = item.get("logo")
            flux_rss = item.get("rssSource", None)
            if not flux_rss and 'apple' in item:
                # flux_rss = get_rss_from_apple_podcast(item['apple']['appleUrl'])
                flux_rss = cls.get_rss_from_apple_podcast(item['apple']['appleUrl'])
            resultats.append({
                "titre": titre,
                "url_page": url_page,
                "description": desc,
                "image": image,
                "flux_rss": flux_rss,
            })
        return resultats

    @staticmethod
    def get_rss_from_apple_podcast(url: str) -> str:
        """
        Extrait l'URL du flux RSS d'un podcast Apple Podcasts.
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Apple Podcasts met le flux RSS dans une balise <script> JSON-LD
        for script in soup.find_all("script", type="application/json"):
            data = json.loads(script.string)
            url_candidates = find_keys(data, 'feedUrl')
            if len(url_candidates):
                return url_candidates[0]

        raise ValueError("Impossible de trouver le flux RSS sur cette page.")


def find_keys(obj, key):
    """Cherche récursivement toutes les valeurs associées à une clé donnée."""
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                results.append(v)
            else:
                results.extend(find_keys(v, key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_keys(item, key))
    return results