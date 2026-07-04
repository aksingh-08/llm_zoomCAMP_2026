Question 1:
using chatgpt =>
```
id: nyc_taxi_csv_to_bigquery
namespace: company.analytics

variables:
  project_id: my-gcp-project
  bucket: my-data-bucket
  dataset: nyc_taxi
  table: yellow_tripdata
  file_name: yellow_tripdata_2024-01.csv
  source_url: https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.csv

tasks:
  - id: download_csv
    type: io.kestra.plugin.core.http.Download
    uri: "{{ vars.source_url }}"

  - id: upload_to_gcs
    type: io.kestra.plugin.gcp.gcs.Upload
    from: "{{ outputs.download_csv.uri }}"
    bucket: "{{ vars.bucket }}"
    name: "{{ vars.file_name }}"

  - id: create_dataset
    type: io.kestra.plugin.gcp.bigquery.Query
    projectId: "{{ vars.project_id }}"
    sql: |
      CREATE SCHEMA IF NOT EXISTS `{{ vars.project_id }}.{{ vars.dataset }}`;

  - id: create_table
    type: io.kestra.plugin.gcp.bigquery.Query
    projectId: "{{ vars.project_id }}"
    sql: |
      CREATE TABLE IF NOT EXISTS `{{ vars.project_id }}.{{ vars.dataset }}.{{ vars.table }}`
      (
        VendorID INTEGER,
        tpep_pickup_datetime TIMESTAMP,
        tpep_dropoff_datetime TIMESTAMP,
        passenger_count FLOAT64,
        trip_distance FLOAT64,
        RatecodeID FLOAT64,
        store_and_fwd_flag STRING,
        PULocationID INTEGER,
        DOLocationID INTEGER,
        payment_type INTEGER,
        fare_amount FLOAT64,
        extra FLOAT64,
        mta_tax FLOAT64,
        tip_amount FLOAT64,
        tolls_amount FLOAT64,
        improvement_surcharge FLOAT64,
        total_amount FLOAT64,
        congestion_surcharge FLOAT64,
        Airport_fee FLOAT64
      );

  - id: load_csv
    type: io.kestra.plugin.gcp.bigquery.LoadFromGcs
    projectId: "{{ vars.project_id }}"
    from:
      - "gs://{{ vars.bucket }}/{{ vars.file_name }}"
    destinationTable: "{{ vars.project_id }}.{{ vars.dataset }}.{{ vars.table }}"
    format: CSV
    autodetect: true
    skipLeadingRows: 1
    writeDisposition: WRITE_TRUNCATE

  - id: verify_load
    type: io.kestra.plugin.gcp.bigquery.Query
    projectId: "{{ vars.project_id }}"
    fetch: true
    sql: |
      SELECT COUNT(*) AS row_count
      FROM `{{ vars.project_id }}.{{ vars.dataset }}.{{ vars.table }}`;
```