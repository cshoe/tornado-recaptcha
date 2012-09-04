from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open('README.rst').read()


version = '0.1'

install_requires = [
    'tornado>=2.2',
]

setup(name='tornado_recaptcha',
    version=version,
    description="Client for talking to ReCaptcha using Tornado's " \
        "async HTTPClient",
    long_description=README,
    author='Chris Schomaker',
    author_email='',
    url='https://github.com/cshoe/tornado-recaptcha',
    license=open('LICENSE').read(),
    packages=['tornado_recaptcha'],
    include_package_data=True,
    install_requires=install_requires,
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    )
)

