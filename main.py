

import compat  
from facts import Company
from engine import DatabaseExpert
from rejections import explain_rejection
from formatter import (
    print_header,
    print_input_facts,
    print_fired_rules,
    print_ranked_recommendations,
    print_rejected_alternatives,
    print_categorized_recommendations,
    print_final_ranking,
)


BOOL_QUESTIONNAIRE = [
    ("structured_data",          "Is the data structured (tables/columns)?"),
    ("unstructured_data",        "Is there unstructured data (JSON/free text)?"),
    ("semi_structured_data",     "Is the data semi-structured (e.g. XML, nested JSON)?"),
    ("transactions",             "Does the company need ACID transactions?"),
    ("flexible_schema",          "Do you need a flexible/changeable schema?"),
    ("big_data",                 "Is the data volume very large (Big Data)?"),
    ("relationships_complex",    "Are there complex relationships between entities?"),
    ("json_support",             "Do you need native JSON support?"),
    ("sql_compatibility",        "Do you need SQL compatibility?"),
    ("geospatial_queries",       "Do you need geospatial queries?"),
    ("vector_search",            "Do you need vector search / AI embeddings support?"),
    ("high_read_speed",          "Do you need very high read speed?"),
    ("caching_needed",           "Do you need a caching layer?"),
    ("low_latency",              "Is low latency a critical requirement?"),
    ("real_time_analytics",      "Do you need real-time analytics?"),
    ("oltp_workload",            "Is this primarily an OLTP (transactional) workload?"),
    ("olap_workload",            "Is this primarily an OLAP (analytical) workload?"),
    ("streaming_data",           "Do you need to ingest streaming data?"),
    ("event_logging",            "Do you need large-scale event logging?"),
    ("time_series_data",         "Is the data time-series (IoT/monitoring)?"),
    ("full_text_search",         "Do you need strong full-text search?"),
    ("analytics_focus",          "Is analytics a primary focus of this system?"),
    ("horizontal_scalability",   "Do you need horizontal scalability?"),
    ("vertical_scalability",     "Do you need vertical scalability?"),
    ("cloud_native",             "Will this be deployed as cloud-native?"),
    ("multi_region_replication", "Do you need multi-region replication?"),
    ("high_availability",        "Is high availability a requirement?"),
    ("fault_tolerance",          "Is fault tolerance a requirement?"),
    ("embedded_database",        "Do you need an embedded (serverless) database?"),
    ("offline_first",            "Do you need offline-first support?"),
    ("data_retention_long_term", "Do you need long-term data retention?"),
    ("backup_required",          "Are regular backups a strict requirement?"),
    ("security_critical",        "Is security a critical concern?"),
    ("compliance_required",      "Do you need regulatory compliance (e.g. GDPR/HIPAA)?"),
    ("multi_tenancy",            "Do you need multi-tenancy support?"),
    ("budget_sensitive",         "Is the project budget-sensitive?"),
    ("open_source_preference",   "Do you prefer open-source technology?"),
]


CATEGORICAL_QUESTIONNAIRE = [
    ("concurrent_users",
     "Estimated concurrent users?  [1=low  2=medium  3=high  4=very_high]",
     {"1": "low", "2": "medium", "3": "high", "4": "very_high"}),

    ("db_size",
     "Anticipated database size?   [1=small  2=medium  3=large  4=massive]",
     {"1": "small", "2": "medium", "3": "large", "4": "massive"}),

    ("workload_pattern",
     "Dominant workload pattern?   [1=read_heavy  2=write_heavy  3=balanced]",
     {"1": "read_heavy", "2": "write_heavy", "3": "balanced"}),

    ("tps",
     "Expected transactions/sec?   [1=low  2=medium  3=high  4=very_high]",
     {"1": "low", "2": "medium", "3": "high", "4": "very_high"}),

    ("project_domain",
     "Project domain?  "
     "[1=ecommerce  2=finance  3=iot  4=social  5=analytics  "
     "6=content  7=healthcare  8=general]",
     {"1": "ecommerce", "2": "finance", "3": "iot", "4": "social",
      "5": "analytics", "6": "content", "7": "healthcare", "8": "general"}),

    ("data_growth",
     "Expected data growth rate?   [1=slow  2=moderate  3=fast  4=explosive]",
     {"1": "slow", "2": "moderate", "3": "fast", "4": "explosive"}),

    ("backup_strategy",
     "Backup strategy maturity?    [1=none  2=basic  3=advanced  4=enterprise]",
     {"1": "none", "2": "basic", "3": "advanced", "4": "enterprise"}),

    ("disaster_recovery",
     "Disaster recovery level?     [1=none  2=basic  3=advanced  4=enterprise]",
     {"1": "none", "2": "basic", "3": "advanced", "4": "enterprise"}),

    ("team_sql_experience",
     "Team SQL experience level?   [1=none  2=low  3=medium  4=high]",
     {"1": "none", "2": "low", "3": "medium", "4": "high"}),
]

FULL_FIELD_ORDER = (
    [pair[0] for pair in BOOL_QUESTIONNAIRE]
    + [pair[0] for pair in CATEGORICAL_QUESTIONNAIRE]
)


