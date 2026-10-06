

import compat  
from experta import Fact, Field


class Company(Fact):


    # --- Core data characteristics -------------------------------------
    structured_data        = Field(bool, default=False)
    unstructured_data      = Field(bool, default=False)
    semi_structured_data   = Field(bool, default=False)
    transactions           = Field(bool, default=False)
    flexible_schema        = Field(bool, default=False)
    big_data               = Field(bool, default=False)
    relationships_complex  = Field(bool, default=False)
    json_support           = Field(bool, default=False)
    sql_compatibility      = Field(bool, default=False)
    geospatial_queries     = Field(bool, default=False)
    vector_search          = Field(bool, default=False)

    # --- Performance characteristics ------------------------------------
    high_read_speed        = Field(bool, default=False)
    caching_needed         = Field(bool, default=False)
    low_latency            = Field(bool, default=False)
    real_time_analytics    = Field(bool, default=False)

    # --- Workload type --------------------------------------------------
    oltp_workload          = Field(bool, default=False)
    olap_workload          = Field(bool, default=False)
    streaming_data         = Field(bool, default=False)
    event_logging          = Field(bool, default=False)
    time_series_data       = Field(bool, default=False)
    full_text_search       = Field(bool, default=False)
    analytics_focus        = Field(bool, default=False)

    # --- Infrastructure / deployment -----------------------------------
    horizontal_scalability = Field(bool, default=False)
    vertical_scalability   = Field(bool, default=False)
    cloud_native           = Field(bool, default=False)
    multi_region_replication = Field(bool, default=False)
    high_availability      = Field(bool, default=False)
    fault_tolerance        = Field(bool, default=False)
    embedded_database      = Field(bool, default=False)
    offline_first          = Field(bool, default=False)

    # --- Operational / business constraints ----------------------------
    data_retention_long_term = Field(bool, default=False)
    backup_required        = Field(bool, default=False)
    security_critical      = Field(bool, default=False)
    compliance_required    = Field(bool, default=False)
    multi_tenancy          = Field(bool, default=False)
    budget_sensitive       = Field(bool, default=False)
    open_source_preference = Field(bool, default=False)

    # --- NEW v3: Quantitative / categorical context --------------------
    concurrent_users       = Field(str, default="medium")
    db_size                = Field(str, default="medium")
    workload_pattern       = Field(str, default="balanced")
    tps                    = Field(str, default="medium")
    project_domain         = Field(str, default="general")
    data_growth            = Field(str, default="moderate")
    backup_strategy        = Field(str, default="basic")
    disaster_recovery      = Field(str, default="basic")
    team_sql_experience    = Field(str, default="medium")




class FiredRule(Fact):

    rule_name = Field(str, mandatory=True)
    db_name   = Field(str, mandatory=True)
    cf_value  = Field(float, mandatory=True)
    reason    = Field(str, mandatory=True)


class DatabaseCF(Fact):
   
    db_name     = Field(str, mandatory=True)
    cf_combined = Field(float, mandatory=True)
