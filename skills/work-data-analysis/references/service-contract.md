# Service data contract

One row represents one month and one service channel. Keys: `month` (YYYY-MM), `service`.

Counts: `received` (new requests), `completed` (closed requests), `on_time_completed` (on-time subset of completed), `survey_responses` (respondents). `total_work_days` is the sum of business-day durations of completed requests, not the number of days in the month. `satisfaction_mean` is a 1–5 group mean and may be missing.

On-time rate = sum(on_time_completed) / sum(completed).
Average duration = sum(total_work_days) / sum(completed).
Weighted satisfaction = sum(mean * respondents) / sum(respondents), restricted to groups with known means; disclose scored respondents / all respondents.

New and closed requests are different cohorts. Do not call closed/new a completion rate for the same requests. Group means and aggregated monthly data do not establish causality or individual distributions. Zero denominator produces an unavailable metric, never a false zero rate.

Conflicting key duplicates, missing required measures, invalid months, negative counts, fractional counts, and on-time counts exceeding completed are rejected. A repeated entire row is removed once and its original row is logged. Exact source row locations assume a header on row 1.
