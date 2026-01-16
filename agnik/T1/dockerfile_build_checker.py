#!/usr/bin/env python3
"""
Dockerfile Build Checker for o-ran-sc repositories
Tests Dockerfile builds and generates a summary report
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import requests
from tabulate import tabulate

# Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_ORG = 'o-ran-sc'
BASE_DIR = Path('/tmp/dockerfile_build_check')
LOG_DIR = BASE_DIR / 'logs'
RESULTS_DIR = BASE_DIR / 'results'

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / f'build_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DockerfileBuildChecker:
    def __init__(self, github_token: str, github_org: str):
        self.github_token = github_token
        self.github_org = github_org
        self.results: List[Dict] = []
        self.session = requests.Session()
        # GitHub API authentication
        if github_token:
            self.session.headers.update({
                'Authorization': f'Bearer {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        
        # Detect Docker command (with or without sudo)
        self.docker_cmd = self._detect_docker_command()
    
    def _detect_docker_command(self) -> List[str]:
        """Detect if Docker needs sudo or not"""
        # Try without sudo first
        try:
            result = subprocess.run(['docker', '--version'], 
                                 capture_output=True, timeout=5,
                                 stderr=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                # Also check if we can run docker info
                info_result = subprocess.run(['docker', 'info'],
                                           capture_output=True, timeout=5,
                                           stderr=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL)
                if info_result.returncode == 0:
                    return ['docker']
        except:
            pass
        
        # Try with sudo
        try:
            result = subprocess.run(['sudo', 'docker', '--version'], 
                                 capture_output=True, timeout=5,
                                 stderr=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL)
            if result.returncode == 0:
                # Also check if we can run docker info with sudo
                info_result = subprocess.run(['sudo', 'docker', 'info'],
                                           capture_output=True, timeout=5,
                                           stderr=subprocess.DEVNULL,
                                           stdout=subprocess.DEVNULL)
                if info_result.returncode == 0:
                    logger.info("Using 'sudo docker' for Docker commands")
                    return ['sudo', 'docker']
        except:
            pass
        
        # If docker command exists but needs sudo, use sudo
        # Check if docker binary exists
        docker_paths = ['/usr/bin/docker', '/usr/local/bin/docker']
        for path in docker_paths:
            if os.path.exists(path):
                logger.info("Docker found but requires sudo, using 'sudo docker'")
                return ['sudo', 'docker']
        
        # Default to sudo docker (most common case on servers)
        logger.info("Defaulting to 'sudo docker' (most common on servers)")
        return ['sudo', 'docker']

    def get_repositories(self, limit: Optional[int] = None, sort_by_updated: bool = False) -> List[str]:
        """Fetch repositories from GitHub organization"""
        repos_data = []
        page = 1
        per_page = 100
        
        logger.info(f"Fetching repositories from {self.github_org}...")
        
        while True:
            url = f'https://api.github.com/orgs/{self.github_org}/repos'
            params = {'page': page, 'per_page': per_page, 'type': 'all', 'sort': 'updated', 'direction': 'desc'}
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    break
                
                if sort_by_updated:
                    # Store full repo data for sorting
                    repos_data.extend(data)
                else:
                    # Just store names
                    for repo in data:
                        repos_data.append(repo['full_name'])
                        if limit and len(repos_data) >= limit:
                            return repos_data
                
                # Check if we have enough or if there are more pages
                if limit and len(repos_data) >= limit:
                    break
                if len(data) < per_page:
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching repositories: {e}")
                break
        
        # If sorting by updated date, sort and return limited list
        if sort_by_updated:
            # Sort by updated_at date (most recent first)
            repos_data.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            repos = [repo['full_name'] for repo in repos_data]
            if limit:
                repos = repos[:limit]
            logger.info(f"Found {len(repos_data)} repositories, returning {len(repos)} most recently updated")
            return repos
        
        logger.info(f"Found {len(repos_data)} repositories")
        return repos_data

    def find_dockerfiles(self, repo_path: Path) -> List[Path]:
        """Find all Dockerfiles in a repository"""
        dockerfiles = []
        
        # Common Dockerfile names
        dockerfile_names = ['Dockerfile', 'Dockerfile.*', '*.dockerfile']
        
        # Search for Dockerfile
        if (repo_path / 'Dockerfile').exists():
            dockerfiles.append(repo_path / 'Dockerfile')
        
        # Search for Dockerfile.* patterns
        for dockerfile in repo_path.rglob('Dockerfile*'):
            if dockerfile.is_file() and 'Dockerfile' in dockerfile.name:
                if dockerfile not in dockerfiles:
                    dockerfiles.append(dockerfile)
        
        return dockerfiles

    def clone_repository(self, repo_name: str) -> Optional[Path]:
        """Clone a repository"""
        # Use token in URL for authentication
        if self.github_token:
            repo_url = f'https://{self.github_token}@github.com/{repo_name}.git'
        else:
            repo_url = f'https://github.com/{repo_name}.git'
        
        repo_path = BASE_DIR / repo_name.replace('/', '_')
        
        # Remove existing clone if it exists
        if repo_path.exists():
            logger.info(f"Removing existing clone: {repo_path}")
            subprocess.run(['rm', '-rf', str(repo_path)], check=False)
        
        logger.info(f"Cloning {repo_name}...")
        try:
            # Set environment to hide token from process list
            env = os.environ.copy()
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=300,
                env=env
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to clone {repo_name}: {result.stderr}")
                return None
            
            return repo_path
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout cloning {repo_name}")
            return None
        except Exception as e:
            logger.error(f"Error cloning {repo_name}: {e}")
            return None

    def build_dockerfile(self, dockerfile_path: Path, repo_name: str) -> Dict:
        """Attempt to build a Dockerfile"""
        result = {
            'dockerfile': str(dockerfile_path.relative_to(BASE_DIR)),
            'status': 'UNKNOWN',
            'error': None,
            'build_time': None
        }
        
        # Get the directory containing the Dockerfile
        build_context = dockerfile_path.parent
        
        # Generate a safe image name
        image_name = f"test-build-{repo_name.replace('/', '-').replace('_', '-')}"
        image_name = image_name.lower()[:128]  # Docker image name length limit
        
        logger.info(f"Building {dockerfile_path}...")
        start_time = datetime.now()
        
        try:
            # Build the Docker image
            build_cmd = self.docker_cmd + [
                'build',
                '-f', str(dockerfile_path),
                '-t', image_name,
                str(build_context)
            ]
            
            build_result = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            build_time = (datetime.now() - start_time).total_seconds()
            result['build_time'] = build_time
            
            if build_result.returncode == 0:
                result['status'] = 'SUCCESS'
                logger.info(f"✓ Build successful for {dockerfile_path}")
                
                # Clean up the image
                try:
                    subprocess.run(self.docker_cmd + ['rmi', image_name], 
                                 capture_output=True, timeout=30)
                except:
                    pass
            else:
                result['status'] = 'FAILED'
                # Get full error output (stderr + stdout for Docker build)
                full_error = (build_result.stderr + "\n" + build_result.stdout).strip()
                result['error'] = full_error[:2000]  # Increased limit for better debugging
                logger.error(f"✗ Build failed for {dockerfile_path}")
                # Log first 500 chars to console, full error to file
                logger.error(f"Error (first 500 chars): {result['error'][:500]}")
                if len(full_error) > 500:
                    logger.debug(f"Full error ({len(full_error)} chars) saved in result")
                
        except subprocess.TimeoutExpired:
            result['status'] = 'TIMEOUT'
            result['error'] = 'Build timeout (10 minutes)'
            logger.error(f"✗ Build timeout for {dockerfile_path}")
        except Exception as e:
            result['status'] = 'ERROR'
            result['error'] = str(e)[:500]
            logger.error(f"✗ Build error for {dockerfile_path}: {e}")
        
        return result

    def check_repository(self, repo_name: str) -> Dict:
        """Check all Dockerfiles in a repository"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Checking repository: {repo_name}")
        logger.info(f"{'='*60}")
        
        # Create repository-specific log directory
        repo_log_dir = LOG_DIR / repo_name.replace('/', '_')
        repo_log_dir.mkdir(parents=True, exist_ok=True)
        repo_log_file = repo_log_dir / f'build_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        # Create repository-specific logger
        repo_logger = logging.getLogger(f'repo_{repo_name}')
        repo_logger.setLevel(logging.INFO)
        # Remove existing handlers to avoid duplicates
        repo_logger.handlers = []
        repo_handler = logging.FileHandler(repo_log_file)
        repo_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        repo_logger.addHandler(repo_handler)
        repo_logger.propagate = False  # Don't propagate to root logger
        
        repo_result = {
            'repository': repo_name,
            'status': 'NO_DOCKERFILE',
            'dockerfiles': [],
            'total_dockerfiles': 0,
            'successful_builds': 0,
            'failed_builds': 0,
            'failed_dockerfile_names': [],
            'errors': [],
            'log_file': str(repo_log_file)
        }
        
        # Clone repository
        repo_logger.info(f"Cloning repository: {repo_name}")
        repo_path = self.clone_repository(repo_name)
        if not repo_path:
            repo_result['status'] = 'CLONE_FAILED'
            repo_result['errors'].append('Failed to clone repository')
            repo_logger.error(f"Failed to clone repository: {repo_name}")
            return repo_result
        
        # Find Dockerfiles
        dockerfiles = self.find_dockerfiles(repo_path)
        repo_result['total_dockerfiles'] = len(dockerfiles)
        repo_logger.info(f"Found {len(dockerfiles)} Dockerfile(s)")
        
        if not dockerfiles:
            logger.info(f"No Dockerfiles found in {repo_name}")
            repo_logger.info(f"No Dockerfiles found in {repo_name}")
            return repo_result
        
        repo_result['status'] = 'CHECKING'
        logger.info(f"Found {len(dockerfiles)} Dockerfile(s)")
        
        # Build each Dockerfile
        for dockerfile in dockerfiles:
            repo_logger.info(f"Building {dockerfile.name}...")
            build_result = self.build_dockerfile(dockerfile, repo_name)
            repo_result['dockerfiles'].append(build_result)
            
            if build_result['status'] == 'SUCCESS':
                repo_result['successful_builds'] += 1
                repo_logger.info(f"✓ Build successful: {dockerfile.name}")
            else:
                repo_result['failed_builds'] += 1
                # Add failed Dockerfile name
                repo_result['failed_dockerfile_names'].append(dockerfile.name)
                repo_logger.error(f"✗ Build failed: {dockerfile.name}")
                if build_result['error']:
                    error_msg = build_result['error'][:1000]  # Log first 1000 chars
                    repo_logger.error(f"Error: {error_msg}")
                    repo_result['errors'].append(f"{dockerfile.name}: {build_result['error']}")
        
        # Determine overall status
        if repo_result['successful_builds'] > 0 and repo_result['failed_builds'] == 0:
            repo_result['status'] = 'ALL_SUCCESS'
            repo_logger.info(f"✓ All builds successful for {repo_name}")
        elif repo_result['successful_builds'] > 0:
            repo_result['status'] = 'PARTIAL_SUCCESS'
            repo_logger.warning(f"⚠ Partial success: {repo_result['successful_builds']} successful, {repo_result['failed_builds']} failed")
        else:
            repo_result['status'] = 'ALL_FAILED'
            repo_logger.error(f"✗ All builds failed for {repo_name}")
        
        repo_logger.info(f"Summary: {repo_result['successful_builds']} successful, {repo_result['failed_builds']} failed out of {repo_result['total_dockerfiles']} total")
        
        # Clean up cloned repository
        try:
            subprocess.run(['rm', '-rf', str(repo_path)], check=False)
        except:
            pass
        
        # Close repository logger handler
        for handler in repo_logger.handlers:
            handler.close()
            repo_logger.removeHandler(handler)
        
        return repo_result

    def generate_report(self, results: List[Dict]) -> str:
        """Generate a summary report table"""
        table_data = []
        
        for result in results:
            status_icon = {
                'ALL_SUCCESS': '✓',
                'PARTIAL_SUCCESS': '⚠',
                'ALL_FAILED': '✗',
                'NO_DOCKERFILE': '-',
                'CLONE_FAILED': '✗',
                'CHECKING': '...'
            }.get(result['status'], '?')
            
            # Format failed Dockerfile names (truncate if too long)
            failed_names = result.get('failed_dockerfile_names', [])
            if failed_names:
                failed_names_str = ', '.join(failed_names)
                # Truncate if longer than 50 chars
                if len(failed_names_str) > 50:
                    failed_names_str = failed_names_str[:47] + '...'
            else:
                failed_names_str = '-'
            
            table_data.append([
                result['repository'],
                result['total_dockerfiles'],
                result['successful_builds'],
                result['failed_builds'],
                failed_names_str
            ])
        
        headers = ['Repository', '# Dockerfiles', '# Successful', '# Failed', 'Failed Dockerfile Names']
        table = tabulate(table_data, headers=headers, tablefmt='grid')
        
        return table

    def run(self, repo_list: Optional[List[str]] = None, limit: Optional[int] = None, recent: bool = False):
        """Run the build checker"""
        logger.info("Starting Dockerfile Build Checker")
        logger.info(f"Log file: {log_file}")
        
        # Get repositories
        if repo_list:
            repos = repo_list
        else:
            repos = self.get_repositories(limit=limit, sort_by_updated=recent)
        
        logger.info(f"Checking {len(repos)} repositories...")
        
        # Check each repository
        for repo in repos:
            result = self.check_repository(repo)
            self.results.append(result)
        
        # Generate report
        report = self.generate_report(self.results)
        
        # Save report
        report_file = RESULTS_DIR / f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        with open(report_file, 'w') as f:
            f.write("Dockerfile Build Check Report\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Repositories checked: {len(repos)}\n\n")
            f.write(report)
            f.write("\n\n")
            f.write("Detailed Results:\n")
            f.write("-" * 60 + "\n")
            for result in self.results:
                f.write(f"\nRepository: {result['repository']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Dockerfiles: {result['total_dockerfiles']}\n")
                if result['errors']:
                    f.write(f"Errors:\n")
                    for error in result['errors']:
                        f.write(f"  - {error}\n")
        
        # Print report
        print("\n" + "=" * 60)
        print("BUILD CHECK SUMMARY")
        print("=" * 60)
        print(report)
        print(f"\nDetailed report saved to: {report_file}")
        print(f"Log file: {log_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check Dockerfile builds for o-ran-sc repositories')
    parser.add_argument('--repos', nargs='+', help='Specific repositories to check (format: org/repo)')
    parser.add_argument('--limit', type=int, help='Limit number of repositories to check')
    parser.add_argument('--test', action='store_true', help='Test mode: check 2 repositories')
    parser.add_argument('--recent', type=int, help='Check N most recently updated repositories')
    
    args = parser.parse_args()
    
    checker = DockerfileBuildChecker(GITHUB_TOKEN, GITHUB_ORG)
    
    if args.test:
        # Test with 2 specific repos
        test_repos = ['o-ran-sc/ric-app-ad', 'o-ran-sc/ric-app-qp']
        logger.info("Running in TEST mode with 2 repositories")
        checker.run(repo_list=test_repos)
    elif args.recent:
        logger.info(f"Running for {args.recent} most recently updated repositories")
        checker.run(limit=args.recent, recent=True)
    elif args.repos:
        checker.run(repo_list=args.repos)
    else:
        checker.run(limit=args.limit)


if __name__ == '__main__':
    main()

