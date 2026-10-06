
DATABASE_CATALOG = {
    "Relational": [
        "MySQL", "PostgreSQL", "MariaDB", "SQLite",
    ],
    "Document": [
        "MongoDB", "CouchDB",
    ],
    "Key-Value": [
        "Redis", "Amazon DynamoDB", "Riak",
    ],
    "Wide-Column": [
        "Cassandra", "HBase", "ScyllaDB",
    ],
    "Graph": [
        "Neo4j", "Amazon Neptune",
    ],
    "Search Engine": [
        "Elasticsearch", "Apache Solr",
    ],
    "Time-Series": [
        "InfluxDB", "TimescaleDB", "OpenTSDB",
    ],
    "Data Warehouse / Analytics": [
        "ClickHouse", "Snowflake", "DuckDB", "Apache Druid",
    ],
    "Multi-Model": [
        "ArangoDB", "OrientDB",
    ],
}


import itertools
import operator

DB_TO_CATEGORY = dict(
    itertools.chain.from_iterable(
        map(
            lambda item: map(lambda db: (db, item[0]), item[1]),
            DATABASE_CATALOG.items(),
        )
    )
)

ALL_DATABASES = list(DB_TO_CATEGORY.keys())


CATEGORY_TO_SECTION = {
    "Relational": "Primary Database (Relational)",
    "Document": "Primary Database (Document)",
    "Key-Value": "Caching Layer",
    "Wide-Column": "Wide-Column Store",
    "Graph": "Graph Database",
    "Search Engine": "Search Engine",
    "Time-Series": "Time-Series Database",
    "Data Warehouse / Analytics": "Analytics Database",
    "Multi-Model": "Multi-Model Database",
}
