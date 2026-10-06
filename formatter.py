

from catalog import ALL_DATABASES, DB_TO_CATEGORY, CATEGORY_TO_SECTION

LINE = "=" * 78
THIN_LINE = "-" * 78


def _run(iterable):
   
    import collections
    collections.deque(iterable, maxlen=0)


def _pick(condition, value_if_true, value_if_false):
  
    return {True: value_if_true, False: value_if_false}[bool(condition)]()


def print_header(title):
    print("\n" + LINE)
    print(title.center(78))
    print(LINE)


def print_input_facts(facts_dict):
  
    print_header("INPUT FACTS")

    def _print_fact(item):
        key, value = item
        label = key.replace("_", " ").title()
        display = _pick(
            isinstance(value, bool),
            lambda: _pick(value, lambda: "Yes", lambda: "No"),
            lambda: str(value),
        )
        print(f"  {label:<35} : {display}")

    _run(map(_print_fact, facts_dict.items()))


def print_fired_rules(fired_rule_log):

    print_header("TRIGGERED RULES")
    _pick(
        fired_rule_log,
        lambda: _run(map(lambda name: print(f"  - {name}"), fired_rule_log)),
        lambda: print("  (no rules fired)"),
    )


def _confidence_percent(score):
  
    return max(0, min(score, 100))


def _print_matched_rule(entry):
  
    rule_name, rule_score, reason = entry
    is_penalty = rule_name.startswith("Penalty_") or rule_name.startswith("Ctx_")
    prefix = _pick(
        rule_name.startswith("Penalty_"),
        lambda: "−",   
        lambda: "+",   
    )
    display_name = (
        rule_name
        .replace("Rule_", "")
        .replace("Penalty_", "[PENALTY] ")
        .replace("Ctx_", "[CTX] ")
        .replace("_", " ")
    )
    score_str = _pick(
        rule_score < 0,
        lambda: f"{rule_score:.2f}",  
        lambda: f"+{rule_score:.2f}",  
    )
    print(f"      {prefix} {score_str:<7} {display_name}")
    print(f"            -> {reason}")


def _print_one_ranked(matched_rules, entry):
    rank, (db_name, total_score) = entry
    confidence = _confidence_percent(total_score)
    print(THIN_LINE)
    print(f"#{rank}  {db_name}")
    print(f"    CF Score: {total_score:.1f}%   |   Confidence: {int(confidence)}%")
    print("    Matched Rules:")
    _run(map(_print_matched_rule, matched_rules[db_name]))


def print_ranked_recommendations(scores, matched_rules):

    print_header("RANKED RECOMMENDATIONS (DETAILED)")

    positive_scores = {k: v for k, v in scores.items() if v > 0}
    ranked = sorted(positive_scores.items(), key=lambda item: item[1], reverse=True)

    _pick(
        ranked,
        lambda: (
            _run(map(
                lambda entry: _print_one_ranked(matched_rules, entry),
                enumerate(ranked, start=1),
            )),
            print(THIN_LINE),
        ),
        lambda: print("  No database reached a positive score for this case."),
    )


def _print_rejected_one(rejection_explainer, facts_dict, db_name):
    reasons = rejection_explainer(db_name, facts_dict)
    print(THIN_LINE)
    print(f"{db_name}")
    print("Not Recommended because:")
    _run(map(lambda reason: print(f"  - {reason}"), reasons))


def print_rejected_alternatives(scores, facts_dict, rejection_explainer):

    print_header("REJECTED ALTERNATIVES")

    not_recommended = list(filter(lambda db: scores.get(db, 0) <= 0, ALL_DATABASES))

    _pick(
        not_recommended,
        lambda: (
            _run(map(
                lambda db_name: _print_rejected_one(
                    rejection_explainer, facts_dict, db_name
                ),
                not_recommended,
            )),
            print(THIN_LINE),
        ),
        lambda: print("  Every known database received at least a partial score."),
    )


def _better_of(current_best, db_name, score):

    candidates = [current_best or (db_name, -1), (db_name, score)]
    return max(candidates, key=lambda pair: pair[1])


def _fold_into_category(by_category, item):
    db_name, score = item
    category = DB_TO_CATEGORY.get(db_name, "Other")
    by_category[category] = _better_of(by_category.get(category), db_name, score)
    return by_category


def _print_category_section(entry):
    category, (db_name, score) = entry
    section_label = CATEGORY_TO_SECTION.get(category, category)
    print(f"{section_label}:")
    print(f"  {db_name}  ({_confidence_percent(score)}% confidence)")
    print()


def print_categorized_recommendations(scores):

    print_header("CATEGORIZED RECOMMENDATIONS")

    import functools
    positive_scores = {k: v for k, v in scores.items() if v > 0}
    by_category = functools.reduce(_fold_into_category, positive_scores.items(), {})
    sections_sorted = sorted(by_category.items(), key=lambda kv: kv[1][1], reverse=True)

    _pick(
        positive_scores,
        lambda: _run(map(_print_category_section, sections_sorted)),
        lambda: print("  No category has a recommended database for this case."),
    )


def _print_final_rank_line(max_name_len, entry):
    rank, (db_name, score) = entry
    confidence = _confidence_percent(score)
    dots = "." * (max_name_len - len(db_name) + 8)
    print(f"{rank}. {db_name} {dots} {int(confidence)}%")


def print_final_ranking(scores):
 
    print_header("FINAL DATABASE RANKING")

    ranked = sorted(
        ((k, v) for k, v in scores.items() if v > 0),
        key=lambda item: item[1],
        reverse=True,
    )
    max_name_len = max(map(lambda pair: len(pair[0]), ranked), default=0)

    _pick(
        ranked,
        lambda: (
            _run(map(
                lambda entry: _print_final_rank_line(max_name_len, entry),
                enumerate(ranked, start=1),
            )),
            print(LINE),
        ),
        lambda: print("  (no recommendations to rank)"),
    )
