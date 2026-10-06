

import sys
import collections
import functools

import compat 

from facts import Company
from engine import DatabaseExpert
from catalog import ALL_DATABASES, DB_TO_CATEGORY, CATEGORY_TO_SECTION
from rejections import explain_rejection

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter,
    QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QCheckBox, QComboBox, QPushButton, QTabWidget,
    QFrame, QProgressBar, QSizePolicy, QGridLayout,
    QGroupBox, QMessageBox, QSpacerItem,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon



BOOL_QUESTIONNAIRE = [
    ("structured_data",          "Structured data (tables/columns)?"),
    ("unstructured_data",        "Unstructured data (JSON / free text)?"),
    ("semi_structured_data",     "Semi-structured data (XML, nested JSON)?"),
    ("transactions",             "ACID transactions required?"),
    ("flexible_schema",          "Flexible / changeable schema?"),
    ("big_data",                 "Very large data volume (Big Data)?"),
    ("relationships_complex",    "Complex relationships between entities?"),
    ("json_support",             "Native JSON support?"),
    ("sql_compatibility",        "SQL compatibility?"),
    ("geospatial_queries",       "Geospatial queries?"),
    ("vector_search",            "Vector search / AI embeddings support?"),
    ("high_read_speed",          "Very high read speed?"),
    ("caching_needed",           "Caching layer needed?"),
    ("low_latency",              "Low latency (critical)?"),
    ("real_time_analytics",      "Real-time analytics?"),
    ("oltp_workload",            "Primarily OLTP (transactional) workload?"),
    ("olap_workload",            "Primarily OLAP (analytical) workload?"),
    ("streaming_data",           "Streaming data ingestion?"),
    ("event_logging",            "Large-scale event logging?"),
    ("time_series_data",         "Time-series data (IoT / monitoring)?"),
    ("full_text_search",         "Strong full-text search?"),
    ("analytics_focus",          "Analytics as primary focus?"),
    ("horizontal_scalability",   "Horizontal scalability?"),
    ("vertical_scalability",     "Vertical scalability?"),
    ("cloud_native",             "Cloud-native deployment?"),
    ("multi_region_replication", "Multi-region replication?"),
    ("high_availability",        "High availability?"),
    ("fault_tolerance",          "Fault tolerance?"),
    ("embedded_database",        "Embedded (serverless) database?"),
    ("offline_first",            "Offline-first support?"),
    ("data_retention_long_term", "Long-term data retention?"),
    ("backup_required",          "Regular backups (strict requirement)?"),
    ("security_critical",        "Security is critical?"),
    ("compliance_required",      "Regulatory compliance (GDPR/HIPAA)?"),
    ("multi_tenancy",            "Multi-tenancy support?"),
    ("budget_sensitive",         "Budget-sensitive project?"),
    ("open_source_preference",   "Prefer open-source technology?"),
]

CATEGORICAL_QUESTIONNAIRE = [
    ("concurrent_users",     "Concurrent users",
     ["low", "medium", "high", "very_high"],      "medium"),
    ("db_size",              "Database size",
     ["small", "medium", "large", "massive"],      "medium"),
    ("workload_pattern",     "Workload pattern",
     ["read_heavy", "write_heavy", "balanced"],    "balanced"),
    ("tps",                  "Transactions / sec",
     ["low", "medium", "high", "very_high"],       "medium"),
    ("project_domain",       "Project domain",
     ["ecommerce", "finance", "iot", "social",
      "analytics", "content", "healthcare", "general"], "general"),
    ("data_growth",          "Data growth rate",
     ["slow", "moderate", "fast", "explosive"],    "moderate"),
    ("backup_strategy",      "Backup strategy",
     ["none", "basic", "advanced", "enterprise"],  "basic"),
    ("disaster_recovery",    "Disaster recovery",
     ["none", "basic", "advanced", "enterprise"],  "basic"),
    ("team_sql_experience",  "Team SQL experience",
     ["none", "low", "medium", "high"],            "medium"),
]

