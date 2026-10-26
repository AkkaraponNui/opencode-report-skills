---
name: work-data-charts
description: Create readable Thai data charts with traceable values and captions, exported as PNG and SVG. Use for charts from validated analysis or CSV, not decorative images or invented statistics.
---

# Chart validated data

Start with the analytical question, validated numbers, units, population and time period. Recompute if source data changed. Do not draw numerical charts using image generation.

Choose a bar chart for comparisons, a line for time trends, or a scatterplot for relationships when appropriate. Prefer direct labels, restrained navy/teal colors, light grids and clear Thai text. Use `assets/Sarabun-*.ttf` with the included OFL license. Never truncate bar axes to exaggerate differences, use decorative 3D, or hide missing values.

## Run the supplied renderer

Use the prepared `.venv` Python. The portable script needs matplotlib and pandas. Workshop path:

```text
python <skill-dir>/scripts/charts.py --analysis output/analysis/analysis.json --output output/charts
```

This produces two charts, their underlying CSV files and `chart-manifest.json`. It hashes `analysis.json` to detect mismatched chart/report inputs. The workload chart distinguishes requests received from completed; the timeliness chart uses on-time/closed and a 0–100% scale.

For unrelated data use explicit fields and a meaningful title/unit, for example:

```text
python <skill-dir>/scripts/charts.py --csv validated.csv --x month --y count --kind line --title "ปริมาณงานรายเดือน" --ylabel "งาน" --output output/charts
```

This generic helper supports bar/line only, rejects duplicate x labels and missing y values, and saves one PNG/SVG/data file. For other chart types write a suitable reproducible renderer rather than misrepresenting the data.

## Verify and deliver

Open every PNG. Check Thai tone marks, clipped titles, legends, units, chronological order and value labels. Match plotted values against source metrics. Put a source and limitation in the caption; distinguish percent changes from percentage-point changes. SVG keeps vector/text elements but requires the supplied font for identical text display; PNG is the reliable report image.

Return chart files, captions and underlying values. Explain the chart's supported finding without inventing a causal story. Keep the manifest and data next to the graphics so a report can trace them.
