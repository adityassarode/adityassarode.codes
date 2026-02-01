from setuptools import setup, find_packages

setup(
    name="adityassarode.codes",
    version="1.0.0",
    author="Aditya Sarode",
    description="Official code projects by Aditya Sarode",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "adityassarode-codes=adityassarode_codes.cli:main"
        ]
    },
)
