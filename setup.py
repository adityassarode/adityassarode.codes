from setuptools import setup, find_packages
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()
setup(
    name="adityassarode.codes",
    version="1.0.2",
    author="Aditya Sarode",
    description="Official code projects by Aditya Sarode",
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
  
)
