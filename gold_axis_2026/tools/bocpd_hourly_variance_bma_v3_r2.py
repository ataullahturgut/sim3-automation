from __future__ import annotations

import bocpd_hourly_variance_bma_v3 as base


def episode_onsets_correct(frame, k: int, threshold: float, p: int):
    s = frame[f"recent_p_{k}"].to_numpy()
    active = False
    above = 0
    below = 0
    idx = []
    for i, v in enumerate(s):
        if not active:
            above = above + 1 if v >= threshold else 0
            if above >= p:
                # Availability-safe onset: the alert can only exist after the
                # P-th confirming hourly observation has completed. Never
                # backdate it to the first above-threshold hour.
                idx.append(i)
                active = True
                above = 0
                below = 0
        else:
            below = below + 1 if v < threshold else 0
            if below >= p:
                active = False
                below = 0
                above = 0
    if not idx:
        return frame.iloc[0:0].copy()
    out = frame.iloc[idx].copy()
    out["score_k"] = k
    out["score_threshold"] = threshold
    out["persistence"] = p
    out["availability_rule"] = "PTH_CONFIRMING_BAR_COMPLETED_NO_BACKDATING"
    return out


def main() -> None:
    base.episode_onsets = episode_onsets_correct
    base.main()


if __name__ == "__main__":
    main()
