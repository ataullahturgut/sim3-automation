from __future__ import annotations

import gc_break_enginewise_export_v1 as impl

_original_base_export = impl.base_export


def _base_export_reset_index(panel, engine, native_clock, role):
    return _original_base_export(panel, engine, native_clock, role).reset_index(drop=True)


impl.base_export = _base_export_reset_index


if __name__ == "__main__":
    raise SystemExit(impl.main())
