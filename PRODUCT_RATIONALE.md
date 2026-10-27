# Product rationale — what this adds beyond AWS

## The defensibility test

Every feature must answer a business decision that an AWS signal alone does
not complete. The app is **not** positioned as a replacement for AWS Cost
Explorer, Budgets, Cost Anomaly Detection, Compute Optimizer, or Cost
Optimization Hub. Those become upstream evidence sources.

| Capability | AWS already provides | This product's distinct job | Why it is necessary |
| --- | --- | --- | --- |
| Cost and utilization signals | Cost Explorer, Budgets, Anomaly Detection, Compute Optimizer, and Cost Optimization Hub provide spend views, alerts, and recommendations. | Normalize selected signals into a decision queue that is comparable across technical and business owners. | An alert or recommendation does not assign a person, a decision deadline, or a safe operating condition. |
| Recommendation | AWS gives service- and resource-level findings, estimated savings, and implementation information. | Create a decision brief with accountable owner, required approval, safeguard checklist, 90-day impact, and a portable audit payload. | Cost changes can affect availability, retention, legal hold, and customer commitments; a savings estimate alone cannot authorize a change. |
| Anomaly/health signal | AWS anomaly detection identifies unusual spend; AWS Budgets tracks thresholds. | Use the signal only to make the decision queue more urgent and transparent. | The score cannot replace AWS detection. It is a visible, explainable triage input for the operating team. |
| Automation (future) | AWS can take configured actions through native services. | Route approved decision packs to a ticket, change-control process, or workflow engine, with evidence and rollback gates intact. | The important control is not “automate everything”; it is preventing unsafe, unowned optimization actions. |

## Delivered now

The Decision Workspace is the first working implementation of this operating
layer. It creates deterministic policy gates by opportunity type, ranks cases
using explainable inputs, and exports a decision pack suitable for a later
Jira, ServiceNow, Slack, or Step Functions adapter.

## Architecture route forward

```text
AWS / billing / telemetry adapters
             ↓
analytics.py  →  recommendations
             ↓
governance.py →  decision cases + policy controls
             ↓
storage / API adapter → ticketing, approval, scheduler, audit trail
```

The presentation layer only renders these services. This lets a future team
replace demo data with AWS SDK adapters and replace local JSON export with a
workflow integration without rewriting decision logic.

## Source baseline

- [AWS Cloud Financial Management](https://aws.amazon.com/aws-cost-management/)
- [AWS Guidance for Cloud Financial Management](https://docs.aws.amazon.com/solutions/cloud-financial-management-on-aws/)