BOOL_GROUPS = [
    ("Core Data Characteristics",
     ["structured_data", "unstructured_data", "semi_structured_data",
      "transactions", "flexible_schema", "big_data", "relationships_complex",
      "json_support", "sql_compatibility", "geospatial_queries", "vector_search"]),
    ("Performance",
     ["high_read_speed", "caching_needed", "low_latency", "real_time_analytics"]),
    ("Workload Type",
     ["oltp_workload", "olap_workload", "streaming_data", "event_logging",
      "time_series_data", "full_text_search", "analytics_focus"]),
    ("Infrastructure & Deployment",
     ["horizontal_scalability", "vertical_scalability", "cloud_native",
      "multi_region_replication", "high_availability", "fault_tolerance",
      "embedded_database", "offline_first"]),
    ("Operational & Business",
     ["data_retention_long_term", "backup_required", "security_critical",
      "compliance_required", "multi_tenancy", "budget_sensitive",
      "open_source_preference"]),
]

DEMO_CASES = [
    ("Banking / Finance",
     {"structured_data": True, "transactions": True, "sql_compatibility": True,
      "security_critical": True, "compliance_required": True,
      "project_domain": "finance", "tps": "high",
      "backup_strategy": "enterprise", "disaster_recovery": "enterprise",
      "team_sql_experience": "high"}),
    ("Content / Flexible JSON",
     {"unstructured_data": True, "flexible_schema": True, "json_support": True,
      "big_data": True, "project_domain": "content",
      "workload_pattern": "read_heavy", "data_growth": "fast"}),
    ("High-Traffic Caching Layer",
     {"caching_needed": True, "high_read_speed": True, "low_latency": True,
      "real_time_analytics": True, "concurrent_users": "very_high",
      "workload_pattern": "read_heavy", "tps": "very_high"}),
    ("IoT Sensor Monitoring",
     {"time_series_data": True, "sql_compatibility": True,
      "streaming_data": True, "project_domain": "iot",
      "data_growth": "fast", "db_size": "large"}),
    ("Social Network (Graph)",
     {"relationships_complex": True, "cloud_native": True,
      "multi_region_replication": True, "project_domain": "social",
      "concurrent_users": "very_high", "data_growth": "explosive"}),
    ("E-commerce Search & Analytics",
     {"full_text_search": True, "analytics_focus": True,
      "project_domain": "ecommerce", "transactions": True,
      "structured_data": True, "sql_compatibility": True}),
    ("Analytics Data Warehouse",
     {"olap_workload": True, "real_time_analytics": True,
      "streaming_data": True, "project_domain": "analytics",
      "db_size": "massive", "workload_pattern": "read_heavy"}),
    ("Embedded / Offline Mobile App",
     {"structured_data": True, "embedded_database": True,
      "offline_first": True, "db_size": "small",
      "concurrent_users": "low", "team_sql_experience": "medium"}),
    ("Healthcare Patient Records",
     {"structured_data": True, "transactions": True,
      "sql_compatibility": True, "compliance_required": True,
      "security_critical": True, "high_availability": True,
      "project_domain": "healthcare", "backup_strategy": "enterprise",
      "disaster_recovery": "enterprise", "team_sql_experience": "high"}),
    ("No Requirements (blank)",
     {}),
]



class InferenceWorker(QThread):
    finished = pyqtSignal(object, object)   
    error    = pyqtSignal(str)

    def __init__(self, facts_dict):
        super().__init__()
        self.facts_dict = facts_dict

    def run(self):
        try:
            full_facts = {}
            for field, _ in BOOL_QUESTIONNAIRE:
                full_facts[field] = self.facts_dict.get(field, False)
            for field, _, _, default in CATEGORICAL_QUESTIONNAIRE:
                full_facts[field] = self.facts_dict.get(field, default)

            eng = DatabaseExpert()
            eng.reset()
            eng.declare(Company(**full_facts))
            eng.run()
            eng.combine_cfs()
            self.finished.emit(eng, full_facts)
        except Exception as exc:
            self.error.emit(str(exc))



def _confidence_color(score):
    """Returns a CSS color string based on confidence level."""
    pct = max(0, min(score, 100))
    if pct >= 70:
        return "#4ade80"  
    if pct >= 40:
        return "#facc15" 
    return "#f87171"      



