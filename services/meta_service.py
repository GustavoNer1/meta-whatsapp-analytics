import os
import requests

from datetime import datetime, timezone, timedelta


class MetaService:

    def __init__(self):
        self.waba_id = os.getenv("META_WABA_ID")
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.base_url = "https://graph.facebook.com/v25.0"

        if not self.waba_id or not self.access_token:
            raise ValueError(
                "META_WABA_ID ou META_ACCESS_TOKEN não configurado."
            )

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

    def get_analytics(self, days=7):

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        fields = (
            f"analytics.start({start_timestamp})"
            f".end({end_timestamp})"
            ".granularity(DAY)"
            ".phone_numbers([])"
            '.country_codes(["BR"])'
        )

        url = f"{self.base_url}/{self.waba_id}"

        params = {
            "fields": fields
        }

        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def get_pricing(self, days=7):

        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        url = f"{self.base_url}/{self.waba_id}/pricing_analytics"

        params = {
            "start": start_timestamp,
            "end": end_timestamp,
            "granularity": "DAILY",
            "metric_types": '["COST","VOLUME"]',
            "dimensions": '["PRICING_CATEGORY","PRICING_TYPE","PHONE","COUNTRY"]'
        }

        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()


    def get_account_info(self):

        url = f"{self.base_url}/{self.waba_id}"

        params = {
            "fields": "id,name,currency"
        }

        response = requests.get(
            url,
            headers=self._headers(),
            params=params,
            timeout=30
        )

        response.raise_for_status()

        return response.json()