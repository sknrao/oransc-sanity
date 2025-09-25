import os
import pandas as pd
import matplotlib.pyplot as plt

base_dir = "active-repos"

files = [f for f in os.listdir(base_dir) if f.endswith("_cve_report.csv")]

severity_data = []
cve_data = []

for f in files:
    repo = f.replace("_cve_report.csv", "")
    path = os.path.join(base_dir, f)

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError:
        continue

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if "severity" not in df.columns:
        continue

    # collect severity counts
    severity_counts = df["severity"].value_counts().to_dict()
    severity_counts["repo_name"] = repo
    severity_data.append(severity_counts)

    # collect cve-package mapping
    if "cve_id" in df.columns and "package" in df.columns:
        for _, row in df.iterrows():
            cve_data.append({
                "repo_name": repo,
                "package": row["package"],
                "cve": row["cve_id"],
                "severity": row["severity"],
                "installed_version": row.get("installed_version", ""),
                "fixed_version": row.get("fixed_version", "")
            })

severity_df = pd.DataFrame(severity_data).fillna(0).set_index("repo_name")
cve_df = pd.DataFrame(cve_data)

# markdown table
with open("severity_report.md", "w") as f:
    f.write("# Vulnerability Report by Repository\n\n")
    f.write(severity_df.to_markdown())
    f.write("\n\n")

# charts
if not severity_df.empty:
    severity_df.plot(kind="bar", stacked=True, figsize=(10,6))
    plt.title("Vulnerabilities by Repo and Severity")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("vulns_by_repo.png")
    plt.close()

    severity_df.sum(axis=1).sort_values(ascending=False).plot(kind="bar", figsize=(8,5))
    plt.title("Total Vulnerabilities by Repo")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("vulns_totals.png")
    plt.close()

    severity_df.sum().plot(kind="pie", autopct="%1.1f%%", figsize=(6,6))
    plt.title("Overall Severity Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("severity_distribution.png")
    plt.close()

    print("charts saved")

# cve-package csv
if not cve_df.empty:
    cve_df.to_csv("cve_package_mapping.csv", index=False)
    print("cve-package csv saved")

    critical_df = cve_df[cve_df["severity"].str.lower() == "critical"]
    high_df = cve_df[cve_df["severity"].str.lower() == "high"]

    with open("severity_report.md", "a") as f:
        if not critical_df.empty:
            critical_df = critical_df.reset_index(drop=True)
            critical_df.index = critical_df.index + 1
            critical_df.index.name = "S.No"

            f.write("## Critical CVEs\n\n")
            f.write(critical_df[["repo_name", "package", "cve", "installed_version", "fixed_version", "severity"]]
                    .to_markdown(index=True))
            f.write("\n\n")

        if not high_df.empty:
            high_df = high_df.reset_index(drop=True)
            high_df.index = high_df.index + 1
            high_df.index.name = "S.No"

            f.write("## High CVEs\n\n")
            f.write(high_df[["repo_name", "package", "cve", "installed_version", "fixed_version", "severity"]]
                    .to_markdown(index=True))
            f.write("\n\n")

        # charts at end
        f.write("## Charts\n\n")
        f.write("![Vulnerabilities by Repo](vulns_by_repo.png)\n\n")
        f.write("![Total Vulnerabilities](vulns_totals.png)\n\n")
        f.write("![Severity Distribution](severity_distribution.png)\n\n")

else:
    print("no cve-package data")

print("md report saved")
