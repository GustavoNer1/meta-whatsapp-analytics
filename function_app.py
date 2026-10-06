import azure.functions as func
import json
import logging
import os
import requests

from datetime import datetime, timezone, timedelta
from services.meta_service import MetaService
from services.dashboard_service import DashboardService
from services.database_service import DatabaseService
from services.sync_service import SyncService

app = func.FunctionApp()

@app.route(route='health', methods=['GET'])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({
            'status': 'ok',
            'mesage': 'Meta WhatsApp Analytics API is running'
        }),
        mimetype='application/json',
        status_code=200
    )


@app.route(route="analytics", methods=["GET"])
def get_analytics(req: func.HttpRequest) -> func.HttpResponse:

    try:
        meta = MetaService()

        data = meta.get_analytics()

        return func.HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as error:
        return func.HttpResponse(
            json.dumps({
                "error": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )

    except requests.RequestException as error:
        logging.exception("Erro ao consultar Analytics da Meta.")

        return func.HttpResponse(
            json.dumps({
                "error": "Erro ao consultar Analytics da Meta.",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=502
        )

@app.route(route="pricing", methods=["GET"])
def get_pricing(req: func.HttpRequest) -> func.HttpResponse:

    try:
        meta = MetaService()

        data = meta.get_pricing()

        return func.HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as error:
        return func.HttpResponse(
            json.dumps({
                "error": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )

    except requests.RequestException as error:
        logging.exception("Erro ao consultar Pricing Analytics da Meta.")

        return func.HttpResponse(
            json.dumps({
                "error": "Erro ao consultar Pricing Analytics da Meta.",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=502
        )


@app.route(route="dashboard", methods=["GET"])
def get_dashboard(req: func.HttpRequest) -> func.HttpResponse:

    try:

        dashboard = DashboardService()

        data = dashboard.get_summary()

        return func.HttpResponse(
            json.dumps(data),
            mimetype="application/json",
            status_code=200
        )

    except Exception as error:

        logging.exception(
            "Erro ao gerar dashboard."
        )

        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )

@app.route(route="db-health", methods=["GET"])
def db_health(req: func.HttpRequest) -> func.HttpResponse:

    try:

        database = DatabaseService()

        result = database.test_connection()

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as error:

        logging.exception(
            "Erro ao conectar ao Azure SQL."
        )

        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(
    route="sync/analytics",
    methods=["POST"]
)
def sync_analytics(req: func.HttpRequest) -> func.HttpResponse:

    try:

        sync_service = SyncService()

        result = sync_service.sync_message_analytics()

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as error:

        logging.exception(
            "Erro ao sincronizar analytics."
        )

        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(
    route="sync/pricing",
    methods=["POST"]
)
def sync_pricing(req: func.HttpRequest) -> func.HttpResponse:

    try:

        sync_service = SyncService()

        result = sync_service.sync_pricing_analytics()

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as error:

        logging.exception(
            "Erro ao sincronizar pricing analytics."
        )

        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )


@app.route(
    route="sync/all",
    methods=["POST"]
)
def sync_all(req: func.HttpRequest) -> func.HttpResponse:

    try:

        sync_service = SyncService()

        result = sync_service.sync_all()

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except Exception as error:

        logging.exception(
            "Erro ao sincronizar dados."
        )

        return func.HttpResponse(
            json.dumps({
                "status": "error",
                "detail": str(error)
            }),
            mimetype="application/json",
            status_code=500
        )