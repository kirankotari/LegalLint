# LegalLint

LegalLint is a license compliance linter for all programming languages, with current support for Python. It ensures that projects adhere to specified licensing policies, allowing users to enforce allowed licenses and trigger errors for disallowed licenses.

## Features
- Detects license types for Python libraries.
- Customizable allowed and disallowed licenses.
- Skips specific libraries from license checking.
- TOML-based configuration for flexible settings.

## Installation
To install LegalLint:
```bash
pip install legallint
```

## Usage

### CLI
```bash
$ legallint -l python
```

### Example Configuration (pyproject.toml)
```toml
[licenses]
allowed = ["MIT", "Apache-2.0", "BSD-3-Clause"]
trigger_error = ["GPL-3.0", "AGPL-3.0", "Proprietary", "Unknown"]

# Libraries to skip
skip_libraries = ["example-lib1", "example-lib2"]
```

```bash
$ legallint -l python
---------------
   PYTHON
---------------
✔     toml                 MIT
✔     pluggy               MIT
✔     iniconfig            MIT
✔     packaging            Apache; BSD
✔     idna                 BSD
✔     requests             Apache-2.0
✔     urllib3              MIT
‼     certifi              MPL-2.0
✔     pytest               MIT
✔     charset-normalizer   MIT
```

### legallint commands
```bash
$ legallint -h
usage: legallint [-h] [--verbose] [-v] [-l {python,node} [{python,node} ...]] [-u] [--license]

LegalLint is a cross-platform tool designed to ensure license compliance across multiple programming languages by analyzing dependencies and enforcing predefined license policies. LegalLint helps maintain legal standards by scanning the project’s dependencies and ensuring that only approved licenses (e.g., MIT, Apache 2.0) are used.

options:
  -h, --help            show this help message and exit
  --verbose             Enable verbose mode
  -v, --version         show program's version number and exit
  -l {python,node} [{python,node} ...], --lang {python,node} [{python,node} ...]
                        Select one or more languages from: python
  -u, --update          Enable update mode
  --license             Enable license mode
```

## License
LegalLint is distributed under the Apache-2.0 License. See `LICENSE` for more information.