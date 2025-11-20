import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# The base URL for the STAC API
BASE_URL = "https://montandon-eoapi-stage.ifrc.org/stac"

def count_items_manually(session, collection_id):
    """
    Last resort: Manually page through all items in a collection and count them.
    This is slow and should be avoided if possible.
    """
    print(f"    -> WARNING: Starting manual count for {collection_id}. This may be very slow.")
    item_count = 0
    url = f"{BASE_URL}/collections/{collection_id}/items?limit=250"
    
    while url:
        try:
            response = session.get(url, timeout=90)
            response.raise_for_status()
            data = response.json()
            
            features = data.get("features", [])
            item_count += len(features)
            
            # Find the URL for the next page
            url = next((link.get("href") for link in data.get("links", []) if link.get("rel") == "next"), None)
            
            # Provide some feedback during long counts
            if item_count > 0 and item_count % 5000 == 0:
                print(f"    -> {collection_id} manual count at {item_count}...")

        except requests.exceptions.RequestException as e:
            print(f"    -> ERROR during manual count for {collection_id}: {e}")
            return "Error during manual count"
            
    print(f"    -> Finished manual count for {collection_id}: {item_count} items.")
    return item_count

def fetch_collection_count(session, collection_id):
    """
    Fetches the metadata for a single collection and returns its item count.
    It tries three methods in order of preference:
    1. Check the collection's summary for 'monty:count'.
    2. If not found, query the /items endpoint with limit=1 to get 'numberMatched'.
    3. If still not found, manually page through all items and count them.
    """
    collection_url = f"{BASE_URL}/collections/{collection_id}"
    try:
        # Method 1: Check the main collection metadata first
        response = session.get(collection_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        item_count = data.get("summaries", {}).get("monty:count")
        if item_count is not None:
            print(f"  -> Fetched {collection_id} (from summary): {item_count} items")
            return {"collection_id": collection_id, "total_events": item_count}

        # Method 2: If summary count is missing, try querying the items endpoint
        print(f"  -> No summary for {collection_id}. Querying items endpoint...")
        items_url = f"{BASE_URL}/collections/{collection_id}/items?limit=1"
        response = session.get(items_url, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "numberMatched" in data:
            item_count = data["numberMatched"]
            print(f"  -> Fetched {collection_id} (from items): {item_count} items")
            return {"collection_id": collection_id, "total_events": item_count}
        
        # Method 3: Manually count if all else fails
        manual_count = count_items_manually(session, collection_id)
        return {"collection_id": collection_id, "total_events": manual_count}

    except requests.exceptions.RequestException as e:
        print(f"  -> ERROR fetching {collection_id}: {e}")
        return {"collection_id": collection_id, "total_events": "Error"}

def get_all_collections(session):
    """Retrieves a list of all collection IDs from the STAC API."""
    url = f"{BASE_URL}/collections"
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Extract the ID for each collection
        return [collection["id"] for collection in data.get("collections", [])]
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not fetch the list of collections. {e}")
        return []

def main():
    """
    Main function to orchestrate fetching all collections and their counts,
    then printing them in a formatted table.
    """
    print("Fetching list of all collections...")
    with requests.Session() as session:
        collection_ids = get_all_collections(session)
        
        if not collection_ids:
            print("No collections found or could not connect. Exiting.")
            return

        print(f"Found {len(collection_ids)} collections. Fetching counts for each...")
        
        results = []
        # Use a ThreadPoolExecutor to fetch counts in parallel for better performance
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_id = {executor.submit(fetch_collection_count, session, cid): cid for cid in collection_ids}
            for future in as_completed(future_to_id):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as exc:
                    collection_id = future_to_id[future]
                    print(f"  -> An exception occurred for {collection_id}: {exc}")
                    results.append({"collection_id": collection_id, "total_events": "Exception"})

    if not results:
        print("\nCould not retrieve counts for any collection.")
        return

    # Sort results alphabetically by collection ID
    results.sort(key=lambda x: x["collection_id"])

    # Use pandas to print a nicely formatted table
    df = pd.DataFrame(results)
    df.set_index("collection_id", inplace=True)
    
    print("\n\n--- Total Events per Collection ---")
    print(df.to_string())
    print("-----------------------------------\n")


if __name__ == "__main__":
    main()
