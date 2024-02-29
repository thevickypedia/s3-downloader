**Versions Supported**

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Language Stats**

![Language count](https://img.shields.io/github/languages/count/thevickypedia/s3-downloader)
![Code coverage](https://img.shields.io/github/languages/top/thevickypedia/s3-downloader)

**Repo Stats**

[![GitHub](https://img.shields.io/github/license/thevickypedia/s3-downloader)][license]
[![GitHub repo size](https://img.shields.io/github/repo-size/thevickypedia/s3-downloader)][repo]
[![GitHub code size](https://img.shields.io/github/languages/code-size/thevickypedia/s3-downloader)][repo]

**Activity**

[![GitHub Repo created](https://img.shields.io/date/1618966420)][repo]
[![GitHub commit activity](https://img.shields.io/github/commit-activity/y/thevickypedia/s3-downloader)][repo]
[![GitHub last commit](https://img.shields.io/github/last-commit/thevickypedia/s3-downloader)][repo]

**Build Status**

[![pypi-publish][gha-pypi-badge]][gha-pypi]
[![pages-build-deployment][gha-pages-badge]][gha-pages]

# S3 Download
Python module to download objects in an S3 bucket.

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

## [Release Notes][release-notes]
**Requirement**
```shell
python -m pip install gitverse
```

**Usage**
```shell
gitverse-release reverse -f release_notes.rst -t 'Release Notes'
```

## Linting
`pre-commit` will ensure linting, run pytest, generate runbook & release notes, and validate hyperlinks in ALL
markdown files (including Wiki pages)

**Requirement**
```shell
pip install sphinx==5.1.1 pre-commit recommonmark
```

**Usage**
```shell
pre-commit run --all-files
```

### Pypi Package
[![pypi-module][pypi-logo]][pypi-tutorials]

[https://pypi.org/project/s3-downloader/][pypi]

## License & copyright

&copy; Vignesh Rao

Licensed under the [MIT License][license]

[license]: https://github.com/thevickypedia/s3-downloader/blob/main/LICENSE
[release-notes]: https://github.com/thevickypedia/s3-downloader/blob/main/release_notes.rst
[pypi]: https://pypi.org/project/s3-downloader/
[pypi-tutorials]: https://packaging.python.org/tutorials/packaging-projects/
[pypi-logo]: https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg
[repo]: https://api.github.com/repos/thevickypedia/s3-downloader
[gha-pages-badge]: https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment/badge.svg
[gha-pypi-badge]: https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml/badge.svg
[gha-pages]: https://github.com/thevickypedia/s3-downloader/actions/workflows/pages/pages-build-deployment
[gha-pypi]: https://github.com/thevickypedia/s3-downloader/actions/workflows/python-publish.yml
