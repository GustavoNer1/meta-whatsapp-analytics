from services.meta_service import MetaService
from services.database_service import DatabaseService


class SyncService:

    def __init__(self):
        self.meta = MetaService()
        self.database = DatabaseService()

    def sync_message_analytics(self, days=7):

        analytics_data = self.meta.get_analytics(days)

        result = self.database.upsert_message_analytics(
            analytics_data
        )

        return {
            "status": "ok",
            "source": "meta",
            "destination": "azure_sql",
            "period_days": days,
            "records_processed": result["processed"]
        }


    def sync_pricing_analytics(self, days=7):

        pricing_data = self.meta.get_pricing(days)

        account_info = self.meta.get_account_info()

        result = self.database.upsert_pricing_analytics(
            pricing_data=pricing_data,
            waba_id=account_info["id"],
            currency_code=account_info["currency"]
        )

        return {
            "status": "ok",
            "source": "meta",
            "destination": "azure_sql",
            "period_days": days,
            "records_processed": result["processed"]
        }

    def sync_all(self, days=7):

        analytics_result = self.sync_message_analytics(days)
        pricing_result = self.sync_pricing_analytics(days)

        return {
            "status": "ok",
            "analytics": analytics_result,
            "pricing": pricing_result
        }