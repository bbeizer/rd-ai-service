#!/bin/bash

# Uncomment previously commented #print() statements (skip venv/)
echo "🟢 Uncommenting #print() statements..."

for file in $(find . -path ./venv -prune -o -name "*.py" -print); do
    echo "Editing $file..."
    sed -i '' -E 's/^([[:space:]]*)#print\(/\1print(/' "$file"
done

echo "✅ All #prints uncommented (venv/ skipped)."
