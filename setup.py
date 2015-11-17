from setuptools import setup

setup(
    name="date_range_parser",
    version="0.6.2",
    author="Ashutosh Priyadarshy",
    author_email="static@hq.siftnet.com",
    packages=['date_range_parser'],
    url='https://github.com/priyadarshy/python-sandbox',
    description='date_range_parser accepts natural language input and maps it to an list of (start, end) times.',
    install_requires=[
        "nltk==2.0.4",
        "parsedatetime",
        "python-dateutil",
        "pytz",
        "textblob"
    ]
)
