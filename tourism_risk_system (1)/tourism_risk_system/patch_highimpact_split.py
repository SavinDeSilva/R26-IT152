path = "app.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def replace_once(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise ValueError(f"[{label}] expected exactly 1 match, found {count}")
    return content.replace(old, new)

# 1. Split the list definition and add the site-aware helper
old_list = """HIGH_IMPACT_DATES = [
    "2026-01-14","2026-02-04",
    "2026-04-13","2026-04-14",
    "2026-05-22","2026-05-23",
    "2026-06-20",
    "2026-08-27",
    "2026-10-20",
    "2026-12-25","2026-12-31",
]"""

new_list = """NATIONAL_HOLIDAY_DATES = [
    "2026-01-14","2026-02-04",
    "2026-04-13","2026-04-14",
    "2026-05-22","2026-05-23",
    "2026-06-20",
    "2026-10-20",
    "2026-12-25","2026-12-31",
]

# Kandy Esala Perahera 2026: Kumbal Perahera Aug 18-22, Randoli Perahera
# Aug 23-27, Diya Kepeema / closing day procession Aug 28. Kandy-specific --
# only elevates crowding at the Temple of the Tooth, not nationwide.
KANDY_ESALA_PERAHERA_DATES = [
    "2026-08-18","2026-08-19","2026-08-20","2026-08-21","2026-08-22",
    "2026-08-23","2026-08-24","2026-08-25","2026-08-26","2026-08-27","2026-08-28",
]

KANDY_TEMPLE_SITE_NAME = "Temple of the Tooth Kandy"

def is_high_impact_date(date_str, site):
    \"\"\"National holidays apply to every site; Esala Perahera only
    elevates crowding at the Temple of the Tooth in Kandy.\"\"\"
    if date_str in NATIONAL_HOLIDAY_DATES:
        return True
    if site.get("name") == KANDY_TEMPLE_SITE_NAME and date_str in KANDY_ESALA_PERAHERA_DATES:
        return True
    return False"""

content = replace_once(content, old_list, new_list, "list_definition")

# 2. build_features() call site
old_a = """    temp, rainfall = get_monthly_weather(month)
    is_holiday = 1 if date_str in HIGH_IMPACT_DATES else 0
    is_weekend = 1 if date.weekday() >= 5 else 0"""
new_a = """    temp, rainfall = get_monthly_weather(month)
    is_holiday = 1 if is_high_impact_date(date_str, site) else 0
    is_weekend = 1 if date.weekday() >= 5 else 0"""
content = replace_once(content, old_a, new_a, "build_features_call_site")

# 3. fallback_prediction() call site
old_b = """        base_score += 0.1
    if date_str in HIGH_IMPACT_DATES:
        base_score += 0.2"""
new_b = """        base_score += 0.1
    if is_high_impact_date(date_str, site):
        base_score += 0.2"""
content = replace_once(content, old_b, new_b, "fallback_prediction_call_site")

# 4. predict() endpoint call site
old_c = """        # anyone reading the response) can tell the difference.
        is_holiday = 1 if date_str in HIGH_IMPACT_DATES else 0
        is_weekend = 1 if datetime.strptime(date_str, "%Y-%m-%d").weekday() >= 5 else 0"""
new_c = """        # anyone reading the response) can tell the difference.
        is_holiday = 1 if is_high_impact_date(date_str, site) else 0
        is_weekend = 1 if datetime.strptime(date_str, "%Y-%m-%d").weekday() >= 5 else 0"""
content = replace_once(content, old_c, new_c, "predict_endpoint_call_site")

# 5. forecast() endpoint call site
old_d = """            crowd_score, risk_level = fallback_prediction(site, target_date_str)
            is_holiday = 1 if target_date_str in HIGH_IMPACT_DATES else 0
            is_weekend = 1 if target_date.weekday() >= 5 else 0"""
new_d = """            crowd_score, risk_level = fallback_prediction(site, target_date_str)
            is_holiday = 1 if is_high_impact_date(target_date_str, site) else 0
            is_weekend = 1 if target_date.weekday() >= 5 else 0"""
content = replace_once(content, old_d, new_d, "forecast_endpoint_call_site")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("All 5 patches applied OK")
