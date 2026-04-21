import httpx

from app.core.config import settings


class GDELTClient:
    BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

    @staticmethod
    def get_article_list(query: str, max_records: int = 10) -> list[dict]:
        # Use a simpler, more robust query format
        # GDELT works well with just the ticker or company name
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": max_records,
            "timespan": settings.gdelt_timespan,
            "sort": "datedesc",
            "format": "jsonfeed",
        }

        try:
            with httpx.Client(timeout=20.0) as client:
                response = client.get(GDELTClient.BASE_URL, params=params)

                if response.status_code != 200:
                    print(f"GDELT HTTP error {response.status_code} for query [{query}]: {response.text[:200]}")
                    return []

                # Some responses may not be JSON despite status 200
                try:
                    data = response.json()
                except Exception as json_err:
                    print(f"GDELT JSON decode failed for query [{query}]: {json_err}")
                    return []

        except Exception as e:
            print(f"GDELT request failed for query [{query}]: {e}")
            return []

        if not isinstance(data, dict):
            return []

        items = data.get("items", [])
        if not isinstance(items, list):
            return []

        return items