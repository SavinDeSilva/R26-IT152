import io

path = "scripts/train_model.py"
with io.open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove the old DATA_PATH line entirely (it currently sits before PROJECT_ROOT exists)
old_datapath_line = 'DATA_PATH = r"C:\\Users\\ASUS\\OneDrive - Sri Lanka Institute of Information Technology\\Desktop\\tourism_risk_system\\data\\master_dataset.csv"\n'
count = content.count(old_datapath_line)
if count != 1:
    raise SystemExit(f"Expected exactly 1 occurrence of DATA_PATH line, found {count}")
content = content.replace(old_datapath_line, "")

# 2. Insert the new DATA_PATH line right after PROJECT_ROOT is defined
anchor = 'PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n'
count_anchor = content.count(anchor)
if count_anchor != 1:
    raise SystemExit(f"Expected exactly 1 occurrence of PROJECT_ROOT line, found {count_anchor}")
content = content.replace(
    anchor,
    anchor + 'DATA_PATH = os.path.join(PROJECT_ROOT, "data", "master_dataset.csv")\n'
)

# 3. Replace the seeded-shuffle holdout block with the fixed 10-site list
old_holdout = """    all_site_ids = df['site_id'].unique()
    rng = np.random.RandomState(42)
    rng.shuffle(all_site_ids)
    n_holdout = max(1, int(len(all_site_ids) * 0.2))
    holdout_sites = set(all_site_ids[:n_holdout])"""
count2 = content.count(old_holdout)
if count2 != 1:
    raise SystemExit(f"Expected exactly 1 occurrence of holdout block, found {count2}")

new_holdout = """    HOLDOUT_SITE_NAMES = [
        "Bentota Beach", "Bundala National Park", "Colombo Lotus Tower",
        "Kalpitiya Beach", "Kande Viharaya", "Kandy Lake",
        "Minneriya National Park", "Pasikuda Beach", "Tangalle Beach",
        "Wilpattu National Park"
    ]
    holdout_sites = set(df.loc[df['site_name'].isin(HOLDOUT_SITE_NAMES), 'site_id'].unique())
    missing_holdout = set(HOLDOUT_SITE_NAMES) - set(
        df.loc[df['site_id'].isin(holdout_sites), 'site_name'].unique()
    )
    if missing_holdout:
        raise ValueError(f"Fixed holdout sites not found in dataset: {missing_holdout}")"""
content = content.replace(old_holdout, new_holdout)

with io.open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("DATA_PATH moved after PROJECT_ROOT and anchored.")
print("Holdout block replaced with fixed 10-site list.")
