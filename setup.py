from setuptools import setup

setup(
    name="date_range_parser",
    version="1.0.0",
    author="Ashutosh Priyadarshy",
    author_email="root@ashuto.sh",
    packages=['date_range_parser'],
    url='https://github.com/priyadarshy/date-range-parser',
    description='date_range_parser accepts natural language input and maps it to an list of (start, end) times.',
    install_requires=[
        "nltk==2.0.4",
        "parsedatetime",
        "python-dateutil",
        "pytz",
        "textblob",
        "pyyaml",
        "six"
    ]
)
