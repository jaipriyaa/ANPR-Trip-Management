#!/usr/bin/env bash
# Automated Jetson TensorRT Engine Generator Script
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
bash "$SCRIPT_DIR/generate_engine.sh"
