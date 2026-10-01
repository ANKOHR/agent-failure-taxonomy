# Lessons for KOML

Explicit error signals support deterministic categories, but descriptions alone cannot establish a root cause. Unknown failures need a visible category so ambiguity is not disguised as accuracy.

The synthetic test validates the assumption that supplied signals and independent labels can reconcile exactly. It does not validate the assumption that Henry's real failures always carry reliable signals. That remains for the two-week hand-checked trial.

Operating rule: keep expected labels outside classification decisions, test mutations to both observations and labels, and refuse to claim operational value until it is measured on actual use.
