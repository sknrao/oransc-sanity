import os
import requests
import json
import re
from datetime import datetime
from collections import defaultdict

# Try to get token from environment variable first, then from file
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    try:
        with open("GITHUB_TOKEN", "r") as f:
            content = f.read().strip()
            if content.startswith("export GITHUB_TOKEN="):
                TOKEN = content.split("=", 1)[1]
            elif content:  # If file just contains the token
                TOKEN = content
    except FileNotFoundError:
        pass

# Debug removed for clean output
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

repos = [
    "o-ran-sc/oam-tr069-adapter",
    "o-ran-sc/aiml-fw-aimlfw-dep",
    "o-ran-sc/aiml-fw-athp-pipeline-components",
    "o-ran-sc/aiml-fw-awmf-modelmgmtservice",
    "o-ran-sc/aiml-fw-aihp-ips-kserve-adapter",
    "o-ran-sc/ci-management",
    "o-ran-sc/com-golog",
    "o-ran-sc/com-log",
    "o-ran-sc/doc",
    "o-ran-sc/it-dep",
    "o-ran-sc/it-test",
    "o-ran-sc/it-tifg",
    "o-ran-sc/nonrtric",
    "o-ran-sc/nonrtric-plt-a1policymanagementservice",
    "o-ran-sc/nonrtric-plt-dmaapadapter",
    "o-ran-sc/nonrtric-plt-dmaapmediatorproducer",
    "o-ran-sc/nonrtric-plt-helmmanager",
    "o-ran-sc/nonrtric-plt-informationcoordinatorservice",
    "o-ran-sc/nonrtric-plt-ranpm",
    "o-ran-sc/nonrtric-plt-rappcatalogue",
    "o-ran-sc/nonrtric-plt-rappmanager",
    "o-ran-sc/nonrtric-plt-sme",
    "o-ran-sc/nonrtric-rapp-healthcheck",
    "o-ran-sc/nonrtric-rapp-orufhrecovery",
    "o-ran-sc/nonrtric-rapp-ransliceassurance",
    "o-ran-sc/o-du-l2",
    "o-ran-sc/o-du-phy",
    "o-ran-sc/oam-oam-controller",
    "o-ran-sc/portal-nonrtric-controlpanel",
    "o-ran-sc/pti-o2",
    "o-ran-sc/pti-rtp",
    "o-ran-sc/ric-app-ad",
    "o-ran-sc/ric-app-ad-cell",
    "o-ran-sc/ric-app-bouncer",
    "o-ran-sc/ric-app-hw-rust",
    "o-ran-sc/ric-app-kpimon-go",
    "o-ran-sc/ric-app-lp",
    "o-ran-sc/ric-app-mc",
    "o-ran-sc/ric-app-qp",
    "o-ran-sc/ric-app-qp-aimlfw",
    "o-ran-sc/ric-app-rc",
    "o-ran-sc/ric-plt-a1",
    "o-ran-sc/ric-plt-alarm-cpp",
    "o-ran-sc/ric-plt-alarm-go",
    "o-ran-sc/ric-plt-appmgr",
    "o-ran-sc/ric-plt-conflictmgr",
    "o-ran-sc/ric-plt-dbaas",
    "o-ran-sc/ric-plt-e2",
    "o-ran-sc/ric-plt-e2mgr",
    "o-ran-sc/ric-plt-jaegeradapter",
    "o-ran-sc/ric-plt-lib-rmr",
    "o-ran-sc/ric-plt-libe2ap",
    "o-ran-sc/ric-plt-nodeb-rnib",
    "o-ran-sc/ric-plt-o1",
    "o-ran-sc/ric-plt-ric-dep",
    "o-ran-sc/ric-plt-rtmgr",
    "o-ran-sc/ric-plt-sdl",
    "o-ran-sc/ric-plt-sdlgo",
    "o-ran-sc/ric-plt-sdlpy",
    "o-ran-sc/ric-plt-streaming-protobufs",
    "o-ran-sc/ric-plt-submgr",
    "o-ran-sc/ric-plt-tracelibcpp",
    "o-ran-sc/ric-plt-utils",
    "o-ran-sc/ric-plt-xapp-frame",
    "o-ran-sc/ric-plt-xapp-frame-cpp",
    "o-ran-sc/ric-plt-xapp-frame-py",
    "o-ran-sc/ric-plt-xapp-frame-rust",
    "o-ran-sc/sim-a1-interface",
    "o-ran-sc/sim-e2-interface",
    "o-ran-sc/sim-e2-interface-data",
    "o-ran-sc/sim-ns3-o-ran-e2",
    "o-ran-sc/sim-o1-interface",
    "o-ran-sc/sim-o1-ofhmp-interfaces",
    "o-ran-sc/smo-o1",
    "o-ran-sc/smo-o2",
    "o-ran-sc/smo-teiv",
    "o-ran-sc/smo-ves"
]

