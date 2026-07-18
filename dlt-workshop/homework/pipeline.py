"""
dlt pipeline: load spans (records) from Logfire's Query API into DuckDB.

Logfire's Query API (https://logfire.pydantic.dev/docs/how-to-guides/query-api/)
exposes an arbitrary-SQL endpoint at GET /v1/query. There's no built-in
offset/cursor pagination, so we page through results using min_timestamp,
advancing it past the last-seen start_timestamp on each request. dlt's
incremental() helper both drives that paging *and* persists the high-water
mark between pipeline runs, so re-running this script only loads new spans.

Auth: reads LOGFIRE_READ_TOKEN from .dlt/secrets.toml (or the environment
variable LOGFIRE_READ_TOKEN / SOURCES__LOGFIRE__READ_TOKEN).
"""

from dotenv import load_dotenv
import os
from typing import Iterator
import dlt
from dlt.sources.helpers import requests
load_dotenv()

LOGFIRE_BASE_URLS = {
    "us": "https://logfire-us.pydantic.dev",
    "eu": "https://logfire-eu.pydantic.dev",
}

# Max rows Logfire's API will return in a single /v1/query response.
PAGE_LIMIT = 10_000

# How far back to load on the very first run.
DEFAULT_START = "2024-01-01T00:00:00Z"


@dlt.source
def logfire_source(
    read_token: str = dlt.secrets.value,
    region: str = dlt.config.value,
) -> Iterator[dlt.sources.DltResource]:
    """Logfire source. Currently exposes a single resource: `spans`."""

    @dlt.resource(
        name="spans",
        write_disposition="append",
        primary_key="span_id",
    )
    def spans(
        start_timestamp: dlt.sources.incremental[str] = dlt.sources.incremental(
            "start_timestamp",
            initial_value=DEFAULT_START,
        ),
    ):
        base_url = LOGFIRE_BASE_URLS.get(region, LOGFIRE_BASE_URLS["us"])
        headers = {
            "Authorization": f"Bearer {read_token}",
            "Accept": "application/json",
        }

        # min_timestamp is a strict "greater than" filter server-side, so
        # re-issuing the query with an advancing min_timestamp gives us
        # simple, dedup-safe pagination through the records table.
        min_ts = start_timestamp.last_value

        while True:
            params = {
                "sql": "SELECT * FROM records ORDER BY start_timestamp ASC",
                "row_oriented": "true",
                "limit": PAGE_LIMIT,
                "min_timestamp": min_ts,
            }
            response = requests.get(f"{base_url}/v1/query", params=params, headers=headers)
            response.raise_for_status()

            payload = response.json()
            
            # Handle row-oriented responses
            if isinstance(payload, list):
                rows = payload
            
            elif isinstance(payload, dict) and "rows" in payload:
                rows = payload["rows"]
            
            # Handle column-oriented responses
            elif isinstance(payload, dict) and "columns" in payload:
                columns = payload["columns"]
            
                names = [c["name"] for c in columns]
                values = [c["values"] for c in columns]
            
                rows = [
                    dict(zip(names, row_values))
                    for row_values in zip(*values)
                ]
            
            else:
                raise ValueError(f"Unexpected response format: {payload}")
            
            if not rows:
                break
            
            yield rows
            
            if len(rows) < PAGE_LIMIT:
                break
            
            min_ts = rows[-1]["start_timestamp"]

    return spans


def run() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_pipeline",
        destination="duckdb",
        dataset_name="logfire_data",
    )

    # Prefer a plain LOGFIRE_READ_TOKEN env var if it's set; otherwise fall
    # back to dlt's normal secrets resolution (.dlt/secrets.toml or
    # SOURCES__... env vars), handled automatically via dlt.secrets.value.
    env_token = os.getenv("LOGFIRE_READ_TOKEN")
    # source = logfire_source(read_token=env_token) if env_token else logfire_source()
    source = logfire_source(
        read_token=env_token,
        region="us",
    )
    
    load_info = pipeline.run(source)
    print(load_info)


if __name__ == "__main__":
    run()
