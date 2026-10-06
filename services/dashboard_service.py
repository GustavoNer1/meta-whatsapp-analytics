import os

from services.database_service import DatabaseService


class DashboardService:

    def __init__(self):

        self.database = DatabaseService()

        self.waba_id = os.getenv("META_WABA_ID")

        if not self.waba_id:
            raise ValueError(
                "META_WABA_ID não configurado."
            )

    def get_summary(self, days=7):

        message_data = (
            self.database.get_message_analytics_summary(
                waba_id=self.waba_id,
                days=days
            )
        )

        pricing_data = (
            self.database.get_pricing_summary(
                waba_id=self.waba_id,
                days=days
            )
        )

        sent = message_data["sent"]
        delivered = message_data["delivered"]

        delivery_rate = (
            round((delivered / sent) * 100, 2)
            if sent > 0
            else 0
        )

        total_volume = 0
        total_cost = 0
        categories = {}

        currency = None

        for item in pricing_data:

            category = item["category"]

            total_volume += item["volume"]
            total_cost += item["cost"]

            if currency is None:
                currency = item["currency"]

            categories[category] = {
                "volume": item["volume"],
                "cost": round(item["cost"], 6)
            }

        return {
            "period_days": days,

            "messages": {
                "sent": sent,
                "delivered": delivered,
                "delivery_rate": delivery_rate
            },

            "billing": {
                "currency": currency,
                "volume": total_volume,
                "total_cost": round(total_cost, 6),
                "categories": categories
            }
        }