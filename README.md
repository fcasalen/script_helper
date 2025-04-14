# Python 
```python
# basic usage
from script_helper import collect_packages_by_author_email

# Find packages by a single author email
packages = collect_packages_by_author_email(
    target_emails=["example@domain.com"],
    python_packages_folder="C:\\Program Files\\Python313\\Lib\\site-packages"
)

# Print the package names found
print(f"Found {len(packages)} packages:")
for package_name in packages:
    print(f"- {package_name}")

# Search for packages from multiple authors
packages = collect_packages_by_author_email(
    target_emails=["dev1@company.com", "dev2@company.com"],
    python_packages_folder="C:\\Program Files\\Python313\\Lib\\site-packages"
)
```

# CLI
```bash

# Find packages by a single author email
script_helper your.email@example.com

# Find packages by multiple author emails and saving json
script_helper dev1@company.com dev2@company.com another@email.org --ptyhon_packages_folder "C:\Program Files\Python313\Lib\site-packages" --save_json
```