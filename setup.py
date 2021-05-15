from setuptools import setup, find_packages

setup(name="ElenaAnalysis",
      version="1.0",
      description="Package for data analysis of Elena",
      packages=find_packages(),
      package_data={"ElenaAnalysis": ["data/*"]})
