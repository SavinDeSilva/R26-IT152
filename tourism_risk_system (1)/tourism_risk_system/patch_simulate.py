import io

path = "scripts/simulate_crowd_data.py"
with io.open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if line.strip().startswith("SITES = ["):
        start_idx = i
    if line.strip().startswith("HIGH_IMPACT_DATES = ["):
        end_idx = i
        break

if start_idx is None or end_idx is None:
    raise SystemExit(f"Could not find boundaries: start_idx={start_idx}, end_idx={end_idx}")

new_block = """PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES_CSV_PATH = os.path.join(PROJECT_ROOT, "data", "tourist_sites.csv")

def load_sites(csv_path=SITES_CSV_PATH):
    sites_df = pd.read_csv(csv_path)
    required_cols = {"site_id", "site_name", "annual_visitors_2024", "capacity_per_day", "category"}
    missing = required_cols - set(sites_df.columns)
    if missing:
        raise ValueError(f"tourist_sites.csv is missing required columns: {missing}")
    sites = []
    for _, row in sites_df.iterrows():
        sites.append({
            "site_id": int(row["site_id"]),
            "site_name": row["site_name"],
            "annual_visitors": row["annual_visitors_2024"],
            "capacity_per_day": row["capacity_per_day"],
            "category": row["category"],
        })
    return sites

SITES = load_sites()

"""

new_lines = lines[:start_idx] + [new_block] + lines[end_idx:]

with io.open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print(f"SITES block replaced: lines {start_idx+1}-{end_idx} -> dynamic loader")
print(f"New total line count: {len(new_lines)}")

with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ('print("Generating simulated crowd data for 50 sites...")',
     'print(f"Generating simulated crowd data for {len(SITES)} sites...")'),
    ('os.makedirs("data", exist_ok=True)',
     'os.makedirs(os.path.join(PROJECT_ROOT, "data"), exist_ok=True)'),
    ('df.to_csv("data/simulated_crowd_data.csv", index=False)',
     'df.to_csv(os.path.join(PROJECT_ROOT, "data", "simulated_crowd_data.csv"), index=False)'),
]

for old, new in replacements:
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly 1 occurrence of {old!r}, found {count}")
    content = content.replace(old, new)

with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Applied 3 follow-on replacements successfully.")
