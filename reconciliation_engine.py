#!/usr/bin/env python3
"""
Financial Audit Data Quality & Reconciliation Engine
Author: Adil El Idrissi
Target: Audit & Assurance Data Stewardship (e.g. Deloitte Extended Services)
"""

import csv
import argparse
from datetime import datetime
from collections import defaultdict


def run_reconciliation(input_csv: str, output_report: str):
    records = []
    with open(input_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    total_records = len(records)
    vouchers = defaultdict(list)
    invoice_counts = defaultdict(list)
    anomalies = []

    # 1. Parse and group by voucher
    for idx, row in enumerate(records, start=1):
        v_id = row.get("voucher_id", "UNKNOWN")
        vouchers[v_id].append((idx, row))

        inv_ref = row.get("invoice_ref")
        if inv_ref:
            invoice_counts[inv_ref].append((v_id, row.get("date"), row.get("debit"), row.get("credit")))

    # 2. Rule Check: Double-entry balancing (Debit == Credit per voucher)
    balanced_vouchers = 0
    unbalanced_vouchers = 0
    total_debit_all = 0.0
    total_credit_all = 0.0

    for v_id, rows in vouchers.items():
        v_debit = sum(float(r[1]["debit"]) for r in rows)
        v_credit = sum(float(r[1]["credit"]) for r in rows)
        total_debit_all += v_debit
        total_credit_all += v_credit

        diff = abs(v_debit - v_credit)
        if diff > 0.001:
            unbalanced_vouchers += 1
            anomalies.append({
                "severity": "CRITICAL",
                "code": "UNBALANCED_JOURNAL_ENTRY",
                "voucher_id": v_id,
                "message": f"Voucher {v_id} is out of balance. Total Debit: {v_debit:.2f}, Total Credit: {v_credit:.2f} (Delta: {diff:.2f})",
            })
        else:
            balanced_vouchers += 1

    # 3. Rule Check: Duplicate Invoices
    for inv_ref, entries in invoice_counts.items():
        distinct_vouchers = set(e[0] for e in entries)
        if len(distinct_vouchers) > 1:
            anomalies.append({
                "severity": "WARNING",
                "code": "DUPLICATE_INVOICE_REFERENCE",
                "voucher_id": ", ".join(distinct_vouchers),
                "message": f"Invoice reference '{inv_ref}' is referenced in multiple vouchers ({', '.join(distinct_vouchers)}). Possible duplicate claim.",
            })

    # 4. Rule Check: Fiscal Period & Account Validity
    for idx, row in enumerate(records, start=1):
        acc = row.get("account_code", "")
        # Flag suspicious suspense or unknown accounts
        if acc.startswith("999") or acc == "000000":
            anomalies.append({
                "severity": "HIGH",
                "code": "SUSPENSE_ACCOUNT_POSTING",
                "voucher_id": row.get("voucher_id"),
                "message": f"Suspicious account '{acc}' ({row.get('account_name')}) posted in voucher {row.get('voucher_id')}.",
            })

        # Fiscal year check (assuming current audit is FY 2025)
        d_str = row.get("date", "")
        if d_str and not d_str.startswith("2025"):
            anomalies.append({
                "severity": "MEDIUM",
                "code": "OUT_OF_PERIOD_TRANSACTION",
                "voucher_id": row.get("voucher_id"),
                "message": f"Transaction date {d_str} in voucher {row.get('voucher_id')} falls outside the active fiscal year 2025.",
            })

    # Calculate Data Quality Score (100 base, deducted by anomaly weights)
    deductions = sum(25 if a["severity"] == "CRITICAL" else 15 if a["severity"] == "HIGH" else 10 for a in anomalies)
    quality_score = max(0, 100 - deductions)

    # 5. Generate Markdown Audit Report
    report_md = f"""# 📋 Audit & Assurance Data Stewardship Report

**Client File:** `{input_csv}`  
**Reconciliation Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Auditor / Data Steward:** Adil El Idrissi  
**Overall Data Quality Score:** **{quality_score} / 100** ({'CERTIFIED READY' if quality_score >= 85 else 'REQUIRES REVIEW' if quality_score >= 60 else 'REJECTED - DATA INTEGRITY RISK'})

---

## 1. Executive Reconciliation Summary

| Metric | Value | Audit Note |
| :--- | :--- | :--- |
| **Total Lines Ingested** | {total_records} | Raw accounting extract line items |
| **Distinct Journal Vouchers** | {len(vouchers)} | Grouped journal entries |
| **Balanced Vouchers** | {balanced_vouchers} | Compliant with double-entry standard |
| **Unbalanced Vouchers** | {unbalanced_vouchers} | **Immediate adjustment required** |
| **Total Ledger Debit** | {total_debit_all:,.2f} MAD | Sum of all debits |
| **Total Ledger Credit** | {total_credit_all:,.2f} MAD | Sum of all credits |
| **Ledger Delta (Trial Balance)** | {abs(total_debit_all - total_credit_all):,.2f} MAD | Must be 0.00 for clean audit clearance |

---

## 2. Identified Discrepancies & Anomaly Log

"""
    if anomalies:
        report_md += "| Severity | Code | Voucher / Ref | Description |\n| :--- | :--- | :--- | :--- |\n"
        for a in anomalies:
            report_md += f"| **{a['severity']}** | `{a['code']}` | `{a['voucher_id']}` | {a['message']} |\n"
    else:
        report_md += "✅ *Zero discrepancies detected. Ledger conforms to all financial integrity rules.*\n"

    report_md += """
---

## 3. Data Steward Recommendation
"""
    if quality_score < 75:
        report_md += "> ⚠️ **Action Required**: Client data extract contains structural balance errors and duplicate invoice entries. Request an updated fiscal export from client accounting before loading into audit analytical models.\n"
    else:
        report_md += "> ✅ **Passed Validation**: Extract meets assurance threshold for analytical testing.\n"

    with open(output_report, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"✓ Reconciliation complete. Quality score: {quality_score}/100. Audit report generated at: {output_report}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Financial Audit Reconciliation Engine")
    parser.add_argument("--input", default="sample_ledger.csv", help="Path to input ledger CSV")
    parser.add_argument("--output", default="audit_report.md", help="Path to output markdown report")
    args = parser.parse_args()
    run_reconciliation(args.input, args.output)
