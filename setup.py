from setuptools import setup, find_packages

setup(
    name="visualtrick",
    version="1.6.0",
    description="AI-powered repository visualization tool",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "visualtrick=visualtrick.visualtrick:main"
        ]
    },
    python_requires=">=3.9",
)