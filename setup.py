from setuptools import setup, find_packages

setup(
    name="script_helper",
    version="0.1.1",
    license="GNU General Public License",
    author="fcasalen",
    author_email="fcasalen@gmail.com",
    description="package to get packages metadata based on author email",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open('requirements.txt').readlines(),
    long_description=open("README.md").read(),
    classifiers=[
        "Development Status :: 5 - Prodution/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13"
    ],
    entry_points={"console_scripts": [
        "script_helper=script_helper.main:cli"
    ]}
)
