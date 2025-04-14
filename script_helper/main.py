from pathlib import Path
from cli_pprinter import CLIPPrinter
import email.parser
import importlib.metadata
import argparse
import json

def collect_packages_by_author_email(target_emails:list[str], python_packages_folder:str) -> dict[str, dict[str, str]]:
    """
    Collects metadata of all packages authored by the specified email address.
    
    Args:
        target_emails (list[str]): The author emails list to search for
        python_packages_folder (str): The folder containing Python packages
        
    Returns:
        dict: Dictionary mapping package names to their metadata
    """
    assert target_emails, "No target emails provided"
    assert Path(python_packages_folder).exists(), f"Folder {python_packages_folder} does not exist"
    assert Path(python_packages_folder).is_dir(), f"{python_packages_folder} is not a directory"
    assert all(isinstance(email, str) for email in target_emails), "All target emails must be strings"
    assert all('@' in email for email in target_emails), "All target emails must be valid email addresses"
    result = {}
    target_emails = [target_email.lower() for target_email in target_emails]
    dist_info_dirs = Path(python_packages_folder).glob('*.dist-info')
    for dist_info in dist_info_dirs:
        metadata_path = dist_info / 'METADATA'
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_content = f.read()
            parser = email.parser.Parser()
            parsed_metadata = parser.parsestr(metadata_content)
            author_email = parsed_metadata.get('Author-email', '')
            if author_email.lower() in target_emails:
                package_name = dist_info.name.split('-')[0]
                try:
                    full_metadata = dict(importlib.metadata.metadata(package_name))
                    for field in ['Requires-Dist', 'Classifier']:
                        if field in full_metadata:
                            full_metadata[field] = importlib.metadata.metadata(package_name).get_all(field)
                    result[package_name] = full_metadata
                except importlib.metadata.PackageNotFoundError:
                    result[package_name] = {k: v for k, v in parsed_metadata.items()}
                result[package_name]['entry_points'] = []
    eps = importlib.metadata.entry_points(group='console_scripts')
    for ep in eps:
        if ep.dist and ep.dist.name in result:
            result[ep.dist.name]['entry_points'].append(ep.name)
    return result

def cli():
    """
    Command-line interface for the script.
    """
    parser = argparse.ArgumentParser(description="Collect Python packages by author email.")
    parser.add_argument('target_emails', nargs='+', help='List of author emails to search for')
    parser.add_argument('--python_packages_folder', default=r'C:\Program Files\Python313\Lib\site-packages',
                        help='Folder containing Python packages (default: %(default)s)')
    parser.add_argument('--requirements', action='store_true',
                        help='Print requirements if available')
    parser.add_argument('--save_json', action='store_true',
                        help='Save results to a JSON file')
    args = parser.parse_args()
    packages = collect_packages_by_author_email(
        target_emails=args.target_emails,
        python_packages_folder=args.python_packages_folder
    )
    if args.save_json:
        with open('packages.json', 'w', encoding='utf-8') as f:
            json.dump(packages, f, indent=4)
        CLIPPrinter.green("Results saved to packages.json")
    print(f"Found {len(packages)} packages by {', '.join(args.target_emails)}:")
    for package_name, metadata in packages.items():
        CLIPPrinter.line_breaker()
        CLIPPrinter.green(f"\n{package_name}:")
        CLIPPrinter.red(f"Version: {metadata.get('Version', 'N/A')}")
        CLIPPrinter.cyan(f"Summary: {metadata.get('Summary', 'N/A')}")
        CLIPPrinter.yellow(f"Author: {metadata.get('Author', 'N/A')}")
        if packages[package_name]['entry_points']:
            CLIPPrinter.white_underline(f"Entry Points: {', '.join(packages[package_name]['entry_points'])}")
        else:
            CLIPPrinter.white_underline("No entry points")
        if 'Description' in metadata and metadata['Description']:
            print(f"Description:\n{metadata['Description']}")
        else:
            print('No description')
        if args.requirements and 'Requires-Dist' in metadata and metadata['Requires-Dist']:
            CLIPPrinter.red_underline("Requirements:")
            for req in metadata['Requires-Dist']:
                CLIPPrinter.red_underline(f"    - {req}")
        CLIPPrinter.line_breaker()