# Optimized parallel fetching for usgs-events using datetime partitioning

import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import time
import json
import os
from datetime import datetime, timedelta

# Configuration
COLLECTION_ID = "usgs-events"
BASE_URL = "https://montandon-eoapi-stage.ifrc.org/stac/collections"
ERROR_FILE = "event_count_errors_usgs_optimized.json"
OUTPUT_FILE = "event_counts_by_country_usgs_optimized.csv"
PAGE_SIZE = 500  # Max items per page (use 10,000 if API allows)
MAX_WORKERS = 10  # Number of parallel datetime ranges (safe for 12-thread CPU)
YEARS_PER_CHUNK = 5  # Split data into 5-year chunks for parallel processing
START_YEAR = 1934  # Earliest USGS event recorded

def write_error_entry(error_entry):
    """Append a single error as a JSON string to the error file."""
    with open(ERROR_FILE, "a", encoding="utf-8") as ef:
        ef.write(json.dumps(error_entry, ensure_ascii=False) + "\n")

def get_collection_temporal_extent():
    """Get the temporal range for USGS collection."""
    start_date = f"{START_YEAR}-01-01T00:00:00Z"
    end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    print(f"Collection temporal extent: {start_date} to {end_date}")
    print(f"Note: Using {START_YEAR} as start year (earliest USGS event)\n")
    return start_date, end_date

def generate_time_chunks(start_date_str, end_date_str, years_per_chunk):
    """Generate time range chunks for parallel processing."""
    start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
    
    chunks = []
    current_start = start_date
    
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=365 * years_per_chunk), end_date)
        chunks.append({
            "start": current_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "label": f"{current_start.year}-{current_end.year}"
        })
        current_start = current_end
    
    return chunks

def fetch_time_chunk(session, collection_id, time_chunk):
    """Fetch all items for a specific time range and count country codes."""
    chunk_label = time_chunk["label"]
    datetime_range = f"{time_chunk['start']}/{time_chunk['end']}"
    
    print(f"  → Starting time chunk: {chunk_label}")
    
    chunk_counter = Counter()
    url = f"{BASE_URL}/{collection_id}/items?limit={PAGE_SIZE}&datetime={datetime_range}&fields=properties.monty:country_codes"
    
    page_count = 0
    total_items = 0
    max_retries = 3
    
    while url:
        page_count += 1
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=90)
                response.raise_for_status()
                data = response.json()
                
                features = data.get("features", [])
                total_items += len(features)
                
                # Count country codes
                for feature in features:
                    codes = feature.get("properties", {}).get("monty:country_codes", [])
                    chunk_counter.update(codes)
                
                # Find next page URL
                url = next((link.get("href") for link in data.get("links", []) if link.get("rel") == "next"), None)
                break  # Success, exit retry loop
                
            except requests.exceptions.RequestException as ex:
                wait_time = 2 ** attempt
                print(f"    ⚠ {chunk_label} page {page_count}, attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                
                if attempt == max_retries - 1:
                    error_entry = {
                        "collection": collection_id,
                        "time_chunk": chunk_label,
                        "page": page_count,
                        "reason": f"Failed after {max_retries} attempts: {str(ex)}"
                    }
                    write_error_entry(error_entry)
                    print(f"    ✗ {chunk_label} failed after {max_retries} attempts")
                    return chunk_counter, error_entry
    
    print(f"  ✓ Completed {chunk_label}: {total_items:,} items in {page_count} pages")
    return chunk_counter, None

def fetch_country_counts_parallel(collection_id):
    """
    Fetches all items using parallel time-based partitioning and aggregates country counts.
    """
    print(f"\n=== Starting optimized time-partitioned fetch for {collection_id} ===\n")
    
    with requests.Session() as session:
        # Step 1: Get temporal extent
        start_date, end_date = get_collection_temporal_extent()
        
        # Step 2: Generate time chunks
        time_chunks = generate_time_chunks(start_date, end_date, YEARS_PER_CHUNK)
        print(f"Generated {len(time_chunks)} time chunks ({YEARS_PER_CHUNK}-year periods)")
        print(f"Using {MAX_WORKERS} parallel workers\n")
        
        # Step 3: Fetch all chunks in parallel
        combined_counter = Counter()
        errors = []
        completed_chunks = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # Submit all chunk fetch tasks
            future_to_chunk = {
                executor.submit(fetch_time_chunk, session, collection_id, chunk): chunk
                for chunk in time_chunks
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_chunk):
                chunk = future_to_chunk[future]
                try:
                    chunk_counter, error = future.result()
                    combined_counter.update(chunk_counter)
                    if error:
                        errors.append(error)
                    
                    completed_chunks += 1
                    progress = completed_chunks / len(time_chunks) * 100
                    print(f"\n  Progress: {completed_chunks}/{len(time_chunks)} chunks completed ({progress:.1f}%)")
                
                except Exception as exc:
                    print(f"  ✗ Chunk {chunk['label']} generated an exception: {exc}")
                    errors.append({
                        "collection": collection_id,
                        "time_chunk": chunk["label"],
                        "reason": str(exc)
                    })
        
        print(f"\n✓ Completed: {completed_chunks}/{len(time_chunks)} time chunks")
        
        # Write errors to file if any
        if errors:
            print(f"⚠ {len(errors)} errors occurred and were logged to {ERROR_FILE}")
        
        return combined_counter

def main():
    start_time = time.time()
    
    # Clear any existing error file before running
    if os.path.exists(ERROR_FILE):
        os.remove(ERROR_FILE)

    # Fetch and count
    country_counts = fetch_country_counts_parallel(COLLECTION_ID)

    # Save to CSV
    if country_counts:
        with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["country_code", "event_count"])
            for country, count in country_counts.most_common():
                writer.writerow([country, count])
        
        print(f"\n✓ Results saved to {OUTPUT_FILE}")
        print(f"  Total unique countries: {len(country_counts)}")
        print(f"  Total events counted: {sum(country_counts.values()):,}")
    else:
        print("\n✗ No data was processed.")

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n⏱ Total execution time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")

if __name__ == "__main__":
    main()
