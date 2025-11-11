#!/bin/bash
# Upload all 48 pay files for 6 umbrella companies (8 files each)

cd /Users/gianlucaformica/Projects/contractor-pay-tracker/InputData

count=0
total=48

echo "=================================="
echo "Uploading 48 Pay Files"
echo "6 umbrella companies × 8 files each"
echo "=================================="
echo ""

for file in *.xlsx; do
    count=$((count + 1))
    echo "[$count/$total] Uploading: $file"

    result=$(curl -s -X POST http://localhost:5557/api/upload \
        -F "file=@$file" \
        -H "Accept: application/json" 2>&1)

    # Check if upload succeeded
    if echo "$result" | grep -q "error"; then
        echo "  ❌ FAILED: $(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null || echo "Upload error")"
    else
        file_id=$(echo "$result" | python3 -c "import sys, json; print(json.load(sys.stdin).get('file_id', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "  ✅ SUCCESS - File ID: $file_id"
    fi

    sleep 1
done

echo ""
echo "=================================="
echo "✅ Upload Complete: $count/$total files"
echo "=================================="
