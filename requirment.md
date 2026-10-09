Technical Environment:
    Python. 3.9
    FastAPI
    pytest
    prefere standard libraries unless an additinal dependencies provides a clear benifit

Requirments:
Using the two CSV files provided (organisations.csv and transactions.csv), build a small working slice of a chain-of-custody service. Any language, framework and data store you are fastest in is fine. SQLite, Postgres or in-memory are all acceptable.
Required: build both of these
1. Load the data. Import both files into your data store.

The user provides 2 CSV files under data folder
    Inspect the CSV files  and check missing required values, unmatcheted records, duplicates, invalid data types
    Do not sliently discard any invalid records
    Idntify any assumptions, ambiguitties, that still need for clafication

Please update the plan.md file containing, 
Requirment summary 
Data analysis
Assumption/Ask
Edge Cases
Technical approach

Do not implement the plan

1. **Unit Conversion:** How should we handle the `bales` unit in `TXN-0114`? 
1bales = 165kg

2. **Missing Organizations:** For `TXN-0119` referencing the unknown buyer `X-99`, - discard for now
3. **Duplicate Transactions:** Should exact duplicate rows like `TXN-0117` be deduplicated during the import process, or should they be recorded as separate entries (which would require a surrogate primary key instead of `txn_ref`)? - ignore
4. **Expired Licenses:** `TXN-0108` involves `G-04` on `2026-07-18`, which is after their license expired (`2026-06-30`). Should this transaction be flagged, rejected, or allowed during import? - ignore
5. **Licensed Volumes:** Is it correct to assume that `licensed_volume_kg` is only applicable to Ginners and can be safely treated as `null` or `0` for other organization types? - yes
----------------------------
Technical Environment:
    Python. 3.9
    FastAPI
    pytest
    prefere standard libraries unless an additinal dependencies provides a clear benifit

Requirments:
2. A reconciliation view, on screen. For every organisation, show quantity received, quantity sold and quantity available, alongside the data problems you find in the seed data. There are several. Find as many as you can and say what you would do about each.
The view must be something we can look at: a web page, a rendered table, a simple dashboard, whatever you can stand up quickly. It does not need to be pretty. We care about whether someone could look at it and know what to do next.

Please update the plan.md file containing, 
Requirment summary 
Data analysis
Assumption/Ask
Edge Cases
Technical approach
Implementation steps - (dont breack it to smaller task for now)
Automation test plan
