import json

with open("manifest.json", "r") as f:
    data = json.load(f)

v = data["version"].split(".")
v[-1] = str(int(v[-1]) + 1)
new_version = ".".join(v)

data["version"] = new_version

with open("manifest.json", "w") as f:
    json.dump(data, f, indent=2)

print("Yeni version:", new_version)
