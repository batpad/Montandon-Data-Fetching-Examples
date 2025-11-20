# Montandon STAC API - CQL2 Filter Troubleshooting

## Issue: CQL2 Filter Not Returning Results

### Working Code vs Non-Working Code

#### ✅ Working Code
```python
spain_flood_late_oct_filter = {
    "op": "and",
    "args": [
        {
            "op": "a_contains",
            "args": [
                {"property": "monty:country_codes"},
                "ESP"
            ]
        },
        {
            "op": "a_overlaps",
            "args": [
                {"property": "monty:hazard_codes"},
                ["nat-hyd-flo-flo", "FL"]
            ]
        },
        {
            "op": "t_intersects",
            "args": [
                {"property": "datetime"},
                {"interval": ["2024-10-20T00:00:00Z", "2024-11-05T23:59:59Z"]}
            ]
        }
    ]
}

spain_flood_late_oct_events = stac_search(
    collections=["gdacs-events", "emdat-events", "glide-events", "reference-events"],
    filter_body=spain_flood_late_oct_filter,
    filter_lang="cql2-json",
    limit=100
)
```

#### ❌ Non-Working Code
```python
filter_dict = {
    "op": "and",
    "args": [
        {
            "op": "a_contains",
            "args": [
                {"property": "monty:country_codes"},
                "ESP"
            ]
        },
        {
            "op": "a_overlaps",
            "args": [
                {"property": "monty:hazard_codes"},
                ["MH0600", "nat-hyd-flo-flo", "FL"]  # ❌ PROBLEM 1: "MH0600" doesn't exist
            ]
        },
        {
            "op": "t_intersects",
            "args": [
                {"property": "datetime"},
                {"interval": ["2024-10-01T00:00:00Z", "2024-11-05T23:59:59Z"]}
            ]
        },
        {
            "op": "in",  # ❌ PROBLEM 2: Incorrect syntax
            "args": [
                "event",
                {"property": "roles"}
            ]
        }
    ]
}

events = stac_search(
    collections=["glide-events", "gdacs-events", "emdat-events", "reference-events"],
    filter_body=filter_dict,
    filter_lang="cql2-json",
    limit=100
)
```

---

## Problems Identified

### Problem 1: Invalid Hazard Code `"MH0600"`

**Issue**: The hazard code `"MH0600"` does not exist in the Montandon data.

**Solution**: Remove `"MH0600"` from the hazard codes array.

**Correct hazard codes for floods:**
```python
["nat-hyd-flo-flo", "FL"]
```

---

### Problem 2: Incorrect `in` Operator Syntax

**Issue**: The role filter is using backwards syntax:
```python
{
    "op": "in",
    "args": [
        "event",
        {"property": "roles"}
    ]
}
```

This checks if the literal string `"event"` is in the `roles` property, which is incorrect.

**Correct Syntax** (if needed):
```python
{
    "op": "in",
    "args": [
        {"property": "roles"},
        ["event"]  # Check if roles array contains "event"
    ]
}
```

**Better Solution**: Remove this filter entirely since you're already searching event collections (`gdacs-events`, `emdat-events`, etc.).

---

## Fixed Code

```python
# Define CQL2 filter for flood events in Spain
filter_dict = {
    "op": "and",
    "args": [
        {
            "op": "a_contains",
            "args": [
                {"property": "monty:country_codes"},
                "ESP"
            ]
        },
        {
            "op": "a_overlaps",
            "args": [
                {"property": "monty:hazard_codes"},
                ["nat-hyd-flo-flo", "FL"]  # ✅ Removed "MH0600"
            ]
        },
        {
            "op": "t_intersects",
            "args": [
                {"property": "datetime"},
                {"interval": ["2024-10-01T00:00:00Z", "2024-11-05T23:59:59Z"]}
            ]
        }
        # ✅ Removed the problematic "roles" filter
    ]
}

print("🔍 Searching for flood events in Spain (October 1 - November 5, 2024)\n")

# Search with CQL2 filter via POST /search
events = stac_search(
    collections=[
        "glide-events", "gdacs-events", "emdat-events", "reference-events"
    ],
    filter_body=filter_dict,
    filter_lang="cql2-json",
    limit=100
)

print(f"✅ Found {len(events)} related flood events in Spain\n")

if events:
    print("📋 Event Details:")
    for event in events:
        print(f"\n  • Event ID: {event.id}")
        print(f"    Collection: {event.collection_id}")
        print(f"    Title: {event.properties.get('title', 'N/A')}")
        print(f"    Correlation ID: {event.properties.get('monty:corr_id', 'N/A')}")
        print(f"    Date: {event.properties.get('datetime')}")
        print(f"    Hazard Codes: {event.properties.get('monty:hazard_codes', 'N/A')}")
else:
    print("ℹ️ No events found matching the criteria.")
```

---

## Summary of Changes

| Change | Reason |
|--------|--------|
| ✅ Removed `"MH0600"` from hazard codes | This hazard code doesn't exist in the data |
| ✅ Removed `roles` filter | Incorrect syntax and unnecessary since searching event collections |
| ✅ Now matches working code structure | Uses only valid filters that exist in the data |

---

## Key Learnings

1. **Always verify hazard codes** - Use only codes that exist in your data sources
2. **CQL2 `in` operator syntax** - Correct format is `property IN array`, not `value IN property`
3. **Avoid redundant filters** - If searching event collections, no need to filter by `roles = "event"`
4. **Test filters incrementally** - Start with simple filters and add complexity gradually

---

## Valid Flood Hazard Codes

Based on the working code, the valid flood hazard codes are:
- `"nat-hyd-flo-flo"` - Natural hydrological flood
- `"FL"` - Flood (short code)

If you need additional hazard codes, verify them against the API data first using diagnostic queries.
