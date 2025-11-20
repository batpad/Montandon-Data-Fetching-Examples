#code to get event counts by year for all event collections
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from datetime import datetime

# --- Configuration ---
BASE_URL = "https://montandon-eoapi-stage.ifrc.org/stac"
OUTPUT_FILE = "event_counts_by_year.xlsx"
MAX_WORKERS = 10  # Number of parallel requests

def get_event_collections(session):
    """Retrieves a list of all collection IDs that have 'event' in their roles."""
    print("Fetching list of all collections...")
    url = f"{BASE_URL}/collections"
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Filter for collections with 'event' in their roles field
        event_collections = [
            collection["id"] for collection in data.get("collections", [])
            if "event" in collection.get("roles", [])
        ]
        print(f"Found {len(event_collections)} event collections: {event_collections}")
        return event_collections
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not fetch the list of collections. {e}")
        return []

def generate_time_bins():
    """
    Generates time bins with 100-year gaps until 1800,
    then 50-year gaps until today.
    """
    bins = []
    # 100-year intervals from 1600 to 1799
    for year in range(1600, 1800, 100):
        start_year = year
        end_year = year + 99
        bins.append({"label": f"{start_year}-{end_year}", "start": start_year, "end": end_year})

    # 50-year intervals from 1800 to today
    current_year = 1800
    end_year_limit = datetime.now().year
    while current_year <= end_year_limit:
        start_year = current_year
        end_year = current_year + 49
        if end_year > end_year_limit:
            end_year = end_year_limit
        bins.append({"label": f"{start_year}-{end_year}", "start": start_year, "end": end_year})
        current_year += 50
        
    return bins

def fetch_count_for_bin(session, collection_id, time_bin):
    """
    Fetches the count of items for a specific collection and time bin
    by using the 'numberMatched' field from a limit=1 query.
    """
    bin_label = time_bin['label']
    start_dt = f"{time_bin['start']}-01-01T00:00:00Z"
    end_dt = f"{time_bin['end']}-12-31T23:59:59Z"
    datetime_range = f"{start_dt}/{end_dt}"
    
    print(f"  -> Querying: {collection_id} for period {bin_label}")
    
    # We only need the count, so we query with limit=1 to get 'numberMatched'
    url = f"{BASE_URL}/collections/{collection_id}/items?limit=1&datetime={datetime_range}"
    
    try:
        response = session.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # 'numberMatched' gives the total count for the query without fetching all items
        count = data.get("numberMatched")

        # If numberMatched is not present, some collections might not support it for date ranges
        if count is None:
             print(f"  -> WARNING: 'numberMatched' not found for {collection_id} in {bin_label}. Count is 0.")
             count = 0
        
        print(f"  -> Completed: {collection_id} for {bin_label} ({count} items)")
        return {
            "collection": collection_id,
            "time_period": bin_label,
            "event_count": count
        }

    except requests.exceptions.RequestException as e:
        print(f"  -> ERROR on {collection_id} for {bin_label}: {e}")
        return {
            "collection": collection_id,
            "time_period": bin_label,
            "event_count": "Error"
        }

def main():
    """
    Main function to orchestrate fetching counts for all event collections
    across all time bins and saving the results to Excel.
    """
    with requests.Session() as session:
        event_collections = get_event_collections(session)
        if not event_collections:
            return
            
        time_bins = generate_time_bins()
        print(f"Generated {len(time_bins)} time bins to process.\n")

        tasks = []
        for collection_id in event_collections:
            for bin_info in time_bins:
                tasks.append((collection_id, bin_info))

        all_results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_task = {
                executor.submit(fetch_count_for_bin, session, coll_id, t_bin): (coll_id, t_bin['label'])
                for coll_id, t_bin in tasks
            }

            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    # Store result even if count is 0 to ensure all periods are represented
                    if result:
                        all_results.append(result)
                except Exception as exc:
                    task_id = future_to_task[future]
                    print(f"A task {task_id} generated an exception: {exc}")

    if not all_results:
        print("\nNo event data was found for any collection in the specified time periods.")
        return

    df_long = pd.DataFrame(all_results)
    
    # Filter out any rows where counting resulted in an error
    df_long = df_long[df_long['event_count'] != 'Error']
    
    print(f"\nProcessing complete. Writing data to Excel file: {OUTPUT_FILE}")

    with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
        collections = sorted(df_long['collection'].unique())
        all_time_periods = sorted(df_long['time_period'].unique())
        
        for collection in collections:
            print(f"  -> Creating sheet for {collection}")
            df_collection = df_long[df_long['collection'] == collection]
            
            # Pivot the table to get the desired wide format
            df_pivot = df_collection.pivot_table(
                index='collection',
                columns='time_period',
                values='event_count'
            ).fillna(0)
            
            # Ensure all time periods are present as columns in the correct order
            df_pivot = df_pivot.reindex(columns=all_time_periods, fill_value=0)
            
            df_pivot.to_excel(writer, sheet_name=collection, index=False)

    print(f"\nSuccessfully created Excel file with {len(collections)} sheets.")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Total execution time: {end_time - start_time:.2f} seconds")
