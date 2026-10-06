
DB_REQUIRED_CONDITIONS = {
    "MySQL":          [("structured_data", "structured data was present"),
                       ("transactions",    "transactional consistency was required")],
    "PostgreSQL":     [("structured_data", "structured data was present"),
                       ("transactions",    "ACID transactions were required")],
    "MariaDB":        [("transactions",    "transactional consistency was required"),
                       ("high_availability", "high availability was requested")],
    "SQLite":         [("embedded_database", "an embedded database was requested"),
                       ("offline_first",   "offline-first support was requested")],

    "MongoDB":        [("unstructured_data", "unstructured data was present"),
                       ("flexible_schema", "a flexible schema was requested"),
                       ("json_support",    "native JSON support was requested")],
    "CouchDB":        [("unstructured_data", "unstructured data was present"),
                       ("offline_first",   "offline-first synchronization was requested")],

    "Redis":          [("caching_needed",  "a caching layer was requested"),
                       ("high_read_speed", "very high read speed was requested"),
                       ("low_latency",     "low latency was requested")],
    "Amazon DynamoDB":[("caching_needed",  "a key-value workload was present"),
                       ("cloud_native",    "cloud-native deployment was requested")],
    "Riak":           [("high_availability", "high availability was requested"),
                       ("fault_tolerance", "fault tolerance was requested")],

    "Cassandra":      [("big_data",        "the data volume was very large"),
                       ("flexible_schema", "a flexible schema was requested")],
    "HBase":          [("big_data",        "the data volume was very large"),
                       ("event_logging",   "event logging at scale was requested")],
    "ScyllaDB":       [("big_data",        "the data volume was very large"),
                       ("low_latency",     "low latency was requested")],

    "Neo4j":          [("relationships_complex",
                        "complex graph relationships were detected")],
    "Amazon Neptune": [("relationships_complex",
                        "complex graph relationships were detected"),
                       ("cloud_native",    "cloud-native deployment was requested")],

    "Elasticsearch":  [("full_text_search", "full-text search was requested")],
    "Apache Solr":    [("full_text_search", "full-text search was requested"),
                       ("open_source_preference",
                        "an open-source preference was stated")],

    "InfluxDB":       [("time_series_data", "time-series data was present")],
    "TimescaleDB":    [("time_series_data", "time-series data was present"),
                       ("sql_compatibility", "SQL compatibility was requested")],
    "OpenTSDB":       [("time_series_data", "time-series data was present"),
                       ("big_data",         "the data volume was very large")],

    "ClickHouse":     [("olap_workload",      "an OLAP analytical workload was present"),
                       ("real_time_analytics", "real-time analytics was requested")],
    "Snowflake":      [("olap_workload",      "an OLAP analytical workload was present"),
                       ("cloud_native",       "cloud-native deployment was requested")],
    "DuckDB":         [("olap_workload",      "an OLAP analytical workload was present"),
                       ("embedded_database",  "an embedded database was requested")],
    "Apache Druid":   [("olap_workload",      "an OLAP analytical workload was present"),
                       ("streaming_data",     "streaming data ingestion was requested")],

    "ArangoDB":       [("relationships_complex",
                        "complex graph relationships were detected"),
                       ("json_support",    "native JSON support was requested")],
    "OrientDB":       [("relationships_complex",
                        "complex graph relationships were detected"),
                       ("flexible_schema", "a flexible schema was requested")],
}


DB_EXCLUSION_CONDITIONS = {
    "MySQL":           [("sql_compatibility",
                         "SQL compatibility was not specifically required")],
    "CouchDB":         [("multi_region_replication",
                         "multi-region replication was not requested")],
    "Amazon DynamoDB": [("open_source_preference",
                         "open-source was not a strict preference")],
    "Cassandra":       [("relationships_complex",
                         "complex relationships were not present")],
    "HBase":           [("structured_data",
                         "the data was not structured")],
    "Snowflake":       [("open_source_preference",
                         "open-source was not a strict preference")],
    "OpenTSDB":        [("sql_compatibility",
                         "SQL compatibility was not requested")],
    "OrientDB":        [("big_data",
                         "the data volume was not yet at massive scale")],
    "Elasticsearch":   [("transactions",
                         "ACID transactions were not required")],
}


