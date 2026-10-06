import os
import mssql_python

from datetime import datetime, timezone

class DatabaseService:

    def __init__(self):
        self.connection_string = os.getenv(
            "AZURE_SQL_CONNECTIONSTRING"
        )

        if not self.connection_string:
            raise ValueError(
                "AZURE_SQL_CONNECTIONSTRING não configurada."
            )

    def get_connection(self):
        return mssql_python.connect(
            self.connection_string
        )

    def test_connection(self):

        connection = self.get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    DB_NAME() AS banco,
                    ORIGINAL_LOGIN() AS usuario
            """)

            row = cursor.fetchone()

            return {
                "status": "ok",
                "database": row[0],
                "user": row[1]
            }

        finally:
            connection.close()

    def upsert_message_analytics(self, analytics_data):

        analytics = analytics_data.get("analytics", {})

        phone_numbers = analytics.get("phone_numbers", [])
        country_codes = analytics.get("country_codes", [])
        data_points = analytics.get("data_points", [])

        waba_id = analytics_data.get("id")

        if not waba_id:
            raise ValueError("WABA ID não encontrado no retorno da Meta.")

        if len(phone_numbers) != 1:
            raise ValueError(
                "Este MVP espera exatamente um número por consulta de analytics."
            )

        if len(country_codes) != 1:
            raise ValueError(
                "Este MVP espera exatamente um país por consulta de analytics."
            )

        phone_number = phone_numbers[0]
        country_code = country_codes[0]

        connection = self.get_connection()
        cursor = connection.cursor()

        try:

            for point in data_points:

                period_start = datetime.fromtimestamp(
                    point["start"],
                    tz=timezone.utc
                ).replace(tzinfo=None)

                period_end = datetime.fromtimestamp(
                    point["end"],
                    tz=timezone.utc
                ).replace(tzinfo=None)

                params = {
                    "waba_id": waba_id,
                    "phone_number": phone_number,
                    "country_code": country_code,
                    "period_start": period_start,
                    "period_end": period_end,
                    "sent": point.get("sent", 0),
                    "delivered": point.get("delivered", 0)
                }

                cursor.execute("""
                    UPDATE dbo.message_analytics_daily

                    SET
                        sent = %(sent)s,
                        delivered = %(delivered)s

                    WHERE
                        waba_id = %(waba_id)s
                        AND phone_number = %(phone_number)s
                        AND country_code = %(country_code)s
                        AND period_start = %(period_start)s
                        AND period_end = %(period_end)s;

                    IF @@ROWCOUNT = 0
                    BEGIN

                        INSERT INTO dbo.message_analytics_daily
                        (
                            waba_id,
                            phone_number,
                            country_code,
                            period_start,
                            period_end,
                            sent,
                            delivered
                        )
                        VALUES
                        (
                            %(waba_id)s,
                            %(phone_number)s,
                            %(country_code)s,
                            %(period_start)s,
                            %(period_end)s,
                            %(sent)s,
                            %(delivered)s
                        );

                    END
                """, params)

            connection.commit()

            return {
                "processed": len(data_points)
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def upsert_pricing_analytics(self, pricing_data, waba_id, currency_code):

        pricing_points = []

        for group in pricing_data.get("data", []):
            pricing_points.extend(
                group.get("data_points", [])
            )

        connection = self.get_connection()
        cursor = connection.cursor()

        try:

            for point in pricing_points:

                period_start = datetime.fromtimestamp(
                    point["start"],
                    tz=timezone.utc
                ).replace(tzinfo=None)

                period_end = datetime.fromtimestamp(
                    point["end"],
                    tz=timezone.utc
                ).replace(tzinfo=None)

                params = {
                    "waba_id": waba_id,
                    "phone_number": point["phone_number"],
                    "country_code": point["country"],
                    "pricing_type": point["pricing_type"],
                    "pricing_category": point["pricing_category"],
                    "currency_code": currency_code,
                    "period_start": period_start,
                    "period_end": period_end,
                    "volume": point.get("volume", 0),
                    "cost": point.get("cost", 0)
                }

                cursor.execute("""
                    UPDATE dbo.pricing_analytics_daily

                    SET
                        volume = %(volume)s,
                        cost = %(cost)s,
                        currency_code = %(currency_code)s,
                        updated_at = SYSUTCDATETIME()

                    WHERE
                        waba_id = %(waba_id)s
                        AND phone_number = %(phone_number)s
                        AND country_code = %(country_code)s
                        AND pricing_type = %(pricing_type)s
                        AND pricing_category = %(pricing_category)s
                        AND period_start = %(period_start)s
                        AND period_end = %(period_end)s;

                    IF @@ROWCOUNT = 0
                    BEGIN

                        INSERT INTO dbo.pricing_analytics_daily
                        (
                            waba_id,
                            phone_number,
                            country_code,
                            pricing_type,
                            pricing_category,
                            currency_code,
                            period_start,
                            period_end,
                            volume,
                            cost
                        )
                        VALUES
                        (
                            %(waba_id)s,
                            %(phone_number)s,
                            %(country_code)s,
                            %(pricing_type)s,
                            %(pricing_category)s,
                            %(currency_code)s,
                            %(period_start)s,
                            %(period_end)s,
                            %(volume)s,
                            %(cost)s
                        );

                    END
                """, params)

            connection.commit()

            return {
                "processed": len(pricing_points)
            }

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()



    def get_message_analytics_summary(self, waba_id, days=7):

        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    COALESCE(SUM(sent), 0) AS sent,
                    COALESCE(SUM(delivered), 0) AS delivered
                FROM dbo.message_analytics_daily
                WHERE
                    waba_id = %(waba_id)s
                    AND period_start >= DATEADD(
                        DAY,
                        -%(days)s,
                        SYSUTCDATETIME()
                    );
            """, {
                "waba_id": waba_id,
                "days": days
            })

            row = cursor.fetchone()

            return {
                "sent": int(row[0]),
                "delivered": int(row[1])
            }

        finally:
            cursor.close()
            connection.close()


    def get_pricing_summary(self, waba_id, days=7):

        connection = self.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("""
                SELECT
                    currency_code,
                    pricing_category,
                    SUM(volume) AS volume,
                    SUM(cost) AS cost
                FROM dbo.pricing_analytics_daily
                WHERE
                    waba_id = %(waba_id)s
                    AND period_start >= DATEADD(
                        DAY,
                        -%(days)s,
                        SYSUTCDATETIME()
                    )
                GROUP BY
                    currency_code,
                    pricing_category
                ORDER BY
                    pricing_category;
            """, {
                "waba_id": waba_id,
                "days": days
            })

            rows = cursor.fetchall()

            return [
                {
                    "currency": row[0],
                    "category": row[1],
                    "volume": int(row[2]),
                    "cost": float(row[3])
                }
                for row in rows
            ]

        finally:
            cursor.close()
            connection.close()