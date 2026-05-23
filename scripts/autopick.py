import json
from pathlib import Path

shortlist = json.loads(Path('scripts/broll_output/shortlist.json').read_text(encoding='utf-8'))
picks = {}

for slot_id, entry in shortlist.items():
    cands = entry.get('candidates', [])
    if not cands:
        print(f'NO CANDIDATES: {slot_id}')
        continue

    def score(c):
        ana = c.get('analysis', {})
        flag = 1 if ana.get('corner_text_flag') else 0
        res = c['width'] * c['height']
        return (flag, -res)

    best = sorted(cands, key=score)[0]
    picks[slot_id] = {
        'slot_id':         slot_id,
        'category':        entry['category'],
        'role':            entry['role'],
        'mood_energy':     entry['mood_energy'],
        'mood_temperature':entry['mood_temperature'],
        'n':               entry['n'],
        'source':          best['source'],
        'id':              best['id'],
        'license_ref':     best['license_ref'],
        'download_url':    best['download_url'],
        'pexels_url':      best.get('pexels_url', ''),
        'width':           best['width'],
        'height':          best['height'],
        'fps':             best['fps'],
        'duration':        best['duration'],
    }
    print(slot_id + ': ' + best['license_ref'] + ' ' + str(best['width']) + 'x' + str(best['height']) + ' ' + str(best['duration']) + 's — ' + best.get('pexels_url',''))

Path('scripts/broll_output/picks.json').write_text(json.dumps(picks, indent=2), encoding='utf-8')
print('\npicks.json written — ' + str(len(picks)) + ' slots picked')
