from setuptools import setup, find_packages

setup(
    name = 'django-basic-apps',
    version = '0.8',
    description = 'Django Basic Apps',
    long_description = open('README.rst').read(),
    url = 'https://github.com/pigmonkey/django-basic-apps',
    author = 'Nathan Borror and Pig Monkey',
    author_email = 'pm@pig-monkey.com',

    packages = find_packages(),
    zip_safe=False,
)
