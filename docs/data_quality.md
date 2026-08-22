NEXPULSE — ORDERS BRONZE DATA QUALITY VALIDATION
======================================================================

Validation Layer:        Bronze
Data Source:             nexpulse_spark
Data Asset:              bronze_orders
Batch Definition:        orders_batch
Expectation Suite:       orders_suite
Validation Definition:   orders_validation
Great Expectations:      1.21.0

Bronze Row Count:        60
Overall Validation:      FAILED
Total Expectations:      6

----------------------------------------------------------------------
EXPECTATION RESULTS
----------------------------------------------------------------------

1. expect_column_values_to_not_be_null
   Status: PASS

2. expect_column_values_to_not_be_null
   Status: PASS

3. expect_column_values_to_not_be_null
   Status: FAIL

4. expect_column_values_to_be_between
   Status: FAIL

5. expect_column_values_to_be_between
   Status: PASS

6. expect_column_values_to_be_in_set
   Status: FAIL

----------------------------------------------------------------------
INTERPRETATION
----------------------------------------------------------------------

The Bronze Orders dataset contains 60 records.

The Great Expectations validation intentionally identified data-quality
violations in the raw Bronze data. Therefore, an overall validation
status of FAILED at the Bronze layer is expected and does not indicate
a pipeline failure.

The failed expectations identify records containing invalid or
unexpected values. These records are handled by the downstream Silver
transformation and validation layer.

The Silver Orders pipeline performs:

- Data type casting and normalization
- Row-level validation
- Invalid-record detection
- Quarantine of invalid records
- Event-level deduplication using event_id
- Bronze-to-Silver reconciliation

This separation preserves the original Bronze data while ensuring that
only validated records are promoted to Silver.

----------------------------------------------------------------------
BRONZE → SILVER DESIGN
----------------------------------------------------------------------

Bronze:
    Raw event data
          ↓
    Great Expectations validation
          ↓
Silver:
    Type casting
    Normalization
    Row-level validation
    Quarantine
    Deduplication
    Reconciliation
          ↓
    Valid Silver Orders

A failed Bronze expectation does not mean that the pipeline should stop.
Bronze is intentionally treated as the raw landing layer, while Silver
is responsible for enforcing data-quality rules before trusted data is
made available to downstream processing.

----------------------------------------------------------------------
VALIDATION STATUS
----------------------------------------------------------------------

Bronze validation completed successfully from a pipeline-execution
perspective.

Data-quality violations were detected as expected and are handled by
the Silver validation and quarantine process.

STATUS: BRONZE ORDERS DATA QUALITY VALIDATION COMPLETED


## Schema Evolution Policy

Automatically merged (no review needed):
- New optional columns added to a producer's event shape (e.g. a new `discount_code` field)

Requires manual review before deploying:
- Any change to an existing column's data type
- Removal of a column relied upon by Silver validation or Gold joins
- Renaming an existing column (Delta's schema merge treats this as add + drop, not a rename)

Enforcement: `mergeSchema=true` is set on Silver writes only. Bronze writes stay
schema-strict, so an unexpected producer change is visible at the earliest
possible layer rather than silently absorbed downstream.

## Step 7 — Bronze-to-Silver Reconciliation

### Orders

Bronze events:          60
Valid Silver events:    52
Quarantined events:     7
Duplicates removed:     1
Reconciled total:       60

Reconciliation:

52 + 7 + 1 = 60

Status: PASSED

### Payments

Bronze events:          60
Valid Silver events:    59
Quarantined events:     0
Duplicates removed:     1
Reconciled total:       60

Reconciliation:

59 + 0 + 1 = 60

Status: PASSED

### Inventory

Inventory uses a different reconciliation model because Silver Inventory
is a current-state table maintained using Delta MERGE.

Bronze inventory events are collapsed to one current state per:

product_id + warehouse_id

Actual run:

Bronze events:          60
Valid before dedup:     59
State rows removed:     4
Final inventory states: 55
Quarantined events:     1
Reconciled total:       60

Reconciliation:

55 + 1 + 4 = 60

The inventory Silver row count is therefore intentionally lower than the
Bronze row count. This is expected because multiple inventory events for
the same product/warehouse pair are collapsed into a single current state.