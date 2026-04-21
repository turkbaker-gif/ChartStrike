import urllib.parse
import xml.etree.ElementTree as ET

import httpx


class GoogleNewsRSSClient:
    BASE_URL = "https://news.google.com/rss/search"

    @staticmethod
    def get_search_results(query: str, when: str = "7d", limit: int = 10) -> list[dict]:
        q = f"{query} when:{when}"
        params = {
            "q": q,
            "hl": "en-US",
            "gl": "US",
            "ceid": "US:en",
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(GoogleNewsRSSClient.BASE_URL, params=params)

                if response.status_code != 200:
                    print(f"Google News RSS error for query [{query}]: {response.text}")
                    return []

                xml_text = response.text
        except Exception as e:
            print(f"Google News RSS request failed for query [{query}]: {e}")
            return []

        try:
            root = ET.fromstring(xml_text)
        except Exception as e:
            print(f"Google News RSS parse failed for query [{query}]: {e}")
            return []

        items = []
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title", default="").strip()
            link = item.findtext("link", default="").strip()
            pub_date = item.findtext("pubDate", default="").strip()
            source = item.findtext("source", default="Google News").strip()

            if title:
                items.append(
                    {
                        "title": title,
                        "url": link,
                        "published_at": pub_date,
                        "source": source or "Google News",
                        "summary": None,
                    }
                )

        return items