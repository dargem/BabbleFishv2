#!/bin/bash

# Cleanup script to remove old test files and structure

echo "Cleaning up old test structure..."

# Remove old test directory
if [ -d "src/nodes_tests" ]; then
    echo "Removing old test directory: src/nodes_tests"
    rm -rf src/nodes_tests
fi

# Remove any old test files in root
for file in test_*.py *_test.py; do
    if [ -f "$file" ]; then
        echo "Removing old test file: $file"
        rm "$file"
    fi
done

echo "Cleanup complete!"
