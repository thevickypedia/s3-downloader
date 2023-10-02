**Versions Supported**

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Language Stats**

![Language count](https://img.shields.io/github/languages/count/thevickypedia/s3-downloader)
![Code coverage](https://img.shields.io/github/languages/top/thevickypedia/s3-downloader)

**Repo Stats**

[![GitHub](https://img.shields.io/github/license/thevickypedia/s3-downloader)](https://github.com/thevickypedia/s3-downloader/blob/main/LICENSE)
[![GitHub repo size](https://img.shields.io/github/repo-size/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub code size](https://img.shields.io/github/languages/code-size/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)

**Activity**

[![GitHub Repo created](https://img.shields.io/date/1618966420)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/s3-downloader)](https://api.github.com/repos/thevickypedia/s3-downloader)

**Build Status**

[![pypi-publish](https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml/badge.svg)](https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml)
[![pages-build-deployment](https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment)

# S3 Download
Python module to download all the objects in an S3 bucket.

### Installation
```shell
pip install s3-downloader
```

### Usage

##### Download objects in parallel
```python
import s3

if __name__ == '__main__':
    wrapper = s3.Downloader(bucket_name='BUCKET_NAME')
    wrapper.run_in_parallel(threads=10)  # Defaults to 5
```

##### Download objects in sequence
```python
import s3

if __name__ == '__main__':
    wrapper = s3.Downloader(bucket_name='BUCKET_NAME')
    wrapper.run()
```

### Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and 
[`isort`](https://pycqa.github.io/isort/)

### Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/s3-downloader/](https://pypi.org/project/s3-downloader/)

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License](https://github.com/thevickypedia/s3-downloader/blob/main/LICENSE)
