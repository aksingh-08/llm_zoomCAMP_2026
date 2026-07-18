import duckdb

conn = duckdb.connect("logfire_pipeline.duckdb")

result = conn.execute("""
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'logfire_data';
""").fetchall()

print(result)

# import duckdb

# conn = duckdb.connect("logfire_pipeline.duckdb")

# print(conn.execute("""
# SELECT table_name
# FROM information_schema.tables
# WHERE table_schema = 'logfire_data'
# ORDER BY table_name;
# """).fetchall())