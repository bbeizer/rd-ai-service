#!/bin/bash

# Comment out all print() statements, wherever they appear
echo "🔵 Aggressively commenting out ALL print statements..."

for file in $(find . -name "*.py"); do
    sed -i '' -E 's/print\(/#print(/g' "$file"
done

echo "✅ Done! All prints commented out everywhere."
