// Ελληνικό λεξικό ετικετών — όλα τα user-facing strings από εδώ
export const L = {
  appName: "Mission Control",
  agents: "Πράκτορες",
  runs: "Εκτελέσεις",
  liveFeed: "Ζωντανή ροή",
  newRun: "Νέα εκτέλεση",
  task: "Εργασία",
  agent: "Πράκτορας",
  statusLabel: "Κατάσταση",
  duration: "Διάρκεια",
  createdAt: "Δημιουργήθηκε",
  available: "Διαθέσιμο",
  notInstalled: "Μη εγκατεστημένο",
  submit: "Εκτέλεση",
  noRuns: "Δεν υπάρχουν εκτελέσεις ακόμα.",
  noEvents: "Αναμονή γεγονότων…",
  apiDown: "Ο server του Mission Control δεν είναι διαθέσιμος (uv run mission-control serve).",
  log: "Log",
  backToRuns: "← Όλες οι εκτελέσεις",
  exitCode: "Κωδικός εξόδου",
  estCost: "εκτ. κόστος/run",
} as const;

export const STATUS_LABELS: Record<string, string> = {
  queued: "Σε αναμονή",
  running: "Σε εξέλιξη",
  done: "Ολοκληρώθηκε",
  error: "Σφάλμα",
  cancelled: "Ακυρώθηκε",
};

export const SCOPE_LABELS: Record<string, string> = {
  arivia: "Arivia",
  titan: "Titan",
  personal: "Personal",
};
