# AWS Cost Optimizer

The runnable Streamlit entry point is the root [`app.py`](app.py).

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open `http://localhost:8501` and sign in with `1234` / `1234`.

The v1 implementation plan, architecture decisions, and next milestones are
in [`IMPLEMENTATION_PLAN.md`](IMPLEMENTATION_PLAN.md). Pure analytics tests can
be run with `python -m pytest -q`.

The **Decision Workspace** is the product's key differentiation: it converts a
cost opportunity into an owned, approval-gated decision brief with safeguards,
a 90-day impact estimate, local audit record, and exportable workflow payload.
See [`PRODUCT_RATIONALE.md`](PRODUCT_RATIONALE.md) for the scope boundary with
AWS-native cost tools.
