// TypeScript mirror of contracts/schemas.py. Source of truth: contracts/api.md.

export type Label = "SAFE" | "SUSPICIOUS" | "HIGH_RISK";
export type Channel = "sms" | "whatsapp" | "email";
export type Lang = "en" | "hi" | "ta";
export type ExplanationSource = "template" | "llm";
export type LinkVerdict = "OK" | "SUSPICIOUS" | "DANGEROUS";
export type TxnType = "PAY" | "COLLECT_REQUEST" | "RECEIVE";
export type TxnChannel = "QR" | "VPA" | "PHONE";
export type FeedbackKind = "message" | "transaction";

export type SignalCode =
  | "URGENCY"
  | "ACCOUNT_THREAT"
  | "CREDENTIAL_REQUEST"
  | "PIN_TO_RECEIVE"
  | "SUSPICIOUS_LINK"
  | "LOOKALIKE_DOMAIN"
  | "URL_SHORTENER"
  | "REMOTE_ACCESS_APP"
  | "PRIZE_LURE"
  | "PAY_TO_EARN"
  | "IMPERSONATION"
  | "KYC_UPDATE"
  | "SENDER_MISMATCH"
  | "CALLBACK_NUMBER"
  | "MODEL_TEXT"
  | "NEW_PAYEE_COLLECT"
  | "YOUNG_PAYEE_ACCOUNT"
  | "PAYMENT_BURST"
  | "NIGHT_HIGH_VALUE"
  | "DEVICE_CHANGE_HIGH_VALUE"
  | "REPORTED_PAYEE"
  | "JUST_UNDER_LIMIT"
  | "MULE_PATTERN"
  | "MODEL_TXN";

export const THRESHOLD_SUSPICIOUS = 35;
export const THRESHOLD_HIGH_RISK = 70;

export interface Health {
  status: "ok";
  models_loaded: boolean;
}

export interface SampleMessage {
  id: string;
  title: string;
  text: string;
  channel: Channel;
  sender: string | null;
}

export interface QuizItem {
  id: string;
  text: string;
  channel: Channel;
  sender: string | null;
  is_scam: boolean;
  scam_type: string | null;
}

export interface Evidence {
  start: number;
  end: number;
  text: string;
}

export interface Signal {
  code: SignalCode;
  title: string;
  weight: number;
  description: string;
  evidence: Evidence[];
}

export interface LinkFinding {
  raw: string;
  domain: string;
  verdict: LinkVerdict;
  reasons: string[];
  lookalike_of: string | null;
}

export interface AnalyzeMessageRequest {
  text: string;
  channel: Channel;
  sender: string | null;
  lang_out: Lang;
  polish?: boolean;
}

export interface MessageAnalysis {
  id: string;
  risk_score: number;
  label: Label;
  scam_type: string | null;
  model_prob: number;
  rule_score: number;
  signals: Signal[];
  links: LinkFinding[];
  explanation: string;
  next_steps: string[];
  explanation_source: ExplanationSource;
}

export interface DemoUser {
  user_id: string;
  persona: string;
  home_city: string;
}

export interface Transaction {
  txn_id: string;
  user_id: string;
  timestamp: string;
  type: TxnType;
  amount_inr: number;
  payee_vpa: string;
  payee_name: string;
  channel: TxnChannel;
  payee_is_new: boolean;
  payee_account_age_days: number;
  payee_report_count: number;
  device_changed: boolean;
}

export interface FeatureContribution {
  feature: string;
  value: string;
  contribution: number;
}

export interface TxnAnalysis {
  txn_id: string;
  risk_score: number;
  label: Label;
  signals: Signal[];
  feature_contributions: FeatureContribution[];
  explanation: string;
  next_steps: string[];
  explanation_source: ExplanationSource;
}

export interface FeedItem {
  transaction: Transaction;
  analysis: TxnAnalysis;
}

export interface AnalyzeTransactionRequest {
  transaction: Transaction;
  lang_out: Lang;
}

export interface FeedbackRequest {
  analysis_id: string;
  kind: FeedbackKind;
  correct_label: Label;
  note: string | null;
}

export interface FeedbackResponse {
  ok: true;
}

// ---- /metrics (shape written by ml/eval/evaluate.py) ----

export interface ClassMetrics {
  precision: number;
  recall: number;
  f1: number;
  pr_auc: number | null;
}

export interface ModelRow extends ClassMetrics {
  name: string;
  key: string;
  confusion: [[number, number], [number, number]];
}

export interface BreakdownRow {
  group: string;
  n: number;
  value: number;
}

export interface FailureRow {
  kind: "message" | "transaction";
  text: string;
  true_label: number;
  predicted: number;
  score: number;
  group: string;
  why: string;
}

export interface MessageMetrics {
  test_size: number;
  train_size: number;
  n_templates_test: number;
  threshold: number;
  fusion_weight: number;
  rule_floor_min: number;
  models: ModelRow[];
  recall_by_scam_type: BreakdownRow[];
  f1_by_language: BreakdownRow[];
  fpr_by_legit_class: BreakdownRow[];
  hard_negative_fpr: number;
  scam_type_accuracy: number;
  external_uci: ClassMetrics & { n: number; note: string };
}

export interface TxnMetrics {
  test_size: number;
  train_size: number;
  fraud_rate_test: number;
  threshold: number;
  floor_min: number;
  explainer: string;
  models: (ModelRow & { false_alarms_per_1000: number })[];
  recall_by_pattern: BreakdownRow[];
  demo_frauds_flagged: string;
}

export interface Metrics {
  generated_at: string;
  data_hash: string;
  message: MessageMetrics;
  transaction: TxnMetrics | null;
  failures: FailureRow[];
}