PENALTY_DESCRIPTIONS = {
    "Penalty_Cassandra_NoBigData":
        "No big-data volume requirement: Cassandra's operational overhead "
        "is unjustified at smaller scale.",
    "Penalty_Cassandra_NoFlexSchema":
        "Rigid structured data: Cassandra is optimised for schema-flexible "
        "workloads; relational databases are more appropriate.",
    "Penalty_Cassandra_ACIDRequired":
        "ACID transactions required: Cassandra offers only lightweight "
        "transactions; a relational engine is a better fit.",
    "Penalty_MongoDB_NoFlexSchema":
        "No flexible schema needed: MongoDB's main strength is schema "
        "flexibility; without it a relational database is preferable.",
    "Penalty_MongoDB_ACID_SQL":
        "ACID + SQL on structured data: this combination strongly favors "
        "a relational database over a document store.",
    "Penalty_Redis_NoCacheOrLatency":
        "No caching or low-latency requirement: Redis's in-memory model "
        "is overkill and expensive for this workload.",
    "Penalty_Redis_BigDataOLAP":
        "Big-data OLAP workload: Redis is an in-memory store unsuitable "
        "for petabyte-scale analytical queries.",
    "Penalty_ES_NoFullTextSearch":
        "No full-text search requirement: Elasticsearch's operational "
        "complexity is hard to justify without search needs.",
    "Penalty_ES_TransactionalWorkload":
        "Transactional + structured data without search: Elasticsearch "
        "is eventually consistent and lacks native ACID support.",
    "Penalty_Neo4j_NoRelationships":
        "No complex relationship requirement: Neo4j's value is graph "
        "traversal; simpler databases are more cost-effective here.",
    "Penalty_Snowflake_NoOLAP":
        "No OLAP workload: Snowflake is a cloud data warehouse; without "
        "analytical queries it is an expensive mismatch.",
    "Penalty_Snowflake_OSSPreference":
        "Open-source preference: Snowflake is proprietary; this "
        "conflicts directly with the stated preference.",
    "Penalty_ClickHouse_NoOLAPOrAnalytics":
        "No OLAP, analytics, or vector-search workload: ClickHouse's "
        "columnar engine adds unnecessary complexity.",
    "Penalty_DynamoDB_OSSPreference":
        "Open-source preference: DynamoDB is a proprietary AWS service; "
        "this is a direct conflict.",
    "Penalty_DynamoDB_NoCloud":
        "Non-cloud deployment: DynamoDB is AWS-managed and cannot run "
        "on-premises.",
    "Penalty_SQLite_BigData":
        "Big-data volume: SQLite is a single-file engine that cannot "
        "handle the required scale.",
    "Penalty_SQLite_HorizontalScale":
        "Horizontal scalability required: SQLite has no clustering or "
        "replication support.",
    "Penalty_SQLite_MultiTenancy":
        "Multi-tenancy + transactions: SQLite's file-level locking makes "
        "it unsuitable for concurrent multi-tenant workloads.",
}


def _sentence_case(text):
  
    return text and (text[0].upper() + text[1:])


def explain_rejection(db_name, facts_dict):

    required = DB_REQUIRED_CONDITIONS.get(db_name, [])
    excluded = DB_EXCLUSION_CONDITIONS.get(db_name, [])

    missing_reasons = list(map(
        lambda pair: f"{_sentence_case(pair[1])}, but this was not the case",
        filter(
            lambda pair: not facts_dict.get(pair[0], False),
            required,
        ),
    ))

    conflicting_reasons = list(map(
        lambda pair: (
            f"It was expected that {pair[1]}, but the opposite was true "
            f"for this case"
        ),
        filter(
            lambda pair: facts_dict.get(pair[0], False),
            excluded,
        ),
    ))

    all_reasons = missing_reasons + conflicting_reasons
    return all_reasons or ["None of its key requirement combinations were fully satisfied."]
