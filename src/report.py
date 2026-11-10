"""Write a source-attributed weekly report from the most recent recorded snapshot."""
import html
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
data = ROOT / 'site' / 'data'
history = json.loads((data / 'history.json').read_text(encoding='utf-8'))
status = json.loads((data / 'status.json').read_text(encoding='utf-8'))
latest = history[-1] if history else {'records': [], 'week': 'not available'}
rows = latest.get('records', [])
groups = {}
for r in rows:
    key = (r['source'], r['benchmark'], r['version'])
    groups.setdefault(key, []).append(r)
lines = ['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Weekly AI Benchmark Report</title><style>body{font:16px system-ui;max-width:980px;margin:25px auto;padding:15px;color:#162237}table{border-collapse:collapse;width:100%}th,td{padding:9px;text-align:left;border-bottom:1px solid #ccd}small{color:#58677a}</style>',
         '<h1>Global AI Benchmark — weekly report</h1>',
         '<p>Week: ' + html.escape(str(latest['week'])) + ' | Collected UTC: ' + html.escape(str(status.get('collected_at'))) + '</p>',
         '<p>Scores belong to separate benchmarks and must not be aggregated. Rank changes across benchmark versions are not comparable.</p><h2>Source status</h2>']
for k, v in status.get('sources', {}).items():
    lines.append('<p><b>' + html.escape(k) + '</b>: ' + html.escape(str(v)) + '</p>')
for (source, bench, version), models in sorted(groups.items()):
    higher = models[0].get('higher_is_better', True)
    models.sort(key=lambda r:r['score'], reverse=higher)
    lines.append('<h2>' + html.escape(source + ' — ' + bench) + '</h2><small>Version: ' + html.escape(version) + '</small><table><tr><th>Rank</th><th>Model</th><th>Score</th></tr>')
    for i, r in enumerate(models[:30], 1):
        lines.append('<tr><td>' + str(i) + '</td><td>' + html.escape(r['model']) + '</td><td>' + html.escape(str(r['score']) + ' ' + r['unit']) + '</td></tr>')
    lines.append('</table>')
if not rows:
    lines.append('<p>No successfully collected benchmark scores yet. This is not a zero-score ranking.</p>')
lines.append('<p><a href="index.html">Dashboard</a></p></html>')
(data.parent / 'weekly-report.html').write_text('\n'.join(lines), encoding='utf-8')
print('Generated weekly-report.html with',len(rows),'official-source records')
