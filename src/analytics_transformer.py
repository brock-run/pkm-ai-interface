import base64
import json
from datetime import datetime, timezone


def lambda_handler(event, context):
    """Enrich Firehose records with a processed timestamp."""
    output = []
    for record in event.get("records", []):
        payload = base64.b64decode(record["data"]).decode("utf-8")
        data = json.loads(payload)
        data["processed_at"] = datetime.now(timezone.utc).isoformat()
        enriched = json.dumps(data) + "\n"
        encoded = base64.b64encode(enriched.encode("utf-8")).decode("utf-8")
        output.append(
            {
                "recordId": record["recordId"],
                "result": "Ok",
                "data": encoded,
            }
        )
    return {"records": output}

