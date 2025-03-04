import csv
import requests
import json
from typing import Dict, List, Tuple
from datetime import datetime

def fetch_package_data(url: str) -> Dict[str, dict]:
    """Fetch package data from the API and index it by package name and architecture."""
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Create a nested dictionary: package_name -> arch -> package_info
    indexed_data = {}
    for pkg in data:
        if pkg['name'] not in indexed_data:
            indexed_data[pkg['name']] = {}
        indexed_data[pkg['name']][pkg['architecture']] = pkg
    
    return indexed_data

def analyze_packages(csv_path: str) -> Tuple[List[dict], List[dict], List[dict]]:
    """
    Analyze packages listed in the CSV file against the API data.
    Returns: (bad_packages, version_mismatches, all_packages)
    """
    # Fetch data from both APIs
    print("Fetching package data...")
    amd64_data = fetch_package_data('https://amd64.reproduce.debian.net/api/v0/pkgs/list')
    all_data = fetch_package_data('https://all.reproduce.debian.net/api/v0/pkgs/list')
    
    bad_packages = []
    version_mismatches = []
    all_packages = []
    
    print("Analyzing packages...")
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) != 3:
                print(f"Warning: Skipping malformed row: {row}")
                continue
                
            name, arch, expected_version = row
            
            # Choose the appropriate API data based on architecture
            api_data = amd64_data if arch == 'amd64' else all_data
            
            package_info = None
            if name in api_data and arch in api_data[name]:
                package_info = api_data[name][arch]
                
                # Add to all packages list
                all_packages.append({
                    'name': name,
                    'architecture': arch,
                    'version': package_info['version'],
                    'status': package_info['status'],
                    'built_at': package_info['built_at']
                })
                
                # Check for bad status
                if package_info['status'] == 'BAD':
                    bad_packages.append(package_info)
                
                # Check version mismatch
                if package_info['version'] != expected_version:
                    version_mismatches.append({
                        'name': name,
                        'architecture': arch,
                        'expected_version': expected_version,
                        'actual_version': package_info['version']
                    })
            else:
                print(f"Warning: Package not found in API data: {name} ({arch})")
    
    return bad_packages, version_mismatches, all_packages

def print_report(bad_packages: List[dict], version_mismatches: List[dict], all_packages: List[dict]):
    """Print a formatted report of the analysis results."""
    print("\n=== Package Analysis Report ===\n")
    
    # Overall statistics
    total_packages = len(all_packages)
    bad_count = len(bad_packages)
    good_count = total_packages - bad_count
    
    print(f"Total packages analyzed: {total_packages}")
    print(f"Good packages: {good_count} ({(good_count/total_packages*100):.1f}%)")
    print(f"Bad packages: {bad_count} ({(bad_count/total_packages*100):.1f}%)")
    
    # List bad packages
    if bad_packages:
        print("\nBad Packages:")
        for pkg in bad_packages:
            built_at = datetime.fromisoformat(pkg['built_at'].replace('Z', '+00:00'))
            print(f"- {pkg['name']} ({pkg['architecture']}) version {pkg['version']}")
            print(f"  Built at: {built_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # List version mismatches
    if version_mismatches:
        print("\nVersion Mismatches:")
        for mismatch in version_mismatches:
            print(f"- {mismatch['name']} ({mismatch['architecture']})")
            print(f"  Expected: {mismatch['expected_version']}")
            print(f"  Actual: {mismatch['actual_version']}")

def main():
    csv_path = 'build/packages.csv'
    bad_packages, version_mismatches, all_packages = analyze_packages(csv_path)
    print_report(bad_packages, version_mismatches, all_packages)

if __name__ == '__main__':
    main()