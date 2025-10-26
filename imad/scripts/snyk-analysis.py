import re
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from collections import defaultdict
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

def parse_snyk_report(filename):
    """Parse Snyk scan summary file"""
    projects = {}
    current_project = None
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Match project header
        if line and not line.startswith('[') and ':' in line and 'Critical' in lines[lines.index(line + '\n') + 1] if line + '\n' in lines else False:
            current_project = line.rstrip(':')
            projects[current_project] = {
                'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0,
                'vulnerabilities': []
            }
        
        # Match severity counts
        elif 'Critical:' in line and 'High:' in line:
            match = re.search(r'Critical:\s*(\d+).*High:\s*(\d+).*Medium:\s*(\d+).*Low:\s*(\d+)', line)
            if match and current_project:
                projects[current_project]['Critical'] = int(match.group(1))
                projects[current_project]['High'] = int(match.group(2))
                projects[current_project]['Medium'] = int(match.group(3))
                projects[current_project]['Low'] = int(match.group(4))
        
        # Match vulnerability entries
        elif line.startswith('[') and current_project:
            vuln_match = re.match(r'\[(CRITICAL|HIGH|MEDIUM|LOW)\]\s+(\w+):\s+(.+)', line)
            if vuln_match:
                severity, pkg_type, vuln_type = vuln_match.groups()
                projects[current_project]['vulnerabilities'].append({
                    'severity': severity,
                    'package_type': pkg_type,
                    'type': vuln_type
                })
    
    return projects

def high_level_analysis(projects):
    """Generate high-level statistics"""
    total_vulns = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    total_projects = len(projects)
    affected_projects = 0
    
    for proj, data in projects.items():
        if sum([data['Critical'], data['High'], data['Medium'], data['Low']]) > 0:
            affected_projects += 1
        for severity in total_vulns:
            total_vulns[severity] += data[severity]
    
    print("=" * 80)
    print("HIGH-LEVEL ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Projects Scanned: {total_projects}")
    print(f"Projects with Vulnerabilities: {affected_projects}")
    print(f"Clean Projects: {total_projects - affected_projects}")
    print(f"\nTotal Vulnerabilities by Severity:")
    print(f"  Critical: {total_vulns['Critical']}")
    print(f"  High: {total_vulns['High']}")
    print(f"  Medium: {total_vulns['Medium']}")
    print(f"  Low: {total_vulns['Low']}")
    print(f"  TOTAL: {sum(total_vulns.values())}")
    
    return total_vulns, affected_projects

def detailed_analysis(projects):
    """Generate detailed analysis by project and package type"""
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS")
    print("=" * 80)
    
    # Top 10 most vulnerable projects
    project_totals = [(proj, sum([data['Critical'], data['High'], data['Medium'], data['Low']])) 
                      for proj, data in projects.items()]
    project_totals.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop 10 Most Vulnerable Projects:")
    for i, (proj, total) in enumerate(project_totals[:10], 1):
        data = projects[proj]
        print(f"{i:2}. {proj:50} - Total: {total:4} (C:{data['Critical']:2} H:{data['High']:3} M:{data['Medium']:3} L:{data['Low']:2})")
    
    # Package type analysis
    pkg_stats = defaultdict(lambda: {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0})
    vuln_types = defaultdict(int)
    
    for proj, data in projects.items():
        for vuln in data['vulnerabilities']:
            pkg_stats[vuln['package_type']][vuln['severity']] += 1
            vuln_types[vuln['type']] += 1
    
    print("\nVulnerabilities by Package Type:")
    for pkg, stats in sorted(pkg_stats.items(), key=lambda x: sum(x[1].values()), reverse=True):
        total = sum(stats.values())
        print(f"  {pkg:15} - Total: {total:4} (C:{stats['CRITICAL']:2} H:{stats['HIGH']:3} M:{stats['MEDIUM']:3} L:{stats['LOW']:2})")
    
    print("\nTop 10 Most Common Vulnerability Types:")
    for i, (vtype, count) in enumerate(sorted(vuln_types.items(), key=lambda x: x[1], reverse=True)[:10], 1):
        print(f"{i:2}. {vtype:60} - {count:4}")
    
    return pkg_stats, vuln_types, project_totals

