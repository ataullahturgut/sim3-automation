# TR09 source quality research

A 2026-09-25 09:00 Europe/Istanbul bar is absent from the HistData candidate source despite observed gold trading on that date. Treat as a data outage, not a holiday. Historical labels must fail closed rather than advance to the next observed 09:00 bar.

Corrected risk frequency (Jan–Sep; 09:00 Turkey, strict market calendar and complete quotes): 2023 9/191, 2024 14/194, 2025 12/193, 2026 40/188. Earlier R72 weekday counts differ because Good Friday was not excluded. This is a label-quality finding, not a profitable trading strategy.
