from setuptools import setup, find_packages

setup(
    name="topsis-pranshu-102313009",
    version="1.0.4",
    author="Pranshu Goel",
    author_email="your@email.com",
    description="TOPSIS command-line tool",
    packages=find_packages(),
    install_requires=["pandas", "numpy"],
    entry_points={
        "console_scripts": [
            "topsis=topsis_pranshu.topsis:main"
        ]
    },
)
