from setuptools import setup, find_packages

# Get the long description from the README file
with open('README.md', 'r', encoding="utf-8") as f:
    long_description = f.read()

__version__ = "0.0.0"

REPO_NAME = "end-to-end-mlops-project"
SRC_REPO = "mlops"
AUTHOR_USER_NAME = "Demiga-g"
AUTHOR_EMAIL = "midegageorge2@gmail.com"


setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description='Python package for use in MLOps project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}',
    project_urls={
        'Bug Tracker': f'https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues',
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # install_requires=[
    #     'numpy',
    #     'pandas',
    #     'seaborn',
    #     'scikit-learn',
    #     'matplotlib',
    # ],
)
