# Verity API contract (v1)

Single source of truth. Backend responses validate against `schemas.py`;
the frontend imports `types.ts`. Never rename fields. All endpoints are
prefixed `/api/v1`.

Score thresholds: **0–34 SAFE, 35–69 SUSPICIOUS, 70–100 HIGH_RISK**.

```
GET  /api/v1/health                 -> {status: "ok", models_loaded: bool}
GET  /api/v1/samples/messages       -> [{id, title, text, channel, sender}]
GET  /api/v1/samples/quiz           -> [QuizItem]                        (added v1.1)
POST /api/v1/analyze/message
  req:  {text: str(1..2000), channel: "sms"|"whatsapp"|"email",
         sender: str|null, lang_out: "en"|"hi"|"ta", polish: bool = false}
  resp: MessageAnalysis {
    id: uuid, risk_score: int 0..100,
    label: "SAFE"|"SUSPICIOUS"|"HIGH_RISK",
    scam_type: str|null,           # e.g. "COLLECT_REFUND", "FAKE_KYC"
    model_prob: float, rule_score: float,
    signals: [Signal], links: [LinkFinding],
    explanation: str, next_steps: [str],
    explanation_source: "template"|"llm" }

Signal { code: SignalCode, title: str, weight: float 0..1,
         description: str,
         evidence: [{start: int, end: int, text: str}] }  # char offsets in text

SignalCode = URGENCY | ACCOUNT_THREAT | CREDENTIAL_REQUEST | PIN_TO_RECEIVE |
  SUSPICIOUS_LINK | LOOKALIKE_DOMAIN | URL_SHORTENER | REMOTE_ACCESS_APP |
  PRIZE_LURE | PAY_TO_EARN | IMPERSONATION | KYC_UPDATE | SENDER_MISMATCH |
  CALLBACK_NUMBER | MODEL_TEXT
  # transaction signals (added v1.1):
  | NEW_PAYEE_COLLECT | YOUNG_PAYEE_ACCOUNT | PAYMENT_BURST | NIGHT_HIGH_VALUE
  | DEVICE_CHANGE_HIGH_VALUE | REPORTED_PAYEE | JUST_UNDER_LIMIT | MULE_PATTERN
  | MODEL_TXN

LinkFinding { raw: str, domain: str, verdict: "OK"|"SUSPICIOUS"|"DANGEROUS",
              reasons: [str], lookalike_of: str|null }

GET  /api/v1/transactions/demo-users -> [{user_id, persona, home_city}]
GET  /api/v1/transactions/feed?user_id=U001&limit=50&lang_out=en
  resp: [{transaction: Transaction, analysis: TxnAnalysis}]
POST /api/v1/analyze/transaction
  req:  {transaction: Transaction, lang_out: "en"|"hi"|"ta"}
  resp: TxnAnalysis

Transaction { txn_id, user_id, timestamp: ISO-8601,
  type: "PAY"|"COLLECT_REQUEST"|"RECEIVE", amount_inr: float,
  payee_vpa: str, payee_name: str, channel: "QR"|"VPA"|"PHONE",
  payee_is_new: bool, payee_account_age_days: int,
  payee_report_count: int, device_changed: bool }

TxnAnalysis { txn_id, risk_score, label, signals: [Signal],
  feature_contributions: [{feature: str, value: str, contribution: float}],
  explanation: str, next_steps: [str], explanation_source }

QuizItem { id: str, text: str, channel, sender: str|null,
           is_scam: bool, scam_type: str|null }

POST /api/v1/feedback {analysis_id, kind: "message"|"transaction",
                       correct_label, note: str|null} -> {ok: true}
GET  /api/v1/metrics -> contents of ml/reports/metrics.json
```

## Notes
- `feature_contributions[].contribution` is in probability-logit units from
  the transaction model (positive pushes risk up). `feature` is a
  plain-language sentence ("Payee account is only 3 days old").
- Transaction signals carry an empty `evidence` list.
- Errors: invalid input returns 422 with `{detail: str | [..]}`; never 500.