def fetch(url):
    """Fetch data from GitHub API with error handling"""
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 404:
            print(f"⚠️  Repository not found: {url}")
            return None
        else:
            print(f"⚠️  Error {r.status_code} for {url}")
            return []
    except Exception as e:
        print(f"❌ Exception fetching {url}: {e}")
        return []

def fetch_repo_info(repo):
    """Fetch comprehensive repository information"""
    print(f"Fetching {repo}...")
    
    # Get basic repo info
    repo_data = fetch(f"https://api.github.com/repos/{repo}")
    if repo_data is None or isinstance(repo_data, list):
        return None
    
    # Get branches
    branches_data = fetch(f"https://api.github.com/repos/{repo}/branches")
    branches = [b["name"] for b in branches_data] if branches_data else []
    
    # Get tags
    tags_data = fetch(f"https://api.github.com/repos/{repo}/tags")
    tags = [t["name"] for t in tags_data] if tags_data else []
    
    # Get releases
    releases_data = fetch(f"https://api.github.com/repos/{repo}/releases")
    releases = []
    if releases_data:
        releases = [{
            "name": r.get("name", r.get("tag_name", "Unknown")),
            "tag_name": r.get("tag_name", ""),
            "published_at": r.get("published_at", ""),
            "prerelease": r.get("prerelease", False)
        } for r in releases_data]
    
    # Get commits count (approximate from default branch)
    commits_data = fetch(f"https://api.github.com/repos/{repo}/commits?per_page=1")
    
    return {
        "name": repo,
        "description": repo_data.get("description", ""),
        "default_branch": repo_data.get("default_branch", "main"),
        "created_at": repo_data.get("created_at", ""),
        "updated_at": repo_data.get("updated_at", ""),
        "pushed_at": repo_data.get("pushed_at", ""),
        "language": repo_data.get("language", ""),
        "size": repo_data.get("size", 0),
        "archived": repo_data.get("archived", False),
        "branches": branches,
        "tags": tags,
        "releases": releases,
        "branch_count": len(branches),
        "tag_count": len(tags),
        "release_count": len(releases)
    }

def analyze_naming_patterns(data):
    """Analyze branch and tag naming patterns across repositories"""
    branch_patterns = defaultdict(int)
    tag_patterns = defaultdict(int)
    
    for repo_name, repo_info in data.items():
        if repo_info is None:
            continue
            
        # Analyze branch patterns
        for branch in repo_info.get("branches", []):
            # Common patterns
            if re.match(r'^master$', branch):
                branch_patterns['master'] += 1
            elif re.match(r'^main$', branch):
                branch_patterns['main'] += 1
            elif re.match(r'^develop(ment)?$', branch, re.IGNORECASE):
                branch_patterns['develop'] += 1
            elif re.match(r'^release[/-]', branch, re.IGNORECASE):
                branch_patterns['release-*'] += 1
            elif re.match(r'^feature[/-]', branch, re.IGNORECASE):
                branch_patterns['feature-*'] += 1
            elif re.match(r'^hotfix[/-]', branch, re.IGNORECASE):
                branch_patterns['hotfix-*'] += 1
            elif re.match(r'^v?\d+\.\d+', branch):
                branch_patterns['version-branches'] += 1
            else:
                branch_patterns['other'] += 1
        
        # Analyze tag patterns
        for tag in repo_info.get("tags", []):
            if re.match(r'^v\d+\.\d+\.\d+', tag):
                tag_patterns['v*.*.* (semver)'] += 1
            elif re.match(r'^\d+\.\d+\.\d+', tag):
                tag_patterns['*.*.* (semver no v)'] += 1
            elif re.match(r'^v\d+\.\d+', tag):
                tag_patterns['v*.* (major.minor)'] += 1
            elif re.match(r'^\d+\.\d+', tag):
                tag_patterns['*.* (major.minor no v)'] += 1
            elif re.match(r'^release[/-]', tag, re.IGNORECASE):
                tag_patterns['release-*'] += 1
            else:
                tag_patterns['other'] += 1
    
    return {
        "branch_patterns": dict(branch_patterns),
        "tag_patterns": dict(tag_patterns)
    }

