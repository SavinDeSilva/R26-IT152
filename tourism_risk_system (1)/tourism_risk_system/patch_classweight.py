path = "scripts/train_model.py"
old = "        return RandomForestClassifier(**best_params, random_state=42, n_jobs=-1)"
new = "        return RandomForestClassifier(**best_params, random_state=42, n_jobs=-1, class_weight=\"balanced\")"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

count = content.count(old)
if count != 1:
    raise ValueError(f"Expected exactly 1 match, found {count}")

content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched OK")
