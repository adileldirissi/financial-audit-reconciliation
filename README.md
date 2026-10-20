# Financial Audit Data Quality & Reconciliation Engine (Python + SQL)

An automated data validation and reconciliation framework developed to ingest raw client financial transactions, audit general ledgers against bank statements, enforce double-entry integrity, and generate certified discrepancy reports for audit and assurance teams.

---

## 🎯 Business Context & Alignment
In external audit and risk assurance (Big 4 statutory assurance standards), data stewards and analysts must verify that client accounting extracts are complete, mathematically consistent, and free of anomalies before feeding downstream analytics. Manual Excel cross-referencing is error-prone and time-consuming. 

This engine automates the primary ingestion gate:
- **Completeness & Schema Checking**: Ensures mandatory fiscal fields (Transaction ID, Date, Account Code, Debit, Credit) exist.
- **Double-Entry Balance Verification**: Asserts that `Total Debits == Total Credits` per journal entry and across fiscal periods.
- **Anomaly & Duplicate Detection**: Flags duplicate invoice references, unexpected negative balances, out-of-period postings, and unmapped account codes.
- **Audit-Ready Reporting**: Generates a structured JSON and Markdown anomaly report for senior auditors with an audit trail and data quality score.

---

## 🏗️ Architecture

```text
[ Raw Client Accounting CSV / SQL ]
                 │
                 ▼
[ Ingestion & Schema Gatekeeper ] (Type enforcement, null checks)
                 │
                 ▼
[ Reconciliation & Audit Rules Engine ]
   ├── Double-entry balancing (Debit = Credit per voucher)
   ├── Duplicate invoice / transaction detection
   ├── Currency and date validity checks
   └── Account mapping verification
                 │
                 ▼
[ Certified Output & Audit Summary ]
   ├── Cleaned Ledger (Parquet / SQLite)
   ├── Discrepancy Log (CSV / JSON)
   └── Executive Audit Memo (Markdown / HTML)
```

---

## 🚀 Quickstart

1. Run the reconciliation script on the sample ledger:
```bash
python3 reconciliation_engine.py --input sample_ledger.csv --output audit_report.md
```

2. Inspect the generated audit discrepancy report `audit_report.md`.
