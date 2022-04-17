**Versions Supported**

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Language Stats**

![Language count](https://img.shields.io/github/languages/count/thevickypedia/s3-downloader)
![Code coverage](https://img.shields.io/github/languages/top/thevickypedia/s3-downloader)

**Repo Stats**

[![GitHub](https://img.shields.io/github/license/thevickypedia/s3-downloader)](https://github.com/thevickypedia/s3-downloader/blob/main/LICENSE)
[![GitHub repo size](https://img.shields.io/github/repo-size/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub code size](https://img.shields.io/github/languages/code-size/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![LOC](https://img.shields.io/tokei/lines/github/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)

**Activity**

[![GitHub Repo created](https://img.shields.io/date/1618966420)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)

**Build Status**

[![pypi-publish](https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml)
[![pages-build-deployment](https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment)

# S3 Download
Python module to download all the objects in an S3 bucket.

### Install from pypi
`pip install s3-downloader`

### Usage

##### Using multi-threading
```python
from s3.dumper import Downloader

if __name__ == '__main__':
    Downloader(bucket_name='MY_BUCKET_NAME').run_in_parallel()
```

##### Without using multi-threading
```python
from s3.dumper import Downloader

if __name__ == '__main__':
    Downloader(bucket_name='MY_BUCKET_NAME').run()
```

### Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and 
[`isort`](https://pycqa.github.io/isort/)

### Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
`pip install --no-cache --upgrade sphinx pre-commit recommonmark`

**Usage**
<br>
`pre-commit run --all-files`

### Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/s3-downloader/](https://pypi.org/project/s3-downloader/)

### Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/main/man/sphinx-autogen.html)

[https://thevickypedia.github.io/s3-downloader/](https://thevickypedia.github.io/s3-downloader/)

## License & copyright

&copy; Vignesh Sivanandha Rao

Licensed under the [MIT License](https://github.com/thevickypedia/s3-downloader/blob/main/LICENSE)
