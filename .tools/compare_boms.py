import csv

def parse_bom(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        for row in reader:
            if len(row) < 5 or not row[0].strip():
                continue
            rows.append({
                'qty': int(row[0]),
                'value': row[1],
                'device': row[2],
                'package': row[3],
                'parts': row[4],
                'description': row[5] if len(row) > 5 else ''
            })
    return rows

def make_key(row):
    return (row['value'], row['device'], row['package'])

def build_map(rows):
    m = {}
    for r in rows:
        k = make_key(r)
        if k in m:
            m[k]['qty'] += r['qty']
            m[k]['parts'] += ', ' + r['parts']
        else:
            m[k] = dict(r)
    return m

def compare_boms(name_a, map_a, name_b, map_b):
    all_keys = sorted(set(list(map_a.keys()) + list(map_b.keys())))
    diffs = []
    for k in all_keys:
        a = map_a.get(k)
        b = map_b.get(k)
        if a and b:
            if a['qty'] != b['qty']:
                diffs.append(f"  QTY MISMATCH: {k[0]} ({k[1]})")
                diffs.append(f"    {name_a}: {a['qty']}x  parts: {a['parts']}")
                diffs.append(f"    {name_b}: {b['qty']}x  parts: {b['parts']}")
        elif a and not b:
            diffs.append(f"  ONLY IN {name_a}: {k[0]} ({k[1]}, {k[2]}) qty={a['qty']} parts={a['parts']}")
        elif b and not a:
            diffs.append(f"  ONLY IN {name_b}: {k[0]} ({k[1]}, {k[2]}) qty={b['qty']} parts={b['parts']}")
    return diffs

mono = parse_bom('legacy-84-mono/legacy-84-mono.csv')
mono_inv = parse_bom('legacy-84-mono-inverted/legacy-84-mono-inverted.csv')
stereo = parse_bom('legacy-84-stereo/legacy-84-stereo.csv')
stereo_inv = parse_bom('legacy-84-stereo-inverted/legacy-84-stereo-inverted.csv')

mono_m = build_map(mono)
mono_inv_m = build_map(mono_inv)
stereo_m = build_map(stereo)
stereo_inv_m = build_map(stereo_inv)

print("=" * 80)
print("1. MONO vs MONO-INVERTED")
print("=" * 80)
diffs = compare_boms("Mono", mono_m, "Mono-Inv", mono_inv_m)
if diffs:
    for d in diffs:
        print(d)
else:
    print("  No differences found.")

print()
print("=" * 80)
print("2. STEREO vs STEREO-INVERTED")
print("=" * 80)
diffs2 = compare_boms("Stereo", stereo_m, "Stereo-Inv", stereo_inv_m)
if diffs2:
    for d in diffs2:
        print(d)
else:
    print("  No differences found.")

print()
print("=" * 80)
print("3. MONO vs STEREO SCALING (stereo should be ~2x mono)")
print("=" * 80)
all_keys = sorted(set(list(mono_m.keys()) + list(stereo_m.keys())))
for k in all_keys:
    a = mono_m.get(k)
    b = stereo_m.get(k)
    if a and b:
        if b['qty'] != 2 * a['qty']:
            print(f"  {k[0]} ({k[1]}): Mono={a['qty']}, Stereo={b['qty']} (expected {2*a['qty']})")
    elif a and not b:
        print(f"  ONLY IN MONO: {k[0]} ({k[1]}, {k[2]}) qty={a['qty']}")
    elif b and not a:
        print(f"  ONLY IN STEREO: {k[0]} ({k[1]}, {k[2]}) qty={b['qty']}")

print()
print("=" * 80)
print("4. MONO-INV vs STEREO-INV SCALING (stereo-inv should be ~2x mono-inv)")
print("=" * 80)
all_keys2 = sorted(set(list(mono_inv_m.keys()) + list(stereo_inv_m.keys())))
for k in all_keys2:
    a = mono_inv_m.get(k)
    b = stereo_inv_m.get(k)
    if a and b:
        if b['qty'] != 2 * a['qty']:
            print(f"  {k[0]} ({k[1]}): Mono-Inv={a['qty']}, Stereo-Inv={b['qty']} (expected {2*a['qty']})")
    elif a and not b:
        print(f"  ONLY IN MONO-INV: {k[0]} ({k[1]}, {k[2]}) qty={a['qty']}")
    elif b and not a:
        print(f"  ONLY IN STEREO-INV: {k[0]} ({k[1]}, {k[2]}) qty={b['qty']}")