def generate_markdown_report(data, patterns):
    """Generate comprehensive markdown report"""
    
    # Filter out None repositories
    valid_repos = {k: v for k, v in data.items() if v is not None}
    
    report = []
    report.append("# O-RAN SC Repository Analysis Report")
    report.append(f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\nTotal repositories analyzed: {len(valid_repos)}")
    
    # Executive Summary
    report.append("\n## Executive Summary")
    total_branches = sum(repo.get("branch_count", 0) for repo in valid_repos.values())
    total_tags = sum(repo.get("tag_count", 0) for repo in valid_repos.values())
    total_releases = sum(repo.get("release_count", 0) for repo in valid_repos.values())
    
    report.append(f"- **Total Branches**: {total_branches}")
    report.append(f"- **Total Tags**: {total_tags}")
    report.append(f"- **Total Releases**: {total_releases}")
    report.append(f"- **Repositories with no tags**: {sum(1 for repo in valid_repos.values() if repo.get('tag_count', 0) == 0)}")
    report.append(f"- **Repositories with no releases**: {sum(1 for repo in valid_repos.values() if repo.get('release_count', 0) == 0)}")
    
    # Repository Overview Table - Standard Format
    report.append("\n## Repository Overview")
    report.append("\n| Repository | Default Branch | Branches | Tags | Releases | Last Updated | Language | Status |")
    report.append("|------------|----------------|----------|------|----------|--------------|----------|--------|")
    
    for repo_name, repo_info in sorted(valid_repos.items()):
        last_updated = repo_info.get("updated_at", "")[:10] if repo_info.get("updated_at") else "Unknown"
        status = "🔒 Archived" if repo_info.get("archived") else "✅ Active"
        language = repo_info.get("language", "Unknown")
        
        report.append(f"| {repo_name} | {repo_info.get('default_branch', 'Unknown')} | {repo_info.get('branch_count', 0)} | {repo_info.get('tag_count', 0)} | {repo_info.get('release_count', 0)} | {last_updated} | {language} | {status} |")
    
    # Custom Analysis Table - Requested Format
    report.append("\n## Analysis Summary Table")
    report.append("\n| Repo Name | Branches | Tags | Issues | Suggested Mechanism |")
    report.append("|-----------|----------|------|--------|---------------------|")
    
    for repo_name, repo_info in sorted(valid_repos.items()):
        if repo_info is None:
            continue
            
        # Format branches info
        branches = repo_info.get("branches", [])
        branch_info = f"{len(branches)} branches"
        if branches:
            main_branches = [b for b in branches if b in ['main', 'master', 'develop']]
            if main_branches:
                branch_info += f" ({', '.join(main_branches)})"
        
        # Format tags info
        tags = repo_info.get("tags", [])
        tag_info = f"{len(tags)} tags"
        if tags:
            # Check for version patterns
            semver_tags = [t for t in tags[:3] if re.match(r'^v?\d+\.\d+\.\d+', t)]
            if semver_tags:
                tag_info += f" (Latest: {semver_tags[0] if semver_tags else 'N/A'})"
        
        # Identify issues
        issues = []
        if repo_info.get("default_branch") == "master":
            issues.append("Uses 'master' branch")
        if len(tags) == 0:
            issues.append("No tags")
        if repo_info.get("release_count", 0) == 0:
            issues.append("No releases")
        if repo_info.get("archived"):
            issues.append("Archived")
        
        # Check tag consistency
        if tags:
            semver_count = len([t for t in tags if re.match(r'^v\d+\.\d+\.\d+', t)])
            non_semver_count = len(tags) - semver_count
            if non_semver_count > 0:
                issues.append(f"Inconsistent tag format")
        
        issues_text = "; ".join(issues) if issues else "None identified"
        
        # Enhanced Suggest mechanism with priority and specific actions
        suggestions = []
        priority_actions = []
        
        # High Priority Actions
        if repo_info.get("default_branch") == "master":
            priority_actions.append("🔄 PRIORITY: Migrate default branch from 'master' to 'main'")
        
        if len(tags) == 0:
            priority_actions.append("🏷️ PRIORITY: Create initial version tags (start with v1.0.0)")
        
        if repo_info.get("release_count", 0) == 0 and len(tags) > 0:
            latest_tag = tags[0] if tags else "v1.0.0"
            priority_actions.append(f"📦 PRIORITY: Create GitHub release for tag {latest_tag}")
        
        # Standard Improvements
        if tags:
            semver_tags = [t for t in tags if re.match(r'^v\d+\.\d+\.\d+', t)]
            non_semver_tags = [t for t in tags if not re.match(r'^v\d+\.\d+\.\d+', t)]
            
            if len(non_semver_tags) > 0:
                suggestions.append(f"📏 Standardize {len(non_semver_tags)} tags to v*.*.* format")
            
            if len(semver_tags) > 0:
                suggestions.append(f"✅ Continue semantic versioning (current: {semver_tags[0]})")
        
        # Branch Management
        branches = repo_info.get("branches", [])
        if len(branches) > 20:
            suggestions.append(f"🌿 Consider cleanup: {len(branches)} branches (review stale branches)")
        elif len(branches) > 10:
            suggestions.append(f"🌿 Review branch strategy: {len(branches)} branches")
        
        # Workflow Improvements
        if repo_info.get("language") in ["Java", "Python", "Go", "JavaScript", "TypeScript"]:
            suggestions.append("🔧 Add automated CI/CD pipeline for releases")
        
        # Additional recommendations based on activity
        last_push = repo_info.get("pushed_at", "")
        if last_push:
            try:
                import datetime as dt
                last_push_date = dt.datetime.fromisoformat(last_push.replace('Z', '+00:00'))
                days_since_push = (dt.datetime.now().replace(tzinfo=last_push_date.tzinfo) - last_push_date).days
                if days_since_push > 365:
                    suggestions.append("⚠️ Repository inactive >1 year - consider archival review")
                elif days_since_push > 180:
                    suggestions.append("📅 Consider maintenance schedule - last update >6 months")
            except:
                pass
        
        # Combine priority and regular suggestions
        all_suggestions = priority_actions + suggestions
        
        if repo_info.get("archived"):
            suggestion_text = "🔒 ARCHIVED: Consider maintenance or migration strategy"
        elif not all_suggestions:
            suggestion_text = "✅ Well maintained - continue current practices"
        else:
            # Limit to most important suggestions for table readability
            suggestion_text = " | ".join(all_suggestions[:3])
            if len(all_suggestions) > 3:
                suggestion_text += f" | +{len(all_suggestions)-3} more"
        
        # Truncate only issues text for table readability, keep full suggestions
        if len(issues_text) > 60:
            issues_text = issues_text[:57] + "..."
            
        report.append(f"| {repo_name} | {branch_info} | {tag_info} | {issues_text} | {suggestion_text} |")
    
    # Branch Analysis
    report.append("\n## Branch Naming Patterns Analysis")
    report.append("\n| Pattern | Count | Percentage |")
    report.append("|---------|-------|------------|")
    
    total_pattern_count = sum(patterns["branch_patterns"].values())
    for pattern, count in sorted(patterns["branch_patterns"].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_pattern_count * 100) if total_pattern_count > 0 else 0
        report.append(f"| {pattern} | {count} | {percentage:.1f}% |")
    
    # Tag Analysis
    report.append("\n## Tag Naming Patterns Analysis")
    report.append("\n| Pattern | Count | Percentage |")
    report.append("|---------|-------|------------|")
    
    total_tag_pattern_count = sum(patterns["tag_patterns"].values())
    for pattern, count in sorted(patterns["tag_patterns"].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_tag_pattern_count * 100) if total_tag_pattern_count > 0 else 0
        report.append(f"| {pattern} | {count} | {percentage:.1f}% |")
    
    # Detailed Repository Analysis
    report.append("\n## Detailed Repository Analysis")
    
    for repo_name, repo_info in sorted(valid_repos.items()):
        report.append(f"\n### {repo_name}")
        report.append(f"- **Description**: {repo_info.get('description', 'No description available')}")
        report.append(f"- **Default Branch**: {repo_info.get('default_branch', 'Unknown')}")
        report.append(f"- **Language**: {repo_info.get('language', 'Unknown')}")
        report.append(f"- **Size**: {repo_info.get('size', 0)} KB")
        report.append(f"- **Last Push**: {repo_info.get('pushed_at', 'Unknown')[:10] if repo_info.get('pushed_at') else 'Unknown'}")
        
        # Branches
        branches = repo_info.get("branches", [])
        if branches:
            report.append(f"- **Branches ({len(branches)})**: {', '.join(branches)}")
        else:
            report.append("- **Branches**: None")
        
        # Tags
        tags = repo_info.get("tags", [])
        if tags:
            report.append(f"- **Tags ({len(tags)})**: {', '.join(tags)}")
        else:
            report.append("- **Tags**: None")
        
        # Releases
        releases = repo_info.get("releases", [])
        if releases:
            report.append(f"- **Releases ({len(releases)})**:")
            for release in releases[:5]:  # Show first 5 releases
                release_name = release.get("name", release.get("tag_name", "Unknown"))
                published_date = release.get("published_at", "")[:10] if release.get("published_at") else "Unknown"
                prerelease_flag = " (Pre-release)" if release.get("prerelease") else ""
                report.append(f"  - {release_name} - {published_date}{prerelease_flag}")
            if len(releases) > 5:
                report.append(f"  - *... and {len(releases) - 5} more*")
        else:
            report.append("- **Releases**: None")
    
    # Enhanced Recommendations
    report.append("\n## Detailed Recommendations for Standardization")
    
    # Priority Actions
    report.append("\n### 🚨 HIGH PRIORITY ACTIONS")
    report.append("\n#### 1. Branch Migration (ALL 77 repositories)")
    report.append("- **Current State**: All repositories use 'master' as default branch")
    report.append("- **Action Required**: Migrate to 'main' branch following GitHub's recommendations")
    report.append("- **Implementation Steps**:")
    report.append("  1. Create 'main' branch from current 'master'")
    report.append("  2. Update default branch in repository settings")
    report.append("  3. Update CI/CD pipelines and documentation")
    report.append("  4. Communicate change to contributors")
    report.append("  5. Archive 'master' branch after migration")
    
    report.append("\n#### 2. Formal Release Creation (ALL 77 repositories)")
    report.append("- **Current State**: ZERO formal GitHub releases across all repositories")
    report.append("- **Action Required**: Create releases for existing tags")
    report.append("- **Immediate Steps**:")
    report.append("  1. Identify latest stable tag for each repository")
    report.append("  2. Create GitHub release with comprehensive release notes")
    report.append("  3. Include changelog and breaking changes")
    report.append("  4. Add deployment/installation instructions")
    
    report.append("\n#### 3. Version Tagging (19 repositories without tags)")
    no_tag_repos = [name for name, info in valid_repos.items() if info.get("tag_count", 0) == 0]
    if no_tag_repos:
        report.append(f"- **Affected Repositories ({len(no_tag_repos)})**:")
        for repo in no_tag_repos[:10]:  # Show first 10
            report.append(f"  - {repo}")
        if len(no_tag_repos) > 10:
            report.append(f"  - *... and {len(no_tag_repos) - 10} more*")
    report.append("- **Action Required**: Implement semantic versioning starting with v1.0.0")
    
    # Standard Strategies
    report.append("\n### 📋 STANDARDIZATION STRATEGIES")
    
    report.append("\n#### Branch Strategy")
    report.append("1. **Default Branch**: 'main' (industry standard)")
    report.append("2. **Development Branches**:")
    report.append("   - `main` - Production-ready code")
    report.append("   - `develop` - Integration branch (optional, for GitFlow)")
    report.append("   - `release/v*.*.*` - Release preparation")
    report.append("   - `feature/*` - New features")
    report.append("   - `hotfix/*` - Critical fixes")
    report.append("   - `bugfix/*` - Non-critical bug fixes")
    
    report.append("\n#### Tag & Version Strategy")
    report.append("1. **Semantic Versioning (SemVer)**:")
    report.append("   - Format: `vMAJOR.MINOR.PATCH` (e.g., v2.1.3)")
    report.append("   - MAJOR: Breaking changes")
    report.append("   - MINOR: New features (backward compatible)")
    report.append("   - PATCH: Bug fixes (backward compatible)")
    report.append("2. **Pre-release Tags**: v2.1.0-alpha.1, v2.1.0-beta.2, v2.1.0-rc.1")
    report.append("3. **Consistency**: Always use 'v' prefix")
    
    report.append("\n#### Release Strategy")
    report.append("1. **Release Cadence**:")
    report.append("   - Major releases: Quarterly or bi-annually")
    report.append("   - Minor releases: Monthly (feature releases)")
    report.append("   - Patch releases: As needed (bug fixes)")
    report.append("2. **Release Process**:")
    report.append("   - Automated testing before release")
    report.append("   - Comprehensive release notes")
    report.append("   - Migration guides for breaking changes")
    report.append("   - Security advisories when applicable")
    
    # Implementation Plan
    report.append("\n### 🎯 IMPLEMENTATION ROADMAP")
    
    report.append("\n#### Phase 1: Foundation (Weeks 1-4)")
    report.append("1. **Branch Migration** (All repositories)")
    report.append("   - Week 1-2: Plan and communicate changes")
    report.append("   - Week 3-4: Execute migration in batches")
    report.append("2. **Tag Standardization** (Repositories with inconsistent tags)")
    report.append("   - Audit existing tags")
    report.append("   - Create standardized tag mapping")
    report.append("   - Apply consistent format")
    
    report.append("\n#### Phase 2: Release Implementation (Weeks 5-8)")
    report.append("1. **Create Initial Releases** (All repositories with tags)")
    report.append("2. **Implement Release Workflows** (CI/CD automation)")
    report.append("3. **Documentation Updates** (README, CONTRIBUTING guides)")
    
    report.append("\n#### Phase 3: Continuous Improvement (Weeks 9-12)")
    report.append("1. **Monitoring and Metrics** (Release frequency, adoption)")
    report.append("2. **Developer Training** (New workflows and standards)")
    report.append("3. **Policy Enforcement** (Branch protection, required reviews)")
    
    # Repository-Specific Actions
    report.append("\n### 📦 REPOSITORY-SPECIFIC RECOMMENDATIONS")
    
    # High-activity repositories
    high_activity_repos = [(name, info) for name, info in valid_repos.items() 
                          if info.get("tag_count", 0) > 15 or info.get("branch_count", 0) > 15]
    if high_activity_repos:
        report.append(f"\n#### High-Activity Repositories ({len(high_activity_repos)} repos)")
        report.append("*Repositories with >15 tags or >15 branches - need immediate attention*")
        for repo_name, repo_info in sorted(high_activity_repos, key=lambda x: x[1].get("tag_count", 0), reverse=True)[:5]:
            report.append(f"- **{repo_name}**: {repo_info.get('branch_count', 0)} branches, {repo_info.get('tag_count', 0)} tags")
            report.append(f"  - Action: Immediate release creation and branch cleanup")
    
    # Critical repositories (based on language/type)
    critical_langs = ["Java", "Go", "Python", "C++", "C"]
    critical_repos = [(name, info) for name, info in valid_repos.items() 
                     if info.get("language") in critical_langs and info.get("tag_count", 0) == 0]
    if critical_repos:
        report.append(f"\n#### Critical Repositories Without Versions ({len(critical_repos)} repos)")
        report.append("*Production-ready languages without any version tags*")
        for repo_name, repo_info in critical_repos[:5]:
            report.append(f"- **{repo_name}** ({repo_info.get('language', 'Unknown')})")
            report.append(f"  - Action: URGENT - Create v1.0.0 tag and release")
    
    # Issues and Concerns
    repos_no_tags = [name for name, info in valid_repos.items() if info.get("tag_count", 0) == 0]
    repos_no_releases = [name for name, info in valid_repos.items() if info.get("release_count", 0) == 0]
    archived_repos = [name for name, info in valid_repos.items() if info.get("archived", False)]
    
    report.append("\n## Issues and Concerns")
    
    if repos_no_tags:
        report.append(f"\n### Repositories without Tags ({len(repos_no_tags)})")
        for repo in repos_no_tags:
            report.append(f"- {repo}")
    
    if repos_no_releases:
        report.append(f"\n### Repositories without Releases ({len(repos_no_releases)})")
        for repo in repos_no_releases:
            report.append(f"- {repo}")
    
    if archived_repos:
        report.append(f"\n### Archived Repositories ({len(archived_repos)})")
        for repo in archived_repos:
            report.append(f"- {repo}")
    
    return "\n".join(report)

# Main execution
print("🚀 Starting O-RAN SC Repository Analysis...")
print(f"Analyzing {len(repos)} repositories...")

if TOKEN:
    print("✅ GitHub token found. Using authenticated requests.")
else:
    print("⚠️  Warning: No GITHUB_TOKEN found. API rate limits may apply.")
    print("   Set GITHUB_TOKEN environment variable for better performance.")

# Determine which repos to analyze based on token availability
if TOKEN:
    # Use all repos if token is available
    analyze_repos = repos
    print(f"Using all {len(analyze_repos)} repositories with authentication.")
else:
    # Use smaller subset without token due to rate limits
    analyze_repos = repos[:10]  # Test with first 10 repos
    print(f"No token available. Testing with first {len(analyze_repos)} repositories.")
    print("⚠️  For complete analysis of all 77 repositories, please provide a valid GitHub token.")

# Fetch comprehensive repository data
results = {}
for i, repo in enumerate(analyze_repos, 1):
    print(f"[{i}/{len(analyze_repos)}] Processing {repo}...")
    repo_info = fetch_repo_info(repo)
    results[repo] = repo_info
    
    # Add delay between requests when no token to avoid rate limiting
    if not TOKEN and i < len(analyze_repos):
        import time
        time.sleep(1)

# Analyze patterns
print("\n📊 Analyzing naming patterns...")
patterns = analyze_naming_patterns(results)

# Generate reports
print("\n📝 Generating reports...")

# Save raw data as JSON
with open("repo_analysis_data.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print("✅ Saved raw data to repo_analysis_data.json")

# Generate markdown report
markdown_report = generate_markdown_report(results, patterns)
with open("O-RAN_SC_Repository_Analysis_Report.md", "w") as f:
    f.write(markdown_report)
print("✅ Saved analysis report to O-RAN_SC_Repository_Analysis_Report.md")

print("\n🎉 Analysis complete!")
print("📋 Files generated:")
print("   - repo_analysis_data.json (raw data)")
print("   - O-RAN_SC_Repository_Analysis_Report.md (comprehensive report)")

# Quick summary
valid_repos = {k: v for k, v in results.items() if v is not None}
total_branches = sum(repo.get("branch_count", 0) for repo in valid_repos.values())
total_tags = sum(repo.get("tag_count", 0) for repo in valid_repos.values())
total_releases = sum(repo.get("release_count", 0) for repo in valid_repos.values())

print(f"\n📈 Quick Summary:")
print(f"   - Repositories analyzed: {len(valid_repos)}")
print(f"   - Total branches: {total_branches}")
print(f"   - Total tags: {total_tags}")
print(f"   - Total releases: {total_releases}")
print(f"   - Repos without tags: {sum(1 for repo in valid_repos.values() if repo.get('tag_count', 0) == 0)}")
print(f"   - Repos without releases: {sum(1 for repo in valid_repos.values() if repo.get('release_count', 0) == 0)}")