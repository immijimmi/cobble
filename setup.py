from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme_file:
    long_description = readme_file.read()

setup(
    name="<package name>",
    packages=[
        "<main package folder>"
    ],
    version="0.1.0",
    license="MIT",  #####
    description="<package description>",
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="<author username/name>",
    author_email="<author email>",
    url="https://github.com/<author username>/<package name>",
    download_url="<tar.gz download link for the package>",
    keywords=[  #####
            
    ],
    install_requires=[  #####
        
    ],
    classifiers=[  #####
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
)