def ask_yes_no(question):
  
    answer = input(f"{question} (y/n): ").strip().lower()
    return answer == "y"


def ask_categorical(question, mapping):
    
    answer = input(f"{question}: ").strip()
    # dict.get with the first mapping value as default for unknown input
    default = next(iter(mapping.values()))
    return mapping.get(answer, default)


def build_facts_from_user():
   
    print("\nPlease answer the following questions about your company's "
          "requirements:\n")
    bool_facts = dict(map(
        lambda pair: (pair[0], ask_yes_no(pair[1])),
        BOOL_QUESTIONNAIRE,
    ))
    print("\nAdditional context (press Enter to accept default):\n")
    cat_facts = dict(map(
        lambda triple: (triple[0], ask_categorical(triple[1], triple[2])),
        CATEGORICAL_QUESTIONNAIRE,
    ))
    bool_facts.update(cat_facts)
    return bool_facts


def run_case(case_title, facts_dict):
    print_header(f"CASE: {case_title}")

    bool_defaults = dict(map(
        lambda pair: (pair[0], facts_dict.get(pair[0], False)),
        BOOL_QUESTIONNAIRE,
    ))
    cat_defaults = dict(map(
        lambda triple: (triple[0], facts_dict.get(triple[0], next(iter(triple[2].values())))),
        CATEGORICAL_QUESTIONNAIRE,
    ))
    bool_defaults.update(cat_defaults)
    full_facts = bool_defaults

    print_input_facts(full_facts)

    engine = DatabaseExpert()
    engine.reset()
    engine.declare(Company(**full_facts))
    engine.run()
    engine.combine_cfs()

    print_fired_rules(engine.fired_rule_log)
    print_ranked_recommendations(engine.scores, engine.matched_rules)
    print_categorized_recommendations(engine.scores)
    print_rejected_alternatives(engine.scores, full_facts, explain_rejection)
    print_final_ranking(engine.scores)



DEMO_CASES = [
    ("Banking system requiring strict transactions",
     {"structured_data": True, "transactions": True, "sql_compatibility": True,
      "security_critical": True, "compliance_required": True,
      "project_domain": "finance", "tps": "high",
      "backup_strategy": "enterprise", "disaster_recovery": "enterprise",
      "team_sql_experience": "high"}),

    ("Content management platform with flexible JSON documents",
     {"unstructured_data": True, "flexible_schema": True, "json_support": True,
      "big_data": True, "project_domain": "content",
      "workload_pattern": "read_heavy", "data_growth": "fast"}),

    ("Real-time caching layer for a high-traffic web app",
     {"caching_needed": True, "high_read_speed": True, "low_latency": True,
      "real_time_analytics": True, "concurrent_users": "very_high",
      "workload_pattern": "read_heavy", "tps": "very_high"}),

    ("IoT sensor monitoring platform",
     {"time_series_data": True, "sql_compatibility": True,
      "streaming_data": True, "project_domain": "iot",
      "data_growth": "fast", "db_size": "large"}),

    ("Social network with deeply interconnected user relationships",
     {"relationships_complex": True, "cloud_native": True,
      "multi_region_replication": True, "project_domain": "social",
      "concurrent_users": "very_high", "data_growth": "explosive"}),

    ("E-commerce search and analytics engine",
     {"full_text_search": True, "analytics_focus": True,
      "project_domain": "ecommerce", "transactions": True,
      "structured_data": True, "sql_compatibility": True}),

    ("Large-scale analytical data warehouse",
     {"olap_workload": True, "real_time_analytics": True,
      "streaming_data": True, "project_domain": "analytics",
      "db_size": "massive", "workload_pattern": "read_heavy"}),

    ("Embedded local-first mobile application",
     {"structured_data": True, "embedded_database": True,
      "offline_first": True, "db_size": "small",
      "concurrent_users": "low", "team_sql_experience": "medium"}),

    ("Healthcare patient records system",
     {"structured_data": True, "transactions": True,
      "sql_compatibility": True, "compliance_required": True,
      "security_critical": True, "high_availability": True,
      "project_domain": "healthcare", "backup_strategy": "enterprise",
      "disaster_recovery": "enterprise", "team_sql_experience": "high"}),

    ("A case with no specified requirements", {}),
]


def _run_interactive_case():
    facts = build_facts_from_user()
    run_case("Your entered case", facts)


def _run_all_demo_cases():
    _run(map(lambda pair: run_case(pair[0], pair[1]), DEMO_CASES))


def _run(iterable):
 
    import collections as _c
    _c.deque(iterable, maxlen=0)


def main():
    print_header("EXPERT SYSTEM FOR DATABASE TECHNOLOGY SELECTION")
    print("Python + Experta  |  Rule-Based Knowledge System  |  v3\n")
    print("Choose how to run the program:")
    print("  1) Run ready-made demo cases")
    print("  2) Enter your own company's data (interactive)\n")

    choice = input("Your choice (1/2): ").strip()

    dispatch = {"2": _run_interactive_case}
    dispatch.get(choice, _run_all_demo_cases)()


__name__ == "__main__" and main()
