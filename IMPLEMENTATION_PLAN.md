# AWS Cost Optimizer — v1 foundation plan

## Presentation milestone

This milestone represents the first 25–30% of the product build: the demo now
has a separable analytics domain, explainable signals, a portable report, and
coverage for the pure business rules. The UI remains a Streamlit presentation
layer rather than becoming the system of record.

## Delivered in this slice

1. **Analytics service layer** — move sample telemetry generation and
   recommendation rules into `aws_cost_optimizer/analytics.py`. The functions
   are reusable by a future AWS Cost Explorer adapter, API, or scheduled job.
2. **Performance foundation** — cache deterministic telemetry with a bounded
   LRU cache so Streamlit reruns do not rebuild the same 30-day and 15-day
   datasets.
3. **Explainable intelligence** — add robust rolling-median/MAD spend anomaly
   detection and a 0–100 cost health score with visible component scores.
4. **Portable reporting** — export the current account analysis as a JSON
   snapshot, establishing a handoff format for automation or an API.
5. **Assistant boundary** — move the local assistant’s intent logic into a
   service module so a model-backed provider can replace it later without
   changing the dashboard.
6. **Decision-governance layer** — add a policy-driven Decision Workspace that
   turns recommendations into owned, approval-gated briefs with safeguards,
   deadlines, 90-day impact, local audit history, and portable decision packs.

## Next milestones

- Replace generated telemetry with read-only Cost Explorer, CloudWatch, S3,
  and resource inventory adapters behind the same analytics interface.
- Add identity and role-based approval to validate decision owners and gates.
- Add an adapter interface for Jira, ServiceNow, Slack, or Step Functions to
  consume exported decision packs; retain the safety checks as preconditions.
- Add scheduled email/Slack summaries and anomaly notifications.
- Add integration tests against mocked AWS responses and a deployment config.
