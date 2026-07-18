# import duckdb

# conn = duckdb.connect("logfire_pipeline.duckdb")

# result = conn.execute("""
# SELECT
#     trace_id,
#     SUM(attributes__gen_ai_usage_input_tokens) AS total_input_tokens
# FROM logfire_data.spans
# WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL
# GROUP BY trace_id
# ORDER BY total_input_tokens DESC;
# """).fetchall()

# for row in result:
#     print(row)

# conn.close()



# import duckdb

# conn = duckdb.connect("logfire_pipeline.duckdb")

# print(conn.execute("""
# SELECT SUM(attributes__gen_ai_usage_input_tokens)
# FROM logfire_data.spans
# WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL;
# """).fetchall())

# conn.close()


# import duckdb

# conn = duckdb.connect("logfire_pipeline.duckdb")

# print(conn.execute("""
# SELECT
#     trace_id,
#     attributes__gen_ai_usage_input_tokens
# FROM logfire_data.spans
# WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL
# ORDER BY trace_id;
# """).fetchall())

# conn.close()


import duckdb

conn = duckdb.connect("logfire_pipeline.duckdb")

print(conn.execute("""
SELECT
    trace_id,
    SUM(attributes__gen_ai_usage_input_tokens) AS total_input_tokens
FROM logfire_data.spans
WHERE attributes__gen_ai_usage_input_tokens IS NOT NULL
GROUP BY trace_id
ORDER BY total_input_tokens DESC;
""").fetchall())

conn.close()