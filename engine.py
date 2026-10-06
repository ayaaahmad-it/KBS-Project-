

import collections
import functools

import compat 
from experta import KnowledgeEngine, Rule, NOT

from facts import Company, FiredRule, DatabaseCF




def _run(iterable):
  
    collections.deque(iterable, maxlen=0)


def _mycin_combine(cf_acc, cf_new):
   
    same_sign  = (cf_acc >= 0) == (cf_new >= 0)
    both_pos   = cf_acc >= 0 and cf_new >= 0
    safe_denom = max(1 - min(abs(cf_acc), abs(cf_new)), 1e-9)
    return {
        True:  {True:  lambda: cf_acc + cf_new * (1 - cf_acc),
                False: lambda: cf_acc + cf_new * (1 + cf_acc)}[both_pos],
        False: lambda: (cf_acc + cf_new) / safe_denom,
    }[same_sign]()



class DatabaseExpert(KnowledgeEngine):


    def __init__(self):
        super().__init__()
        
        self.fired_rule_log  = []
        self.scores          = {}                         
        self.matched_rules   = collections.defaultdict(list) 



    def cf_vote(self, db_name, rule_name, cf_value, reason):

        self.declare(FiredRule(
            rule_name=rule_name,
            db_name=db_name,
            cf_value=cf_value,
            reason=reason,
        ))
        self.fired_rule_log.append(rule_name)

 

    def combine_cfs(self):
     
        fired = list(filter(
            lambda f: isinstance(f, FiredRule),
            self.facts.values(),
        ))

        by_db = collections.defaultdict(list)
        _run(map(
            lambda f: by_db[f["db_name"]].append(
                (f["rule_name"], f["cf_value"], f["reason"])
            ),
            fired,
        ))

        def _process_db(item):
            db_name, rules = item
            cf_raw    = functools.reduce(
                _mycin_combine,
                map(lambda r: r[1], rules),
                0.0,
            )
            cf_clamped = max(-1.0, min(cf_raw, 1.0))
            self.declare(DatabaseCF(
                db_name=db_name,
                cf_combined=round(cf_clamped, 4),
            ))
            self.scores[db_name]        = round(cf_clamped * 100, 2)
            self.matched_rules[db_name] = list(rules)

        _run(map(_process_db, by_db.items()))



    @Rule(Company(structured_data=True, transactions=True,
                  sql_compatibility=True, security_critical=True,
                  compliance_required=True),
          salience=20)
    def rule_pg_acid_sql_secure_compliant(self):
        self.cf_vote("PostgreSQL", "Rule_PG_ACID_SQL_Secure_Compliant", 0.90,
                     "Structured data + ACID transactions + SQL + security + "
                     "compliance is the definitive PostgreSQL use-case: "
                     "a standards-compliant, auditable, secure relational engine.")

    @Rule(Company(structured_data=True, transactions=True,
                  sql_compatibility=True),
          salience=20)
    def rule_pg_acid_sql_core(self):
        self.cf_vote("PostgreSQL", "Rule_PG_ACID_SQL_Core", 0.75,
                     "Structured data + ACID transactions + SQL compatibility "
                     "strongly favor a mature relational engine; PostgreSQL is "
                     "the premier open-source choice.")

    @Rule(Company(structured_data=True, transactions=True,
                  geospatial_queries=True),
          salience=20)
    def rule_pg_geospatial_transactional(self):
        self.cf_vote("PostgreSQL", "Rule_PG_Geospatial_Transactional", 0.75,
                     "Transactional structured data + geospatial queries maps "
                     "precisely onto PostgreSQL with the PostGIS extension.")

    @Rule(Company(structured_data=True, sql_compatibility=True,
                  multi_tenancy=True, security_critical=True),
          salience=20)
    def rule_pg_multitenant_secure(self):
        self.cf_vote("PostgreSQL", "Rule_PG_MultiTenant_Secure", 0.75,
                     "Multi-tenant + SQL + security: PostgreSQL's row-level "
                     "security (RLS) and schema-per-tenant isolation are "
                     "purpose-built for this pattern.")

    @Rule(Company(structured_data=True, transactions=True,
                  high_availability=True, compliance_required=True),
          salience=20)
    def rule_pg_ha_compliance(self):
        self.cf_vote("PostgreSQL", "Rule_PG_HA_Compliance", 0.70,
                     "High availability + compliance + transactional workload: "
                     "PostgreSQL's streaming replication and audit extensions "
                     "cover both requirements.")

    @Rule(Company(structured_data=True, sql_compatibility=True,
                  oltp_workload=True, vertical_scalability=True),
          salience=20)
    def rule_pg_oltp_vertical(self):
        self.cf_vote("PostgreSQL", "Rule_PG_OLTP_Vertical", 0.70,
                     "SQL + structured + OLTP + vertical scalability: "
                     "PostgreSQL scales efficiently on large single nodes "
                     "for heavy transactional traffic.")

    # --- MongoDB composite rules --------------------------------------

    @Rule(Company(unstructured_data=True, flexible_schema=True,
                  json_support=True),
          salience=20)
    def rule_mongodb_document_core(self):
        self.cf_vote("MongoDB", "Rule_MongoDB_DocumentCore", 0.80,
                     "Unstructured data + flexible schema + JSON is the "
                     "textbook MongoDB use-case: a native document store.")

    @Rule(Company(unstructured_data=True, flexible_schema=True,
                  json_support=True, horizontal_scalability=True),
          salience=20)
    def rule_mongodb_scalable_document(self):
        self.cf_vote("MongoDB", "Rule_MongoDB_ScalableDocument", 0.85,
                     "Unstructured + flexible schema + JSON + horizontal "
                     "scalability is MongoDB's sweet spot: sharded document "
                     "clusters at any scale.")

    # --- Redis composite rules ----------------------------------------

    @Rule(Company(caching_needed=True, high_read_speed=True,
                  low_latency=True),
          salience=20)
    def rule_redis_cache_latency_core(self):
        self.cf_vote("Redis", "Rule_Redis_Cache_Latency_Core", 0.85,
                     "Caching + high read speed + low latency is the "
                     "definitive Redis pattern: sub-millisecond in-memory "
                     "key-value access.")

    @Rule(Company(low_latency=True, high_read_speed=True,
                  real_time_analytics=True),
          salience=20)
    def rule_redis_realtime_low_latency(self):
        self.cf_vote("Redis", "Rule_Redis_RealTime_LowLatency", 0.75,
                     "Low latency + high read speed + real-time analytics "
                     "benefits from Redis Streams and its in-memory "
                     "analytics capabilities.")

    # --- Elasticsearch composite rules --------------------------------

    @Rule(Company(full_text_search=True, analytics_focus=True),
          salience=20)
    def rule_es_search_analytics(self):
        self.cf_vote("Elasticsearch", "Rule_ES_Search_Analytics", 0.85,
                     "Full-text search + analytics focus is Elasticsearch's "
                     "primary positioning: inverted-index search combined "
                     "with aggregation-based analytics.")

    @Rule(Company(full_text_search=True, real_time_analytics=True,
                  event_logging=True),
          salience=20)
    def rule_es_search_realtime_logs(self):
        self.cf_vote("Elasticsearch", "Rule_ES_Search_RealTime_Logs", 0.80,
                     "Full-text search + real-time analytics + event logging "
                     "is the ELK-stack core use-case; Elasticsearch excels here.")

    # --- Neo4j composite rules ----------------------------------------

    @Rule(Company(relationships_complex=True, analytics_focus=True),
          salience=20)
    def rule_neo4j_graph_analytics(self):
        self.cf_vote("Neo4j", "Rule_Neo4j_GraphAnalytics", 0.85,
                     "Complex relationships + analytics focus: Neo4j's native "
                     "graph engine and GDS (Graph Data Science) library are "
                     "optimised for graph-based analytical workloads.")

    @Rule(Company(relationships_complex=True, real_time_analytics=True,
                  low_latency=True),
          salience=20)
    def rule_neo4j_realtime_graph(self):
        self.cf_vote("Neo4j", "Rule_Neo4j_RealTime_Graph", 0.80,
                     "Complex relationships + real-time analytics + low "
                     "latency: Neo4j's index-free adjacency enables "
                     "sub-millisecond graph traversals in real time.")

    # --- ClickHouse composite rules -----------------------------------

    @Rule(Company(olap_workload=True, real_time_analytics=True),
          salience=20)
    def rule_clickhouse_olap_realtime(self):
        self.cf_vote("ClickHouse", "Rule_ClickHouse_OLAP_RealTime", 0.85,
                     "OLAP workload + real-time analytics: ClickHouse's "
                     "columnar storage and vectorised query execution deliver "
                     "sub-second analytical queries on billions of rows.")

    @Rule(Company(vector_search=True, analytics_focus=True,
                  olap_workload=True),
          salience=20)
    def rule_clickhouse_vector_analytics(self):
        self.cf_vote("ClickHouse", "Rule_ClickHouse_Vector_Analytics", 0.85,
                     "Vector search + analytics + OLAP: ClickHouse's native "
                     "vector indexing (Approximate Nearest Neighbour) combined "
                     "with its columnar engine serves AI/embedding workloads "
                     "at analytical scale.")

    # --- Cassandra composite rules ------------------------------------

    @Rule(Company(big_data=True, flexible_schema=True,
                  high_availability=True, fault_tolerance=True),
          salience=20)
    def rule_cassandra_bigdata_ha(self):
        self.cf_vote("Cassandra", "Rule_Cassandra_BigData_HA_FT", 0.85,
                     "Big data + flexible schema + high availability + fault "
                     "tolerance is Cassandra's archetype: a masterless, "
                     "geographically distributed wide-column store.")

    @Rule(Company(big_data=True, streaming_data=True,
                  event_logging=True, high_availability=True),
          salience=20)
    def rule_cassandra_streaming_events(self):
        self.cf_vote("Cassandra", "Rule_Cassandra_Streaming_Events", 0.80,
                     "Big data + streaming + event logging + high availability: "
                     "Cassandra's append-optimised write path and time-ordered "
                     "partitioning handle high-throughput event ingestion well.")

    # --- TimescaleDB composite rules ----------------------------------

    @Rule(Company(time_series_data=True, sql_compatibility=True,
                  structured_data=True),
          salience=20)
    def rule_timescale_sql_timeseries(self):
        self.cf_vote("TimescaleDB", "Rule_TimescaleDB_SQL_TimeSeries", 0.85,
                     "Time-series + SQL + structured data: TimescaleDB extends "
                     "PostgreSQL with hypertable partitioning, continuous "
                     "aggregates, and compression optimised for time-ordered "
                     "data – the best of both worlds.")

    # --- Apache Druid composite rules ---------------------------------

    @Rule(Company(olap_workload=True, streaming_data=True,
                  real_time_analytics=True),
          salience=20)
    def rule_druid_streaming_olap(self):
        self.cf_vote("Apache Druid", "Rule_Druid_Streaming_OLAP", 0.85,
                     "OLAP + streaming + real-time analytics: Apache Druid "
                     "ingests streaming data (Kafka/Kinesis) and makes it "
                     "queryable for sub-second slice-and-dice analytics "
                     "simultaneously.")



    # --- Relational databases -----------------------------------------

    @Rule(Company(structured_data=True, transactions=True),
          NOT(Company(sql_compatibility=True)),
          salience=10)
    def rule_mysql_relational(self):
        self.cf_vote("MySQL", "Rule_MySQL_GeneralRelational", 0.50,
                     "Structured data + transactions fits a classic relational "
                     "model; MySQL is the popular general-purpose choice when "
                     "SQL dialect flexibility is less critical.")

    @Rule(Company(structured_data=True, transactions=True,
                  high_availability=True),
          salience=10)
    def rule_mariadb_ha(self):
        self.cf_vote("MariaDB", "Rule_MariaDB_HighAvailability", 0.35,
                     "MariaDB's Galera Cluster provides synchronous "
                     "multi-master HA for relational transactional workloads.")

    @Rule(Company(structured_data=True, embedded_database=True),
          salience=10)
    def rule_sqlite_embedded(self):
        self.cf_vote("SQLite", "Rule_SQLite_Embedded", 0.65,
                     "Embedded database requirement directly points to SQLite: "
                     "serverless, zero-configuration, file-based SQL engine.")

    @Rule(Company(structured_data=True, offline_first=True),
          salience=10)
    def rule_sqlite_offline(self):
        self.cf_vote("SQLite", "Rule_SQLite_OfflineFirst", 0.45,
                     "Offline-first apps with structured data commonly rely "
                     "on a local SQLite database.")

    @Rule(Company(structured_data=True, transactions=True,
                  budget_sensitive=True, open_source_preference=True),
          salience=10)
    def rule_pg_budget_oss(self):
        self.cf_vote("PostgreSQL", "Rule_PG_BudgetOpenSource", 0.25,
                     "Budget sensitivity + open-source preference + "
                     "transactions: PostgreSQL is the fully featured "
                     "zero-license-cost relational engine.")

    # --- Document databases -------------------------------------------

    @Rule(Company(unstructured_data=True, big_data=True),
          salience=10)
    def rule_mongodb_bigdata(self):
        self.cf_vote("MongoDB", "Rule_MongoDB_BigData", 0.45,
                     "MongoDB's horizontal sharding handles very large "
                     "volumes of unstructured documents efficiently.")

    @Rule(Company(unstructured_data=True, horizontal_scalability=True,
                  multi_region_replication=True),
          salience=10)
    def rule_mongodb_distributed(self):
        self.cf_vote("MongoDB", "Rule_MongoDB_Distributed", 0.35,
                     "Built-in sharding + multi-region replica sets make "
                     "MongoDB a strong fit for globally distributed document "
                     "workloads.")

    @Rule(Company(unstructured_data=True, flexible_schema=True,
                  open_source_preference=True),
          NOT(Company(multi_region_replication=True)),
          salience=10)
    def rule_couchdb_oss(self):
        self.cf_vote("CouchDB", "Rule_CouchDB_OpenSourceDoc", 0.30,
                     "CouchDB is a fully open-source document store with a "
                     "simple HTTP/JSON API; a good fit without strict "
                     "multi-region requirements.")

    @Rule(Company(unstructured_data=True, offline_first=True),
          salience=10)
    def rule_couchdb_offline(self):
        self.cf_vote("CouchDB", "Rule_CouchDB_OfflineSync", 0.40,
                     "CouchDB's native multi-master replication protocol is "
                     "specifically designed for offline-first sync scenarios.")

    # --- Key-value / cache databases ----------------------------------

    @Rule(Company(caching_needed=True, high_read_speed=True),
          salience=10)
    def rule_redis_cache(self):
        self.cf_vote("Redis", "Rule_Redis_Cache", 0.55,
                     "Caching + high read speed is the primary Redis "
                     "use-case: in-memory key-value with microsecond latency.")

    @Rule(Company(low_latency=True),
          salience=10)
    def rule_redis_latency(self):
        self.cf_vote("Redis", "Rule_Redis_LowLatency", 0.40,
                     "Low-latency requirements are well served by Redis's "
                     "in-memory data access model.")

    @Rule(Company(caching_needed=True, cloud_native=True,
                  horizontal_scalability=True),
          NOT(Company(open_source_preference=True)),
          salience=10)
    def rule_dynamodb_cloud_kv(self):
        self.cf_vote("Amazon DynamoDB", "Rule_DynamoDB_CloudKeyValue", 0.55,
                     "Cloud-native + horizontally scalable key-value without "
                     "open-source constraint fits a managed service like "
                     "DynamoDB.")

    @Rule(Company(high_availability=True, fault_tolerance=True,
                  horizontal_scalability=True, open_source_preference=True),
          salience=10)
    def rule_riak_ha_kv(self):
        self.cf_vote("Riak", "Rule_Riak_HighAvailabilityKV", 0.40,
                     "Riak is a masterless open-source key-value store "
                     "engineered for high availability and fault tolerance.")

    # --- Wide-column databases ----------------------------------------

    @Rule(Company(big_data=True, flexible_schema=True),
          NOT(Company(relationships_complex=True)),
          salience=10)
    def rule_cassandra_bigdata(self):
        self.cf_vote("Cassandra", "Rule_Cassandra_BigDataFlexible", 0.55,
                     "Large data volume + flexible schema without complex "
                     "relationships is a classic Cassandra use-case.")

    @Rule(Company(big_data=True, high_availability=True,
                  fault_tolerance=True),
          salience=10)
    def rule_cassandra_ha(self):
        self.cf_vote("Cassandra", "Rule_Cassandra_HighAvailability", 0.40,
                     "Cassandra's masterless multi-datacenter architecture "
                     "is built for HA and fault tolerance at scale.")

    @Rule(Company(big_data=True, oltp_workload=True, low_latency=True),
          salience=10)
    def rule_scylladb_low_latency(self):
        self.cf_vote("ScyllaDB", "Rule_ScyllaDB_LowLatencyOLTP", 0.50,
                     "ScyllaDB (Cassandra-compatible, C++ re-write) delivers "
                     "dramatically lower latency for large-scale OLTP.")

    @Rule(Company(big_data=True, event_logging=True),
          NOT(Company(structured_data=True)),
          salience=10)
    def rule_hbase_logging(self):
        self.cf_vote("HBase", "Rule_HBase_EventLogging", 0.40,
                     "HBase on Hadoop handles large-scale unstructured "
                     "event logs with random read/write access over huge "
                     "datasets.")

    # --- Graph databases ----------------------------------------------

    @Rule(Company(relationships_complex=True),
          salience=10)
    def rule_neo4j_core(self):
        self.cf_vote("Neo4j", "Rule_Neo4j_ComplexRelationships", 0.65,
                     "Highly interconnected complex relationships are exactly "
                     "what graph databases like Neo4j are optimised to "
                     "traverse.")

    @Rule(Company(relationships_complex=True, cloud_native=True,
                  multi_region_replication=True),
          salience=10)
    def rule_neptune_cloud_graph(self):
        self.cf_vote("Amazon Neptune", "Rule_Neptune_CloudGraph", 0.45,
                     "Cloud-native graph data with multi-region replication "
                     "favors a managed graph service like Amazon Neptune.")

    # --- Search engines -----------------------------------------------

    @Rule(Company(full_text_search=True),
          salience=10)
    def rule_es_fulltext(self):
        self.cf_vote("Elasticsearch", "Rule_ES_FullTextSearch", 0.60,
                     "Strong full-text search maps directly onto "
                     "Elasticsearch's inverted-index engine.")

    @Rule(Company(full_text_search=True, open_source_preference=True,
                  budget_sensitive=True),
          salience=10)
    def rule_solr_oss_search(self):
        self.cf_vote("Apache Solr", "Rule_Solr_OpenSourceSearch", 0.30,
                     "Apache Solr is a mature, fully open-source search "
                     "platform – attractive when budget and OSS preference "
                     "combine.")

    # --- Time-series databases ----------------------------------------

    @Rule(Company(time_series_data=True),
          salience=10)
    def rule_influxdb_timeseries(self):
        self.cf_vote("InfluxDB", "Rule_InfluxDB_TimeSeries", 0.60,
                     "Time-stamped sequential data such as IoT or monitoring "
                     "metrics is InfluxDB's core purpose-built use-case.")

    @Rule(Company(time_series_data=True, sql_compatibility=True),
          salience=10)
    def rule_timescale_sql_ts(self):
        self.cf_vote("TimescaleDB", "Rule_TimescaleDB_SQL_TS", 0.50,
                     "When time-series data must be queried with standard "
                     "SQL, TimescaleDB (built on PostgreSQL) is the "
                     "strongest fit.")

    @Rule(Company(time_series_data=True, big_data=True,
                  open_source_preference=True),
          NOT(Company(sql_compatibility=True)),
          salience=10)
    def rule_opentsdb_bigdata_ts(self):
        self.cf_vote("OpenTSDB", "Rule_OpenTSDB_BigDataTS", 0.30,
                     "OpenTSDB on HBase suits very large-scale open-source "
                     "time-series storage without a SQL requirement.")

    # --- OLAP / data warehouse ----------------------------------------

    @Rule(Company(olap_workload=True, cloud_native=True),
          NOT(Company(open_source_preference=True)),
          salience=10)
    def rule_snowflake_cloud_olap(self):
        self.cf_vote("Snowflake", "Rule_Snowflake_CloudOLAP", 0.55,
                     "Cloud-native OLAP without open-source constraint fits "
                     "Snowflake's fully managed data warehouse model.")

    @Rule(Company(olap_workload=True, embedded_database=True),
          salience=10)
    def rule_duckdb_embedded_olap(self):
        self.cf_vote("DuckDB", "Rule_DuckDB_EmbeddedOLAP", 0.50,
                     "DuckDB brings OLAP analytical querying into an "
                     "embedded, in-process engine – ideal for local analytics "
                     "without a server.")

    # --- Vector search ------------------------------------------------

    @Rule(Company(vector_search=True),
          salience=10)
    def rule_clickhouse_vector(self):
        self.cf_vote("ClickHouse", "Rule_ClickHouse_VectorSearch", 0.30,
                     "Vector search / AI embedding workloads are natively "
                     "supported by ClickHouse's ANN indexing.")

    # --- Cross-cutting specialised factors ----------------------------

    @Rule(Company(geospatial_queries=True, structured_data=True),
          salience=10)
    def rule_pg_geospatial(self):
        self.cf_vote("PostgreSQL", "Rule_PG_Geospatial", 0.30,
                     "PostgreSQL + PostGIS extension provides mature, "
                     "standards-compliant geospatial query support.")

    @Rule(Company(geospatial_queries=True, unstructured_data=True),
          salience=10)
    def rule_mongo_geospatial(self):
        self.cf_vote("MongoDB", "Rule_MongoDB_Geospatial", 0.20,
                     "MongoDB's native geospatial indexes work naturally "
                     "alongside flexible document storage.")

    @Rule(Company(compliance_required=True, security_critical=True,
                  structured_data=True),
          salience=10)
    def rule_pg_compliance(self):
        self.cf_vote("PostgreSQL", "Rule_PG_ComplianceSecurity", 0.25,
                     "Regulatory compliance + security + structured data: "
                     "PostgreSQL's fine-grained access control, row-level "
                     "security, and audit extensions meet GDPR/HIPAA needs.")

    @Rule(Company(multi_tenancy=True, structured_data=True,
                  transactions=True),
          salience=10)
    def rule_pg_multitenancy(self):
        self.cf_vote("PostgreSQL", "Rule_PG_MultiTenancy", 0.15,
                     "PostgreSQL's schema-per-tenant or row-level security "
                     "is a standard pattern for multi-tenant transactional "
                     "apps.")

    @Rule(Company(streaming_data=True, event_logging=True),
          NOT(Company(olap_workload=True)),
          salience=10)
    def rule_cassandra_streaming_log(self):
        self.cf_vote("Cassandra", "Rule_Cassandra_StreamingEventLog", 0.20,
                     "High-throughput streaming event logs without a "
                     "dedicated OLAP layer append efficiently into "
                     "Cassandra's wide-column store.")

    # --- Multi-model --------------------------------------------------

    @Rule(Company(unstructured_data=True, relationships_complex=True,
                  json_support=True),
          salience=10)
    def rule_arangodb_multimodel(self):
        self.cf_vote("ArangoDB", "Rule_ArangoDB_DocPlusGraph", 0.55,
                     "Needing both document-style JSON and complex graph "
                     "queries favors a multi-model database like ArangoDB "
                     "over two separate systems.")

    @Rule(Company(relationships_complex=True, flexible_schema=True),
          NOT(Company(big_data=True)),
          salience=10)
    def rule_orientdb_multimodel(self):
        self.cf_vote("OrientDB", "Rule_OrientDB_GraphPlusDoc", 0.30,
                     "OrientDB blends graph and document models for "
                     "flexible, relationship-rich data without massive "
                     "horizontal scale.")



    # --- Cassandra penalties ------------------------------------------

    @Rule(Company(big_data=False),
          salience=15)
    def rule_penalty_cassandra_no_bigdata(self):
        self.cf_vote("Cassandra", "Penalty_Cassandra_NoBigData", -0.70,
                     "PENALTY: Cassandra's operational complexity is "
                     "unjustified without a big-data volume requirement.")

    @Rule(Company(flexible_schema=False, structured_data=True),
          salience=15)
    def rule_penalty_cassandra_no_flex_schema(self):
        self.cf_vote("Cassandra", "Penalty_Cassandra_NoFlexSchema", -0.50,
                     "PENALTY: Cassandra suits schema-flexible workloads; "
                     "rigid structured data favors relational databases.")

    @Rule(Company(transactions=True),
          salience=15)
    def rule_penalty_cassandra_acid(self):
        self.cf_vote("Cassandra", "Penalty_Cassandra_ACIDRequired", -0.60,
                     "PENALTY: Cassandra offers only lightweight transactions; "
                     "a full ACID requirement is better served by PostgreSQL "
                     "or MySQL.")

    # --- MongoDB penalties --------------------------------------------

    @Rule(Company(flexible_schema=False),
          salience=15)
    def rule_penalty_mongo_no_flex(self):
        self.cf_vote("MongoDB", "Penalty_MongoDB_NoFlexSchema", -0.60,
                     "PENALTY: MongoDB's main advantage is schema flexibility; "
                     "without it, a relational database is usually preferable.")

    @Rule(Company(transactions=True, structured_data=True,
                  sql_compatibility=True),
          salience=15)
    def rule_penalty_mongo_acid_sql(self):
        self.cf_vote("MongoDB", "Penalty_MongoDB_ACID_SQL", -0.70,
                     "PENALTY: Requiring ACID transactions on structured data "
                     "with SQL compatibility is a strong contra-indicator for "
                     "MongoDB.")

    # --- Redis penalties ----------------------------------------------

    @Rule(Company(caching_needed=False, low_latency=False),
          salience=15)
    def rule_penalty_redis_no_cache_latency(self):
        self.cf_vote("Redis", "Penalty_Redis_NoCacheOrLatency", -0.60,
                     "PENALTY: Without caching or low-latency requirements, "
                     "Redis's in-memory model is usually overkill and costly.")

    @Rule(Company(big_data=True, olap_workload=True),
          salience=15)
    def rule_penalty_redis_bigdata_olap(self):
        self.cf_vote("Redis", "Penalty_Redis_BigDataOLAP", -0.55,
                     "PENALTY: Redis is an in-memory store; big-data OLAP "
                     "workloads are far better served by columnar engines "
                     "like ClickHouse or Druid.")

    # --- Elasticsearch penalties --------------------------------------

    @Rule(Company(full_text_search=False),
          salience=15)
    def rule_penalty_es_no_search(self):
        self.cf_vote("Elasticsearch", "Penalty_ES_NoFullTextSearch", -0.65,
                     "PENALTY: Elasticsearch's primary value is full-text "
                     "search; without that requirement its operational "
                     "overhead is hard to justify.")

    @Rule(Company(transactions=True, structured_data=True),
          NOT(Company(full_text_search=True)),
          salience=15)
    def rule_penalty_es_transactional(self):
        self.cf_vote("Elasticsearch", "Penalty_ES_TransactionalWorkload", -0.60,
                     "PENALTY: Elasticsearch is eventually consistent and has "
                     "no native ACID transactions; transactional workloads "
                     "should use a relational database.")

    # --- Neo4j penalties ----------------------------------------------

    @Rule(Company(relationships_complex=False),
          salience=15)
    def rule_penalty_neo4j_no_relationships(self):
        self.cf_vote("Neo4j", "Penalty_Neo4j_NoRelationships", -0.80,
                     "PENALTY: Neo4j's core value is traversing complex "
                     "relationships; without that requirement, relational or "
                     "document databases are more appropriate.")

    # --- Snowflake penalties ------------------------------------------

    @Rule(Company(olap_workload=False),
          salience=15)
    def rule_penalty_snowflake_no_olap(self):
        self.cf_vote("Snowflake", "Penalty_Snowflake_NoOLAP", -0.70,
                     "PENALTY: Snowflake is a cloud data warehouse optimised "
                     "for OLAP; without that workload type it is an expensive "
                     "misfit.")

    @Rule(Company(open_source_preference=True),
          salience=15)
    def rule_penalty_snowflake_oss(self):
        self.cf_vote("Snowflake", "Penalty_Snowflake_OSSPreference", -0.50,
                     "PENALTY: Snowflake is a proprietary managed service; "
                     "an open-source preference conflicts with using it.")

    # --- ClickHouse penalties -----------------------------------------

    @Rule(Company(olap_workload=False, analytics_focus=False,
                  vector_search=False),
          salience=15)
    def rule_penalty_clickhouse_no_olap(self):
        self.cf_vote("ClickHouse", "Penalty_ClickHouse_NoOLAPOrAnalytics", -0.65,
                     "PENALTY: ClickHouse is a columnar OLAP engine; without "
                     "analytical or vector-search workloads it is unnecessarily "
                     "complex.")

    # --- DynamoDB penalties -------------------------------------------

    @Rule(Company(open_source_preference=True),
          salience=15)
    def rule_penalty_dynamodb_oss(self):
        self.cf_vote("Amazon DynamoDB", "Penalty_DynamoDB_OSSPreference", -0.60,
                     "PENALTY: DynamoDB is a proprietary AWS-only service; "
                     "an open-source preference is a direct conflict.")

    @Rule(Company(cloud_native=False),
          salience=15)
    def rule_penalty_dynamodb_no_cloud(self):
        self.cf_vote("Amazon DynamoDB", "Penalty_DynamoDB_NoCloud", -0.70,
                     "PENALTY: DynamoDB is an AWS-managed service; on-premises "
                     "or cloud-agnostic deployments cannot use it.")

    # --- SQLite penalties ---------------------------------------------

    @Rule(Company(big_data=True),
          salience=15)
    def rule_penalty_sqlite_bigdata(self):
        self.cf_vote("SQLite", "Penalty_SQLite_BigData", -0.90,
                     "PENALTY: SQLite is a single-file embedded engine; it "
                     "cannot handle big-data volumes or concurrent write "
                     "loads.")

    @Rule(Company(horizontal_scalability=True),
          salience=15)
    def rule_penalty_sqlite_horizontal(self):
        self.cf_vote("SQLite", "Penalty_SQLite_HorizontalScale", -0.80,
                     "PENALTY: SQLite has no clustering or replication; "
                     "horizontal scalability is fundamentally unsupported.")

    @Rule(Company(multi_tenancy=True, transactions=True),
          salience=15)
    def rule_penalty_sqlite_multitenancy(self):
        self.cf_vote("SQLite", "Penalty_SQLite_MultiTenancy", -0.70,
                     "PENALTY: SQLite's file-level locking makes it "
                     "unsuitable for concurrent multi-tenant transactional "
                     "workloads.")



    # --- Project domain rules -----------------------------------------

    @Rule(Company(project_domain="finance"),
          salience=5)
    def rule_ctx_domain_finance(self):
        self.cf_vote("PostgreSQL", "Ctx_Domain_Finance", 0.14,
                     "Finance domain: ACID compliance, mature auditing, and "
                     "regulatory tooling make PostgreSQL the de-facto standard "
                     "for financial systems.")

    @Rule(Company(project_domain="healthcare"),
          salience=5)
    def rule_ctx_domain_healthcare(self):
        self.cf_vote("PostgreSQL", "Ctx_Domain_Healthcare", 0.14,
                     "Healthcare domain: HIPAA compliance, audit trails, and "
                     "strong access control align naturally with PostgreSQL.")

    @Rule(Company(project_domain="iot"),
          salience=5)
    def rule_ctx_domain_iot(self):
        self.cf_vote("InfluxDB", "Ctx_Domain_IoT_InfluxDB", 0.14,
                     "IoT domain: Time-stamped sensor data is InfluxDB's "
                     "primary design target.")

    @Rule(Company(project_domain="iot"),
          salience=5)
    def rule_ctx_domain_iot_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_Domain_IoT_Cassandra", 0.10,
                     "IoT domain at scale: Cassandra's write-optimised, "
                     "append-only model handles high-throughput sensor "
                     "ingestion well.")

    @Rule(Company(project_domain="social"),
          salience=5)
    def rule_ctx_domain_social(self):
        self.cf_vote("Neo4j", "Ctx_Domain_Social_Neo4j", 0.14,
                     "Social domain: friend graphs, follower networks, and "
                     "recommendation engines are Neo4j's natural habitat.")

    @Rule(Company(project_domain="social"),
          salience=5)
    def rule_ctx_domain_social_mongo(self):
        self.cf_vote("MongoDB", "Ctx_Domain_Social_MongoDB", 0.10,
                     "Social domain: activity feeds and user profiles with "
                     "varying fields suit a flexible document model.")

    @Rule(Company(project_domain="analytics"),
          salience=5)
    def rule_ctx_domain_analytics(self):
        self.cf_vote("ClickHouse", "Ctx_Domain_Analytics", 0.14,
                     "Analytics domain: ClickHouse's columnar engine is the "
                     "top-performing choice for analytical dashboards.")

    @Rule(Company(project_domain="ecommerce"),
          salience=5)
    def rule_ctx_domain_ecommerce(self):
        self.cf_vote("PostgreSQL", "Ctx_Domain_Ecommerce", 0.12,
                     "E-commerce domain: product catalogs, orders, and "
                     "inventory management rely on ACID transactions, which "
                     "PostgreSQL handles exceptionally well.")

    @Rule(Company(project_domain="content"),
          salience=5)
    def rule_ctx_domain_content(self):
        self.cf_vote("MongoDB", "Ctx_Domain_Content", 0.12,
                     "Content management domain: varying article structures "
                     "and metadata fit MongoDB's flexible document model.")

    # --- Workload pattern rules ---------------------------------------

    @Rule(Company(workload_pattern="read_heavy"),
          salience=5)
    def rule_ctx_read_heavy_redis(self):
        self.cf_vote("Redis", "Ctx_ReadHeavy_Redis", 0.10,
                     "Read-heavy workload: Redis's in-memory reads provide "
                     "the highest read throughput available.")

    @Rule(Company(workload_pattern="read_heavy"),
          salience=5)
    def rule_ctx_read_heavy_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_ReadHeavy_PG", 0.08,
                     "Read-heavy workload: PostgreSQL's MVCC enables "
                     "excellent concurrent read performance with connection "
                     "pooling (PgBouncer).")

    @Rule(Company(workload_pattern="write_heavy"),
          salience=5)
    def rule_ctx_write_heavy_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_WriteHeavy_Cassandra", 0.12,
                     "Write-heavy workload: Cassandra's log-structured "
                     "merge-tree storage is optimised for sustained high "
                     "write throughput.")

    @Rule(Company(workload_pattern="write_heavy"),
          salience=5)
    def rule_ctx_write_heavy_mongo(self):
        self.cf_vote("MongoDB", "Ctx_WriteHeavy_MongoDB", 0.08,
                     "Write-heavy workload: MongoDB's write concern tuning "
                     "and journaling support high-throughput document "
                     "ingestion.")

    # --- TPS (transactions per second) rules --------------------------

    @Rule(Company(tps="very_high", transactions=True),
          salience=5)
    def rule_ctx_tps_very_high_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_TPS_VeryHigh_PG", 0.12,
                     "Very high TPS + ACID: PostgreSQL with PgBouncer and "
                     "logical replication handles tens of thousands of "
                     "transactions per second reliably.")

    @Rule(Company(tps="very_high", big_data=True),
          salience=5)
    def rule_ctx_tps_very_high_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_TPS_VeryHigh_Cassandra", 0.12,
                     "Very high TPS at big-data scale: Cassandra's "
                     "masterless architecture sustains millions of writes "
                     "per second across a cluster.")

    @Rule(Company(tps="very_high", caching_needed=True),
          salience=5)
    def rule_ctx_tps_very_high_redis(self):
        self.cf_vote("Redis", "Ctx_TPS_VeryHigh_Redis", 0.12,
                     "Very high TPS + caching: Redis can handle millions "
                     "of operations per second from DRAM, making it the "
                     "fastest layer in any stack.")

    # --- Database size rules ------------------------------------------

    @Rule(Company(db_size="massive", horizontal_scalability=True),
          salience=5)
    def rule_ctx_massive_db_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_MassiveDB_Cassandra", 0.12,
                     "Massive database + horizontal scalability: Cassandra "
                     "scales to petabytes by simply adding nodes.")

    @Rule(Company(db_size="massive", olap_workload=True),
          salience=5)
    def rule_ctx_massive_db_clickhouse(self):
        self.cf_vote("ClickHouse", "Ctx_MassiveDB_ClickHouse", 0.12,
                     "Massive database + OLAP: ClickHouse's columnar "
                     "compression and sharding are designed for petabyte-scale "
                     "analytical queries.")

    @Rule(Company(db_size="small", embedded_database=True),
          salience=5)
    def rule_ctx_small_db_sqlite(self):
        self.cf_vote("SQLite", "Ctx_SmallDB_SQLite", 0.10,
                     "Small database + embedded: SQLite is the clear "
                     "winner for small, self-contained datasets that need "
                     "zero infrastructure.")

    # --- Concurrent users rules ---------------------------------------

    @Rule(Company(concurrent_users="very_high",
                  horizontal_scalability=True),
          salience=5)
    def rule_ctx_high_concurrency_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_HighConcurrency_Cassandra", 0.11,
                     "Very high concurrent users + horizontal scale: "
                     "Cassandra's peer-to-peer topology serves any concurrency "
                     "level by adding nodes.")

    @Rule(Company(concurrent_users="very_high",
                  caching_needed=True),
          salience=5)
    def rule_ctx_high_concurrency_redis(self):
        self.cf_vote("Redis", "Ctx_HighConcurrency_Redis", 0.11,
                     "Very high concurrent users + caching: Redis Cluster "
                     "can serve millions of concurrent connections via "
                     "in-memory reads.")

    @Rule(Company(concurrent_users="very_high",
                  transactions=True),
          salience=5)
    def rule_ctx_high_concurrency_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_HighConcurrency_PG", 0.09,
                     "Very high concurrent users + transactions: PostgreSQL "
                     "with PgBouncer pooling handles high concurrency while "
                     "preserving ACID guarantees.")

    # --- Data growth rules --------------------------------------------

    @Rule(Company(data_growth="explosive",
                  horizontal_scalability=True),
          salience=5)
    def rule_ctx_explosive_growth_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_ExplosiveGrowth_Cassandra", 0.12,
                     "Explosive data growth + horizontal scale: Cassandra's "
                     "linear scalability absorbs rapid growth by adding nodes "
                     "with no downtime.")

    @Rule(Company(data_growth="explosive",
                  unstructured_data=True),
          salience=5)
    def rule_ctx_explosive_growth_mongo(self):
        self.cf_vote("MongoDB", "Ctx_ExplosiveGrowth_MongoDB", 0.10,
                     "Explosive growth + unstructured data: MongoDB's "
                     "auto-sharding distributes documents across nodes as "
                     "the dataset grows.")

    @Rule(Company(data_growth="slow"),
          salience=5)
    def rule_ctx_slow_growth_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_SlowGrowth_PG", 0.08,
                     "Slow data growth: a well-tuned PostgreSQL instance "
                     "can serve a stable dataset for years without "
                     "infrastructure changes.")

    # --- Backup strategy / disaster recovery rules --------------------

    @Rule(Company(backup_strategy="enterprise",
                  structured_data=True),
          salience=5)
    def rule_ctx_backup_enterprise_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_Backup_Enterprise_PG", 0.10,
                     "Enterprise backup strategy + structured data: "
                     "PostgreSQL supports pg_basebackup, WAL archiving, "
                     "PITR, and integrates with enterprise backup tools.")

    @Rule(Company(disaster_recovery="enterprise",
                  high_availability=True),
          salience=5)
    def rule_ctx_dr_enterprise_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_DR_Enterprise_PG", 0.10,
                     "Enterprise disaster recovery + HA: PostgreSQL's "
                     "streaming and logical replication with automated "
                     "failover (Patroni) satisfies enterprise DR requirements.")

    @Rule(Company(disaster_recovery="enterprise",
                  high_availability=True,
                  fault_tolerance=True),
          salience=5)
    def rule_ctx_dr_enterprise_cassandra(self):
        self.cf_vote("Cassandra", "Ctx_DR_Enterprise_Cassandra", 0.10,
                     "Enterprise DR + HA + fault tolerance: Cassandra's "
                     "multi-datacenter replication provides native active-active "
                     "disaster recovery.")

    # --- Team SQL experience rules ------------------------------------

    @Rule(Company(team_sql_experience="high"),
          salience=5)
    def rule_ctx_sql_exp_high_pg(self):
        self.cf_vote("PostgreSQL", "Ctx_SQLExp_High_PG", 0.10,
                     "High SQL experience: the team can fully leverage "
                     "PostgreSQL's advanced SQL features (window functions, "
                     "CTEs, partitioning, FDW).")

    @Rule(Company(team_sql_experience="high"),
          salience=5)
    def rule_ctx_sql_exp_high_mysql(self):
        self.cf_vote("MySQL", "Ctx_SQLExp_High_MySQL", 0.08,
                     "High SQL experience: MySQL is a well-understood, "
                     "widely documented relational engine that SQL-fluent "
                     "teams ramp onto quickly.")

    @Rule(Company(team_sql_experience="none"),
          salience=5)
    def rule_ctx_sql_exp_none_mongo(self):
        self.cf_vote("MongoDB", "Ctx_SQLExp_None_MongoDB", 0.08,
                     "No SQL experience: MongoDB's query language and "
                     "document model have a lower barrier to entry for "
                     "teams without SQL backgrounds.")

    @Rule(Company(team_sql_experience="none"),
          salience=5)
    def rule_ctx_sql_exp_none_redis(self):
        self.cf_vote("Redis", "Ctx_SQLExp_None_Redis", 0.06,
                     "No SQL experience: Redis's simple command-based API "
                     "is easy to learn without prior database knowledge.")



    @Rule(Company(
        structured_data=False, unstructured_data=False,
        semi_structured_data=False, transactions=False,
        flexible_schema=False, big_data=False,
        relationships_complex=False, json_support=False,
        sql_compatibility=False, geospatial_queries=False,
        vector_search=False, high_read_speed=False,
        caching_needed=False, low_latency=False,
        real_time_analytics=False, oltp_workload=False,
        olap_workload=False, streaming_data=False,
        event_logging=False, time_series_data=False,
        full_text_search=False, analytics_focus=False,
    ))
    def rule_no_requirements(self):
        self.fired_rule_log.append("Rule_NoRequirementsDetected")
