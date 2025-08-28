from setuptools import setup, find_packages

setup(
    name="seo-audit-tool",
    version="0.1.0",
    description="Professional SEO Audit Tool",
    author="SEO Audit Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "selectolax>=0.3.17",
        "urllib3>=2.0.0",
        "pandas>=2.0.0",
        "httpx>=0.25.0",
        "playwright>=1.40.0",
        "lxml>=4.9.3"
    ],
    entry_points={
        "console_scripts": [
            "seo-audit=seo_audit.cli:main",
        ],
    },
    python_requires=">=3.8",
)