def create_visualizations(projects, total_vulns, pkg_stats, vuln_types, project_totals):
    """Create comprehensive visualizations"""
    
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Overall Severity Distribution (Pie Chart)
    ax1 = plt.subplot(2, 3, 1)
    colors = ['#d32f2f', '#f57c00', '#fbc02d', '#689f38']
    sizes = [total_vulns['Critical'], total_vulns['High'], total_vulns['Medium'], total_vulns['Low']]
    labels = [f"Critical\n{total_vulns['Critical']}", f"High\n{total_vulns['High']}", 
              f"Medium\n{total_vulns['Medium']}", f"Low\n{total_vulns['Low']}"]
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Overall Vulnerability Distribution by Severity', fontsize=14, fontweight='bold')
    
    # 2. Top 15 Vulnerable Projects (Horizontal Bar)
    ax2 = plt.subplot(2, 3, 2)
    top_projects = project_totals[:15]
    proj_names = [p[0].split('/')[-1] if len(p[0]) > 30 else p[0] for p in top_projects]
    proj_counts = [p[1] for p in top_projects]
    y_pos = np.arange(len(proj_names))
    bars = ax2.barh(y_pos, proj_counts, color='#e53935')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(proj_names, fontsize=9)
    ax2.invert_yaxis()
    ax2.set_xlabel('Number of Vulnerabilities')
    ax2.set_title('Top 15 Most Vulnerable Projects', fontsize=14, fontweight='bold')
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax2.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}', 
                ha='left', va='center', fontsize=8)
    
    # 3. Package Type Breakdown (Stacked Bar)
    ax3 = plt.subplot(2, 3, 3)
    pkg_names = list(pkg_stats.keys())
    critical_vals = [pkg_stats[p]['CRITICAL'] for p in pkg_names]
    high_vals = [pkg_stats[p]['HIGH'] for p in pkg_names]
    medium_vals = [pkg_stats[p]['MEDIUM'] for p in pkg_names]
    low_vals = [pkg_stats[p]['LOW'] for p in pkg_names]
    
    x_pos = np.arange(len(pkg_names))
    ax3.bar(x_pos, critical_vals, label='Critical', color='#d32f2f')
    ax3.bar(x_pos, high_vals, bottom=critical_vals, label='High', color='#f57c00')
    ax3.bar(x_pos, medium_vals, bottom=np.array(critical_vals) + np.array(high_vals), 
            label='Medium', color='#fbc02d')
    ax3.bar(x_pos, low_vals, bottom=np.array(critical_vals) + np.array(high_vals) + np.array(medium_vals), 
            label='Low', color='#689f38')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(pkg_names, rotation=45, ha='right')
    ax3.set_ylabel('Number of Vulnerabilities')
    ax3.set_title('Vulnerabilities by Package Type', fontsize=14, fontweight='bold')
    ax3.legend()
    
    # 4. Severity Heatmap by Top Projects
    ax4 = plt.subplot(2, 3, 4)
    top_10_projects = project_totals[:10]
    heatmap_data = []
    for proj, _ in top_10_projects:
        data = projects[proj]
        heatmap_data.append([data['Critical'], data['High'], data['Medium'], data['Low']])
    
    proj_labels = [p[0].split('/')[-1] if len(p[0]) > 25 else p[0] for p, _ in top_10_projects]
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='Reds', 
                xticklabels=['Critical', 'High', 'Medium', 'Low'],
                yticklabels=proj_labels, ax=ax4, cbar_kws={'label': 'Count'})
    ax4.set_title('Severity Heatmap - Top 10 Projects', fontsize=14, fontweight='bold')
    
    # 5. Top Vulnerability Types (Horizontal Bar)
    ax5 = plt.subplot(2, 3, 5)
    top_vulns = sorted(vuln_types.items(), key=lambda x: x[1], reverse=True)[:12]
    vuln_names = [v[0][:50] for v in top_vulns]
    vuln_counts = [v[1] for v in top_vulns]
    y_pos = np.arange(len(vuln_names))
    bars = ax5.barh(y_pos, vuln_counts, color='#ff6f00')
    ax5.set_yticks(y_pos)
    ax5.set_yticklabels(vuln_names, fontsize=8)
    ax5.invert_yaxis()
    ax5.set_xlabel('Count')
    ax5.set_title('Top 12 Vulnerability Types', fontsize=14, fontweight='bold')
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax5.text(width, bar.get_y() + bar.get_height()/2, f' {int(width)}', 
                ha='left', va='center', fontsize=8)
    
    # 6. Risk Distribution (Projects by Total Vulnerabilities)
    ax6 = plt.subplot(2, 3, 6)
    risk_categories = {
        'Critical Risk (100+)': 0,
        'High Risk (50-99)': 0,
        'Medium Risk (10-49)': 0,
        'Low Risk (1-9)': 0,
        'No Risk (0)': 0
    }
    
    for proj, total in project_totals:
        if total == 0:
            risk_categories['No Risk (0)'] += 1
        elif total >= 100:
            risk_categories['Critical Risk (100+)'] += 1
        elif total >= 50:
            risk_categories['High Risk (50-99)'] += 1
        elif total >= 10:
            risk_categories['Medium Risk (10-49)'] += 1
        else:
            risk_categories['Low Risk (1-9)'] += 1
    
    categories = list(risk_categories.keys())
    values = list(risk_categories.values())
    colors_risk = ['#b71c1c', '#d32f2f', '#f57c00', '#fbc02d', '#689f38']
    bars = ax6.bar(categories, values, color=colors_risk)
    ax6.set_ylabel('Number of Projects')
    ax6.set_title('Project Risk Distribution', fontsize=14, fontweight='bold')
    ax6.tick_params(axis='x', rotation=45)
    for bar in bars:
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('snyk_vulnerability_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✓ Visualizations saved as 'snyk_vulnerability_analysis.png'")
    plt.show()

def generate_csv_reports(projects, project_totals):
    """Generate CSV reports for further analysis"""
    
    # Project summary CSV
    summary_data = []
    for proj, total in project_totals:
        data = projects[proj]
        summary_data.append({
            'Project': proj,
            'Critical': data['Critical'],
            'High': data['High'],
            'Medium': data['Medium'],
            'Low': data['Low'],
            'Total': total
        })
    
    df_summary = pd.DataFrame(summary_data)
    df_summary.to_csv('project_vulnerability_summary.csv', index=False)
    print("✓ Project summary saved as 'project_vulnerability_summary.csv'")
    
    # Detailed vulnerabilities CSV
    detailed_data = []
    for proj, data in projects.items():
        for vuln in data['vulnerabilities']:
            detailed_data.append({
                'Project': proj,
                'Severity': vuln['severity'],
                'Package_Type': vuln['package_type'],
                'Vulnerability_Type': vuln['type']
            })
    
    df_detailed = pd.DataFrame(detailed_data)
    df_detailed.to_csv('detailed_vulnerabilities.csv', index=False)
    print("✓ Detailed vulnerabilities saved as 'detailed_vulnerabilities.csv'")

# Main execution
if __name__ == "__main__":
    print("Starting Snyk Vulnerability Analysis...")
    print("=" * 80)
    
    # Parse the report
    projects = parse_snyk_report('scan-summary.txt')
    
    # High-level analysis
    total_vulns, affected_projects = high_level_analysis(projects)
    
    # Detailed analysis
    pkg_stats, vuln_types, project_totals = detailed_analysis(projects)
    
    # Create visualizations
    create_visualizations(projects, total_vulns, pkg_stats, vuln_types, project_totals)
    
    # Generate CSV reports
    generate_csv_reports(projects, project_totals)
    
    print("\n" + "=" * 80)
    print("Analysis complete! Check the generated files:")
    print("  - snyk_vulnerability_analysis.png")
    print("  - project_vulnerability_summary.csv")
    print("  - detailed_vulnerabilities.csv")
    print("=" * 80)