#!/bin/bash
# Go to the directory where the script is located
cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd
REQUIRED_VERSION="24.3.0"
black --required-version ${REQUIRED_VERSION} --line-length 79 ssr
black --required-version ${REQUIRED_VERSION} --line-length 79 dataset_preparation
