#!/bin/bash
# Batch download papers via DOI from Sci-Hub
# Usage: bash download_papers.sh

DOI_FILE="paper/doi_list.txt"
OUT_DIR="paper"
LOG_FILE="paper/download_log.txt"
FAILED_FILE="paper/failed_dois.txt"

> "$LOG_FILE"
> "$FAILED_FILE"

TOTAL=$(wc -l < "$DOI_FILE")
COUNT=0
SUCCESS=0
FAILED=0

echo "Starting download of $TOTAL papers..."
echo "========================================"

while IFS= read -r doi; do
    [ -z "$doi" ] && continue
    COUNT=$((COUNT + 1))

    # Create safe filename from DOI
    SAFE_NAME=$(echo "$doi" | sed 's/[\/:]/_/g')
    PDF_PATH="$OUT_DIR/${SAFE_NAME}.pdf"

    # Skip if already downloaded
    if [ -f "$PDF_PATH" ] && [ -s "$PDF_PATH" ]; then
        echo "[$COUNT/$TOTAL] SKIP (exists): $doi"
        SUCCESS=$((SUCCESS + 1))
        continue
    fi

    echo "[$COUNT/$TOTAL] Downloading: $doi"

    # Try multiple Sci-Hub mirrors
    DOWNLOADED=false
    for BASE_URL in "https://sci-hub.se" "https://sci-hub.st" "https://sci-hub.ru"; do
        # Step 1: Get the actual PDF URL from Sci-Hub
        RESPONSE=$(curl -s -L --max-time 30 -H "User-Agent: Mozilla/5.0" "${BASE_URL}/${doi}" 2>/dev/null)

        # Extract PDF URL from Sci-Hub response
        PDF_URL=$(echo "$RESPONSE" | grep -oP '(?<=location.href=.)[^"]+' | head -1)
        if [ -z "$PDF_URL" ]; then
            PDF_URL=$(echo "$RESPONSE" | grep -oP '(?<=src=.)[^"]*\.pdf[^"]*' | head -1)
        fi
        if [ -z "$PDF_URL" ]; then
            PDF_URL=$(echo "$RESPONSE" | grep -oP 'https?://[^"]+\.pdf[^"]*' | head -1)
        fi

        if [ -n "$PDF_URL" ]; then
            # Fix URL if it starts with //
            if [[ "$PDF_URL" == //* ]]; then
                PDF_URL="https:${PDF_URL}"
            fi

            # Download the PDF
            curl -s -L --max-time 60 -o "$PDF_PATH" -H "User-Agent: Mozilla/5.0" "$PDF_URL" 2>/dev/null

            # Verify download
            if [ -f "$PDF_PATH" ] && [ -s "$PDF_PATH" ]; then
                FILE_SIZE=$(stat -c%s "$PDF_PATH" 2>/dev/null || echo 0)
                if [ "$FILE_SIZE" -gt 10000 ]; then  # >10KB, likely a valid PDF
                    echo "  -> SUCCESS ($(numfmt --to=iec $FILE_SIZE 2>/dev/null || echo ${FILE_SIZE}B))"
                    echo "OK: $doi -> $PDF_PATH" >> "$LOG_FILE"
                    SUCCESS=$((SUCCESS + 1))
                    DOWNLOADED=true
                    break
                else
                    rm -f "$PDF_PATH"
                fi
            fi
        fi
    done

    if [ "$DOWNLOADED" = false ]; then
        echo "  -> FAILED"
        echo "FAILED: $doi" >> "$LOG_FILE"
        echo "$doi" >> "$FAILED_FILE"
        FAILED=$((FAILED + 1))
    fi

    # Small delay to avoid rate limiting
    sleep 1

done < "$DOI_FILE"

echo "========================================"
echo "Download complete!"
echo "Total: $TOTAL | Success: $SUCCESS | Failed: $FAILED"
echo "Log: $LOG_FILE"
echo "Failed list: $FAILED_FILE"
