import os

from setuptools import setup

from version import version_info

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Information Technology',
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.9',
    'Topic :: Internet :: File Transfer Protocol (FTP)'
]


def read(name: str) -> str:
    """https://pythonhosted.org/an_example_pypi_project/setuptools.html#setting-up-setup-py - reference."""
    return open(os.path.join(os.path.dirname(__file__), name)).read()


setup(
    name='s3-downloader',
    version='.'.join(str(c) for c in version_info),
    description='Python module to download all the objects in an S3 bucket.',
    long_description=read('README.md') + '\n\n' + read('CHANGELOG'),
    long_description_content_type='text/markdown',
    url='https://github.com/thevickypedia/s3-download',
    author='Vignesh Sivanandha Rao',
    author_email='svignesh1793@gmail.com',
    License='MIT',
    classifiers=classifiers,
    keywords='s3',
    packages=['.s3'],
    python_requires=">=3.8",
    include_package_data=True,
    install_requires=read(name='requirements.txt').splitlines(),
    project_urls={
        'Docs': 'https://thevickypedia.github.io/s3-download',
        'Bug Tracker': 'https://github.com/thevickypedia/s3-download/issues'
    }
)
