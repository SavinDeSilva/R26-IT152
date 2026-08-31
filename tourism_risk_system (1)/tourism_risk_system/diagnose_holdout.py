import pandas as pd

df = pd.read_csv("data/master_dataset.csv")
holdout_names = ["Bentota Beach", "Bundala National Park", "Colombo Lotus Tower",
                  "Kalpitiya Beach", "Kande Viharaya", "Kandy Lake",
                  "Minneriya National Park", "Pasikuda Beach", "Tangalle Beach",
                  "Wilpattu National Park"]
holdout_df = df[df["site_name"].isin(holdout_names)]
print("Holdout rows:", len(holdout_df))
print("\nrisk_level distribution within holdout set:")
print(holdout_df["risk_level"].value_counts())
print("\nrisk_level distribution PER SITE within holdout set:")
print(holdout_df.groupby("site_name")["risk_level"].value_counts().unstack(fill_value=0))

sites = pd.read_csv("data/tourist_sites.csv")
print("\nCurrent tourist_sites.csv values for these 10 sites:")
print(sites[sites["site_name"].isin(holdout_names)][["site_name","annual_visitors_2024","capacity_per_day"]].to_string(index=False))
