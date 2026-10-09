# Implementation Plan: Chain-of-Custody Service

## Requirement Summary
1. **Data Loading:** Build a small, working slice of a chain-of-custody service using Python 3.9, FastAPI, and pytest. Load data from provided CSV files into an SQLite database.
2. **Reconciliation View:** Create a visible screen (rendered table/web page) showing for every organization: quantity received, quantity sold, quantity available, and any data problems identified in the seed data along with proposed resolutions.

## Data Analysis
### Seed Data Issues (Data Problems to Surface)
1. **Overselling / Negative Balances:** Organizations that have sold more quantity than they have received (or licensed, in the case of Ginners). 
   * *Resolution*: Flag in the view; block future transactions in a real system.
2. **Expired Licenses:** Transactions (`TXN-0108`) involving organizations (`G-04`) after their license has expired. 
   * *Resolution*: Flag the transaction/organization; prevent processing in a live system.
3. **Invalid Buyers/Sellers:** Transactions (`TXN-0119`) referencing organizations (`X-99`) that do not exist. 
   * *Resolution*: Transaction discarded during import (as per clarification); display a note about it in the data problems summary.
4. **Duplicate Transactions:** Exact row duplicates (`TXN-0117`) which should be merged/deduplicated. 
   * *Resolution*: Deduplicated via PK constraints on import; note this in the summary.
5. **Unit Inconsistencies:** Transactions (`TXN-0114`) in `bales` rather than standard `kg`. 
   * *Resolution*: Converted to `kg` at import (1 bale = 165kg).

## Assumptions / Asks for Clarification
* **Balance Calculation Rules:** 
  * *Ginners*: `Received` is equivalent to their `licensed_volume_kg`.
  * *Traders/Spinners/Fabric Mills*: `Received` is the sum of `quantity` from all `Confirmed` purchase transactions.
  * *Sold*: Sum of `quantity` from all `Confirmed` sale transactions.
  * *Available*: `Received - Sold`.
* **UI Delivery:** We will use FastAPI's built-in `HTMLResponse` to serve a simple HTML page containing the reconciliation table and data problems list, avoiding extra templating dependencies like Jinja2.

## Edge Cases to Handle
* Handling `Pending` or `Rejected` transactions: We must exclude these from balance calculations so we don't artificially inflate Received or Sold quantities.
* Displaying organizations that might not have any transactions but still need to be in the reconciliation view.

## Technical Approach
1. **Backend:** FastAPI for API routing and data fetching.
2. **Database Queries:** Retrieve all organizations and all confirmed transactions. Calculate the balances in Python memory (since it's a small slice) or via SQL aggregations. 
3. **Frontend View:** Return a raw HTML string from a new endpoint (`/reconciliation`). It will use basic inline CSS/HTML tables.

## Implementation Steps
1. Write a data aggregation function in `services.py` that computes Received, Sold, and Available for every organization.
2. Identify negative balances or expired license usage during the aggregation.
3. Build an HTML generator function that formats this data into an easy-to-read table.
4. Create a new endpoint `/reconciliation` in `main.py` that returns the `HTMLResponse`.

## Automation Test Plan
* **Unit Tests for Balances:** Test the aggregation logic using the `/reconciliation` endpoint to ensure HTTP 200 is returned.
* **Content Validation:** Check that the HTML response contains known data like "Saurashtra Ginning Co" and "Data Problems Found".
