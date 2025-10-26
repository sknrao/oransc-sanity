import re
import json

input_file = "scan-summary.txt"
output_file = "high_vulns.json"

result = {}

with open(input_file, "r") as f:
    current_repo = None
    in_vuln_section = False
    for line in f:
        line = line.rstrip()
        if not line:
            continue

        # detect repo name lines (no indentation, ends with ':')
        if not line.startswith(" ") and line.endswith(":"):
            current_repo = line[:-1].replace("/", "_").lower()
            in_vuln_section = False
            continue

        # check if entering vulnerabilities section
        if "Vulnerabilities:" in line:
            in_vuln_section = True
            continue

        # parse only lines in vulnerabilities section
        if in_vuln_section and "[HIGH]" in line:
            match = re.match(r"\s*\[HIGH\]\s*(\w+):\s*(.*)", line)
            if match:
                tool, description = match.groups()
                key = f"{current_repo}_high_snyk"
                if key not in result:
                    result[key] = []
                result[key].append({
                    "severity": "High",
                    "package": tool if tool else "",
                    "cve": "-",
                    "description": description if description else "",
                    "installedVersion": "-",
                    "fixedVersion": "-"
                })

# write JSON output
with open(output_file, "w") as f:
    json.dump(result, f, indent=2)

print(f"HIGH vulnerabilities written to {output_file}")