class DbRecommendationCard(QFrame):
    def __init__(self, rank, db_name, score, matched_rules, parent=None):
        super().__init__(parent)
        self.setObjectName("dbCard")
        confidence = max(0, min(score, 100))
        color = _confidence_color(score)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header row
        header = QHBoxLayout()
        rank_lbl = QLabel(f"#{rank}")
        rank_lbl.setObjectName("rankLabel")
        name_lbl = QLabel(db_name)
        name_lbl.setObjectName("dbNameLabel")
        score_lbl = QLabel(f"CF: {score:.1f}%")
        score_lbl.setObjectName("scoreLabel")
        header.addWidget(rank_lbl)
        header.addWidget(name_lbl, 1)
        header.addWidget(score_lbl)
        layout.addLayout(header)

        # Confidence bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(round(confidence)))
        bar.setFormat(f"{confidence:.1f}% confidence")
        bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #334155;
                border-radius: 4px;
                background: #1e293b;
                height: 18px;
                text-align: center;
                color: #f1f5f9;
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(bar)

        # Rule list (collapsible via toggle)
        if matched_rules:
            toggle_btn = QPushButton("▶  Show matched rules")
            toggle_btn.setObjectName("toggleBtn")
            toggle_btn.setCheckable(True)
            toggle_btn.setChecked(False)
            layout.addWidget(toggle_btn)

            rules_widget = QWidget()
            rules_layout = QVBoxLayout(rules_widget)
            rules_layout.setContentsMargins(6, 4, 6, 4)
            rules_layout.setSpacing(4)
            rules_widget.setVisible(False)

            for rule_name, rule_score, reason in matched_rules:
                is_penalty = rule_name.startswith("Penalty_")
                prefix = "−" if is_penalty else "+"
                display = (rule_name
                           .replace("Rule_", "")
                           .replace("Penalty_", "[PENALTY] ")
                           .replace("Ctx_", "[CTX] ")
                           .replace("_", " "))
                score_str = f"{rule_score:.2f}" if rule_score < 0 else f"+{rule_score:.2f}"
                rcolor = "#f87171" if is_penalty else "#86efac"

                row = QHBoxLayout()
                score_badge = QLabel(f"{prefix} {score_str}")
                score_badge.setFixedWidth(52)
                score_badge.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                score_badge.setStyleSheet(f"color: {rcolor}; font-weight: 600; font-size: 11px;")

                rule_col = QVBoxLayout()
                rule_lbl = QLabel(display)
                rule_lbl.setObjectName("ruleName")
                reason_lbl = QLabel(reason)
                reason_lbl.setObjectName("ruleReason")
                reason_lbl.setWordWrap(True)
                rule_col.addWidget(rule_lbl)
                rule_col.addWidget(reason_lbl)

                row.addWidget(score_badge)
                row.addLayout(rule_col, 1)
                rules_layout.addLayout(row)

                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setObjectName("ruleSep")
                rules_layout.addWidget(sep)

            layout.addWidget(rules_widget)

            def _toggle(checked, btn=toggle_btn, w=rules_widget):
                btn.setText("▼  Hide matched rules" if checked else "▶  Show matched rules")
                w.setVisible(checked)

            toggle_btn.toggled.connect(_toggle)



class ResultsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.placeholder = QLabel("Run an analysis to see recommendations here.")
        self.placeholder.setObjectName("placeholder")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.placeholder)

        self.tabs = QTabWidget()
        self.tabs.setVisible(False)
        layout.addWidget(self.tabs)

    def display(self, engine, facts_dict):
        self.placeholder.setVisible(False)
        self.tabs.setVisible(True)
        self.tabs.clear()

        # Build sorted results
        positive = {k: v for k, v in engine.scores.items() if v > 0}
        ranked = sorted(positive.items(), key=lambda x: x[1], reverse=True)
        not_recommended = [db for db in ALL_DATABASES if engine.scores.get(db, 0) <= 0]

        # ── Tab 1: Summary ────────────────────────────────────────────────
        summary_tab = QScrollArea()
        summary_tab.setWidgetResizable(True)
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        summary_layout.setSpacing(10)
        summary_layout.setContentsMargins(16, 16, 16, 16)

        # Category grouping
        by_category = {}
        for db_name, score in ranked:
            cat = DB_TO_CATEGORY.get(db_name, "Other")
            if cat not in by_category or score > by_category[cat][1]:
                by_category[cat] = (db_name, score)

        if by_category:
            cat_title = QLabel("Best Recommendation per Category")
            cat_title.setObjectName("sectionTitle")
            summary_layout.addWidget(cat_title)

            sections_sorted = sorted(by_category.items(),
                                     key=lambda kv: kv[1][1], reverse=True)
            grid = QGridLayout()
            grid.setSpacing(10)
            for col, (cat, (db_name, score)) in enumerate(sections_sorted):
                section_label = CATEGORY_TO_SECTION.get(cat, cat)
                confidence = max(0, min(score, 100))
                color = _confidence_color(score)

                card = QFrame()
                card.setObjectName("summaryCard")
                cl = QVBoxLayout(card)
                cl.setContentsMargins(12, 10, 12, 10)
                cl.setSpacing(4)

                sec_lbl = QLabel(section_label)
                sec_lbl.setObjectName("summarySection")
                sec_lbl.setWordWrap(True)
                db_lbl = QLabel(db_name)
                db_lbl.setObjectName("summaryDb")
                pct_lbl = QLabel(f"{confidence}% confidence")
                pct_lbl.setStyleSheet(f"color: {color}; font-weight: 600;")

                cl.addWidget(sec_lbl)
                cl.addWidget(db_lbl)
                cl.addWidget(pct_lbl)

                row_idx, col_idx = divmod(col, 3)
                grid.addWidget(card, row_idx, col_idx)

            summary_layout.addLayout(grid)
        else:
            no_rec = QLabel("No database reached a positive score for these requirements.")
            no_rec.setObjectName("placeholder")
            no_rec.setAlignment(Qt.AlignmentFlag.AlignCenter)
            summary_layout.addWidget(no_rec)

        # Final leaderboard
        if ranked:
            rank_title = QLabel("Full Ranking")
            rank_title.setObjectName("sectionTitle")
            summary_layout.addWidget(rank_title)

            for i, (db_name, score) in enumerate(ranked, 1):
                confidence = max(0, min(score, 100))
                color = _confidence_color(score)
                row_f = QFrame()
                row_f.setObjectName("rankRow")
                rl = QHBoxLayout(row_f)
                rl.setContentsMargins(10, 6, 10, 6)
                rn = QLabel(f"{i}. {db_name}")
                rn.setObjectName("rankName")
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setValue(int(round(confidence)))
                bar.setFormat(f"{confidence:.1f}%")
                bar.setFixedWidth(200)
                bar.setStyleSheet(f"""
                    QProgressBar {{
                        border: 1px solid #334155; border-radius:3px;
                        background:#1e293b; height:14px; text-align:center;
                        color:#f1f5f9; font-size:10px;
                    }}
                    QProgressBar::chunk {{ background:{color}; border-radius:2px; }}
                """)
                rl.addWidget(rn, 1)
                rl.addWidget(bar)
                summary_layout.addWidget(row_f)

        summary_layout.addStretch()
        summary_tab.setWidget(summary_widget)
        self.tabs.addTab(summary_tab, "📊  Summary")

        # ── Tab 2: Detailed Recommendations ───────────────────────────────
        detail_tab = QScrollArea()
        detail_tab.setWidgetResizable(True)
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(16, 16, 16, 16)
        detail_layout.setSpacing(12)

        if ranked:
            for rank_i, (db_name, score) in enumerate(ranked, 1):
                card = DbRecommendationCard(
                    rank_i, db_name, score,
                    engine.matched_rules.get(db_name, [])
                )
                detail_layout.addWidget(card)
        else:
            no_det = QLabel("No positive recommendations for this case.")
            no_det.setObjectName("placeholder")
            no_det.setAlignment(Qt.AlignmentFlag.AlignCenter)
            detail_layout.addWidget(no_det)

        detail_layout.addStretch()
        detail_tab.setWidget(detail_widget)
        self.tabs.addTab(detail_tab, "🔍  Detailed")

        # ── Tab 3: Rejected Alternatives ──────────────────────────────────
        rejected_tab = QScrollArea()
        rejected_tab.setWidgetResizable(True)
        rejected_widget = QWidget()
        rejected_layout = QVBoxLayout(rejected_widget)
        rejected_layout.setContentsMargins(16, 16, 16, 16)
        rejected_layout.setSpacing(8)

        if not_recommended:
            for db_name in not_recommended:
                reasons = explain_rejection(db_name, facts_dict)
                rej_frame = QFrame()
                rej_frame.setObjectName("rejCard")
                rl = QVBoxLayout(rej_frame)
                rl.setContentsMargins(12, 10, 12, 10)
                rl.setSpacing(4)
                dn = QLabel(db_name)
                dn.setObjectName("rejDbName")
                rl.addWidget(dn)
                for r in reasons:
                    rl.addWidget(QLabel(f"  • {r}"))
                rejected_layout.addWidget(rej_frame)
        else:
            all_rec = QLabel("Every known database scored positively.")
            all_rec.setObjectName("placeholder")
            all_rec.setAlignment(Qt.AlignmentFlag.AlignCenter)
            rejected_layout.addWidget(all_rec)

        rejected_layout.addStretch()
        rejected_tab.setWidget(rejected_widget)
        self.tabs.addTab(rejected_tab, "✗  Rejected")

        # ── Tab 4: Fired Rules Log ─────────────────────────────────────────
        fired_tab = QScrollArea()
        fired_tab.setWidgetResizable(True)
        fired_widget = QWidget()
        fired_layout = QVBoxLayout(fired_widget)
        fired_layout.setContentsMargins(16, 16, 16, 16)
        fired_layout.setSpacing(4)

        if engine.fired_rule_log:
            title_f = QLabel(f"{len(engine.fired_rule_log)} rules fired (in firing order):")
            title_f.setObjectName("sectionTitle")
            fired_layout.addWidget(title_f)
            for rname in engine.fired_rule_log:
                is_penalty = rname.startswith("Penalty_")
                color = "#f87171" if is_penalty else "#86efac"
                lbl = QLabel(f"  • {rname}")
                lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
                fired_layout.addWidget(lbl)
        else:
            no_rules = QLabel("No rules fired for this case.")
            no_rules.setObjectName("placeholder")
            no_rules.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fired_layout.addWidget(no_rules)

        fired_layout.addStretch()
        fired_tab.setWidget(fired_widget)
        self.tabs.addTab(fired_tab, "⚡  Fired Rules")

        # ── Tab 5: Input Facts ─────────────────────────────────────────────
        facts_tab = QScrollArea()
        facts_tab.setWidgetResizable(True)
        facts_widget = QWidget()
        facts_layout = QVBoxLayout(facts_widget)
        facts_layout.setContentsMargins(16, 16, 16, 16)
        facts_layout.setSpacing(4)

        for key, value in facts_dict.items():
            label = key.replace("_", " ").title()
            if isinstance(value, bool):
                disp = "✓  Yes" if value else "✗  No"
                color = "#86efac" if value else "#94a3b8"
            else:
                disp = str(value)
                color = "#93c5fd"
            row = QFrame()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(6, 2, 6, 2)
            k_lbl = QLabel(label)
            k_lbl.setFixedWidth(260)
            k_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            v_lbl = QLabel(disp)
            v_lbl.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
            rl.addWidget(k_lbl)
            rl.addWidget(v_lbl, 1)
            facts_layout.addWidget(row)

        facts_layout.addStretch()
        facts_tab.setWidget(facts_widget)
        self.tabs.addTab(facts_tab, "📋  Input Facts")



class InputPanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setMinimumWidth(340)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(14, 14, 14, 14)
        self._layout.setSpacing(10)
        self.setWidget(container)

        # Title
        title = QLabel("Requirements")
        title.setObjectName("panelTitle")
        self._layout.addWidget(title)

        subtitle = QLabel("Check all that apply to your project:")
        subtitle.setObjectName("panelSubtitle")
        self._layout.addWidget(subtitle)

        # Build checkbox widgets indexed by field name
        self._checkboxes = {}
        bool_lookup = {field: label for field, label in BOOL_QUESTIONNAIRE}

        for group_name, fields in BOOL_GROUPS:
            grp = QGroupBox(group_name)
            grp.setObjectName("inputGroup")
            gl = QVBoxLayout(grp)
            gl.setSpacing(4)
            for field in fields:
                cb = QCheckBox(bool_lookup[field])
                cb.setObjectName("reqCheck")
                gl.addWidget(cb)
                self._checkboxes[field] = cb
            self._layout.addWidget(grp)

        # Categorical dropdowns
        cat_grp = QGroupBox("Quantitative Context")
        cat_grp.setObjectName("inputGroup")
        cat_layout = QGridLayout(cat_grp)
        cat_layout.setSpacing(8)
        self._combos = {}

        for row, (field, label, options, default) in enumerate(CATEGORICAL_QUESTIONNAIRE):
            lbl = QLabel(label + ":")
            lbl.setObjectName("catLabel")
            combo = QComboBox()
            combo.setObjectName("catCombo")
            for opt in options:
                combo.addItem(opt)
            combo.setCurrentText(default)
            cat_layout.addWidget(lbl, row, 0)
            cat_layout.addWidget(combo, row, 1)
            self._combos[field] = combo

        self._layout.addWidget(cat_grp)
        self._layout.addStretch()

    # ── Public API ─────────────────────────────────────────────────────────

    def get_facts(self) -> dict:
        """Returns the current GUI state as a facts dict."""
        facts = {}
        for field, cb in self._checkboxes.items():
            facts[field] = cb.isChecked()
        for field, combo in self._combos.items():
            facts[field] = combo.currentText()
        return facts

    def load_facts(self, facts_dict: dict):
        """Loads a facts dict into the GUI (for demo presets)."""
        # Reset all booleans first
        for cb in self._checkboxes.values():
            cb.setChecked(False)
        # Reset all combos to default
        for field, _, _, default in CATEGORICAL_QUESTIONNAIRE:
            self._combos[field].setCurrentText(default)

        for field, value in facts_dict.items():
            if field in self._checkboxes and isinstance(value, bool):
                self._checkboxes[field].setChecked(value)
            elif field in self._combos and isinstance(value, str):
                self._combos[field].setCurrentText(value)

    def clear_all(self):
        for cb in self._checkboxes.values():
            cb.setChecked(False)
        for field, _, _, default in CATEGORICAL_QUESTIONNAIRE:
            self._combos[field].setCurrentText(default)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Expert System")
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

        self._worker = None

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ────────────────────────────────────────────────────────
        topbar = QFrame()
        topbar.setObjectName("topBar")
        topbar.setFixedHeight(64)
        tb_layout = QHBoxLayout(topbar)
        tb_layout.setContentsMargins(20, 0, 20, 0)

        app_title = QLabel("Database Expert System")
        app_title.setObjectName("appTitle")
        tb_layout.addWidget(app_title)

        subtitle_lbl = QLabel("Rule-Based Knowledge System  ·  Experta + PyQt6")
        subtitle_lbl.setObjectName("appSubtitle")
        tb_layout.addWidget(subtitle_lbl, 1)

        # Demo preset selector
        demo_label = QLabel("Load Demo:")
        demo_label.setObjectName("demoLabel")
        tb_layout.addWidget(demo_label)

        self.demo_combo = QComboBox()
        self.demo_combo.setObjectName("demoCombo")
        for name, _ in DEMO_CASES:
            self.demo_combo.addItem(name)
        self.demo_combo.setFixedWidth(240)
        tb_layout.addWidget(self.demo_combo)

        load_btn = QPushButton("Load")
        load_btn.setObjectName("loadBtn")
        load_btn.clicked.connect(self._load_demo)
        tb_layout.addWidget(load_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(self._clear)
        tb_layout.addWidget(clear_btn)

        root.addWidget(topbar)

        # ── Body: splitter ─────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setObjectName("mainSplitter")

        # Left: input panel
        left_frame = QFrame()
        left_frame.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.input_panel = InputPanel()
        left_layout.addWidget(self.input_panel)

        run_frame = QFrame()
        run_frame.setObjectName("runFrame")
        run_frame.setFixedHeight(60)
        rl = QHBoxLayout(run_frame)
        rl.setContentsMargins(14, 10, 14, 10)

        self.run_btn = QPushButton("▶  Run Analysis")
        self.run_btn.setObjectName("runBtn")
        self.run_btn.clicked.connect(self._run_analysis)
        rl.addWidget(self.run_btn)

        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("statusLabel")
        rl.addWidget(self.status_lbl)

        left_layout.addWidget(run_frame)
        splitter.addWidget(left_frame)

        # Right: results panel
        right_frame = QFrame()
        right_frame.setObjectName("rightPanel")
        rl2 = QVBoxLayout(right_frame)
        rl2.setContentsMargins(0, 0, 0, 0)

        self.results_panel = ResultsPanel()
        rl2.addWidget(self.results_panel)
        splitter.addWidget(right_frame)

        splitter.setSizes([380, 900])
        root.addWidget(splitter, 1)

        self._apply_stylesheet()

    # ── Slots ──────────────────────────────────────────────────────────────

    def _load_demo(self):
        idx = self.demo_combo.currentIndex()
        _, facts_dict = DEMO_CASES[idx]
        self.input_panel.load_facts(facts_dict)

    def _clear(self):
        self.input_panel.clear_all()

    def _run_analysis(self):
        if self._worker and self._worker.isRunning():
            return

        self.run_btn.setEnabled(False)
        self.run_btn.setText("⏳  Running…")
        self.status_lbl.setText("")

        facts_dict = self.input_panel.get_facts()
        self._worker = InferenceWorker(facts_dict)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, engine, facts_dict):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run Analysis")
        pos_count = sum(1 for v in engine.scores.values() if v > 0)
        self.status_lbl.setText(
            f"Done — {pos_count} recommendation(s), "
            f"{len(engine.fired_rule_log)} rules fired"
        )
        self.results_panel.display(engine, facts_dict)

    def _on_error(self, msg):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("▶  Run Analysis")
        QMessageBox.critical(self, "Inference Error", msg)

    # ── Stylesheet ─────────────────────────────────────────────────────────

    def _apply_stylesheet(self):
        self.setStyleSheet("""
        /* ── Global ──────────────────────────────────────────────── */
        QMainWindow, QWidget {
            background: #0f172a;
            color: #e2e8f0;
            font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
            font-size: 13px;
        }

        QScrollArea { border: none; background: transparent; }
        QScrollBar:vertical {
            background: #1e293b; width: 8px; border: none;
        }
        QScrollBar::handle:vertical {
            background: #334155; border-radius: 4px; min-height: 24px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

        /* ── Top bar ──────────────────────────────────────────────── */
        #topBar {
            background: #1e293b;
            border-bottom: 1px solid #334155;
        }
        #appTitle {
            font-size: 17px;
            font-weight: 700;
            color: #f1f5f9;
            margin-right: 10px;
        }
        #appSubtitle { color: #64748b; font-size: 12px; }
        #demoLabel   { color: #94a3b8; font-size: 12px; margin-right: 4px; }

        #demoCombo {
            background: #0f172a;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 4px 8px;
            font-size: 12px;
        }
        #demoCombo::drop-down { border: none; }
        #demoCombo QAbstractItemView {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            selection-background-color: #3b82f6;
        }

        #loadBtn {
            background: #3b82f6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 12px;
        }
        #loadBtn:hover  { background: #2563eb; }
        #loadBtn:pressed { background: #1d4ed8; }

        #clearBtn {
            background: #334155;
            color: #cbd5e1;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
        }
        #clearBtn:hover  { background: #475569; }
        #clearBtn:pressed { background: #334155; }

        /* ── Left panel ───────────────────────────────────────────── */
        #leftPanel { background: #0f172a; border-right: 1px solid #1e293b; }

        #panelTitle {
            font-size: 15px;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: 2px;
        }
        #panelSubtitle { color: #64748b; font-size: 12px; margin-bottom: 4px; }

        #inputGroup {
            color: #94a3b8;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid #1e293b;
            border-radius: 8px;
            margin-top: 4px;
            padding: 6px;
        }
        #inputGroup::title { subcontrol-position: top left; padding: 0 4px; }

        #reqCheck {
            color: #cbd5e1;
            spacing: 8px;
            font-size: 12px;
            padding: 2px 0;
        }
        #reqCheck::indicator {
            width: 15px; height: 15px;
            border: 1px solid #475569;
            border-radius: 3px;
            background: #1e293b;
        }
        #reqCheck::indicator:checked {
            background: #3b82f6;
            border-color: #3b82f6;
        }
        #reqCheck:hover { color: #f1f5f9; }

        #catLabel { color: #94a3b8; font-size: 12px; }
        #catCombo {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 5px;
            padding: 3px 8px;
            font-size: 12px;
        }
        #catCombo::drop-down { border: none; }
        #catCombo QAbstractItemView {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            selection-background-color: #3b82f6;
        }

        /* ── Run bar ──────────────────────────────────────────────── */
        #runFrame {
            background: #1e293b;
            border-top: 1px solid #334155;
        }
        #runBtn {
            background: #22c55e;
            color: #052e16;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: 700;
        }
        #runBtn:hover  { background: #16a34a; color: white; }
        #runBtn:pressed { background: #15803d; }
        #runBtn:disabled { background: #374151; color: #6b7280; }
        #statusLabel { color: #64748b; font-size: 12px; margin-left: 8px; }

        /* ── Right / results panel ───────────────────────────────── */
        #rightPanel  { background: #0f172a; }
        #placeholder {
            color: #334155;
            font-size: 18px;
            font-weight: 600;
        }

        QTabWidget::pane {
            border: none;
            background: #0f172a;
        }
        QTabBar {
            background: #1e293b;
        }
        QTabBar::tab {
            background: #1e293b;
            color: #64748b;
            padding: 10px 18px;
            border: none;
            font-size: 12px;
            font-weight: 600;
        }
        QTabBar::tab:selected {
            color: #f1f5f9;
            border-bottom: 2px solid #3b82f6;
            background: #0f172a;
        }
        QTabBar::tab:hover:!selected { color: #94a3b8; }

        /* ── Result cards ─────────────────────────────────────────── */
        #dbCard {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
        }

        #rankLabel {
            font-size: 20px;
            font-weight: 700;
            color: #475569;
            min-width: 36px;
        }
        #dbNameLabel {
            font-size: 16px;
            font-weight: 700;
            color: #f1f5f9;
        }
        #scoreLabel { color: #64748b; font-size: 12px; }

        #toggleBtn {
            background: transparent;
            border: 1px solid #334155;
            border-radius: 5px;
            color: #64748b;
            padding: 4px 10px;
            font-size: 11px;
            text-align: left;
        }
        #toggleBtn:hover { border-color: #3b82f6; color: #93c5fd; }
        #toggleBtn:checked { color: #93c5fd; border-color: #3b82f6; }

        #ruleName   { color: #93c5fd; font-size: 11px; font-weight: 600; }
        #ruleReason { color: #64748b; font-size: 11px; }
        #ruleSep    { color: #1e293b; }

        /* ── Summary cards ───────────────────────────────────────── */
        #summaryCard {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
        }
        #summarySection { color: #64748b; font-size: 11px; font-weight: 600; }
        #summaryDb      { color: #f1f5f9; font-size: 14px; font-weight: 700; }

        /* ── Rank rows ────────────────────────────────────────────── */
        #rankRow { background: #1e293b; border-radius: 6px; }
        #rankName { color: #cbd5e1; font-size: 13px; }

        /* ── Section titles ──────────────────────────────────────── */
        #sectionTitle {
            font-size: 14px;
            font-weight: 700;
            color: #94a3b8;
            margin-top: 8px;
        }

        /* ── Rejected cards ──────────────────────────────────────── */
        #rejCard {
            background: #1a0a0a;
            border: 1px solid #7f1d1d;
            border-radius: 8px;
        }
        #rejDbName { color: #fca5a5; font-weight: 700; font-size: 13px; }

        /* ── Splitter handle ─────────────────────────────────────── */
        #mainSplitter::handle { background: #334155; }
        """)



def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Database Expert System")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


__name__ == "__main__" and main()
