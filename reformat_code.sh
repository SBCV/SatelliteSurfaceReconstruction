#!/bin/bash
# Go to the directory where the script is located
cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
black --line-length 79 ssr
# black --line-length 79 docs/sphinx/source/conf.py