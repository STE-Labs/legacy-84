# Legacy 84 BOM Comparison Findings

Date: 2026-08-16

## Overview

Four BOMs were compared across the Legacy 84 variants:

- **legacy-84-mono** (mono, upright tubes)
- **legacy-84-mono-inverted** (mono, inverted tubes)
- **legacy-84-stereo** (stereo, upright tubes)
- **legacy-84-stereo-inverted** (stereo, inverted tubes)

Mono and Mono-Inverted should have identical component counts (only tube socket packages differ).
Stereo variants should generally have 2x the mono component counts, except for shared components
(pure switch circuit: B3B-ZR, BS170, BZX55C5V1, 100nF capacitor, and one 10k/1k resistor).

---

## Expected Differences (by design)

### Tube Socket Packages

| Component | Mono / Stereo          | Mono-Inv / Stereo-Inv        |
|-----------|------------------------|------------------------------|
| ECC88     | ECC88-P (NOVAL1)       | ECC88-POI (NOVAL1_INVERTED)  |
| EL84      | EL84-PO (NOVAL1)       | EL84-POI (NOVAL1_INVERTED)   |

This is correct — inverted variants use inverted tube socket footprints.

### Shared Components (not doubled in stereo)

The following are shared across both channels in the stereo variants and correctly appear as 1x:

- B3B-ZR connector (1x)
- BS170 N-Channel MOS FET (1x)
- BZX55C5V1 zener diode, DO35-7 (1x)
- 100nF capacitor (1x)

The 10k and 1k resistors scale as +1 (shared) rather than exactly 2x, which is also expected.

---

## Inconsistencies Found

### 1. Value Naming: 100u/25V Capacitor (Cosmetic)

| BOM              | Value Used   | Parts        |
|------------------|--------------|--------------|
| Mono             | 100u/25V     | C310, C311   |
| Mono-Inverted    | 100uF/25V    | C310, C311   |
| Stereo (line 1)  | 100u/25V     | C310, C311   |
| Stereo (line 2)  | 100u/25      | C610, C611   |
| Stereo-Inverted  | 100u/25V     | C310-C611    |

**Problem:** Three different value strings for the same component. The Stereo BOM splits the
same part across two lines with different names ("100u/25V" and "100u/25"), and the Mono-Inverted
BOM uses "100uF/25V" instead of "100u/25V".

**Recommendation:** Standardize all to "100u/25V".

---

### 2. Fuse Value Naming: "T 3A" vs "T3A" (Cosmetic)

| BOM           | Value  | Part |
|---------------|--------|------|
| Mono          | T 3A   | F102 |
| Mono-Inverted | T3A    | F102 |

**Problem:** Inconsistent spacing in the fuse value name.

**Recommendation:** Use consistent formatting, e.g., "T 3A" with a space.

---

### 3. Fuse Ratings Differ Between Normal and Inverted Variants

| BOM              | HV Fuse             | LV Fuse                      |
|------------------|----------------------|-------------------------------|
| Mono             | T 3A (F102)          | T 315mA (F101, F201)          |
| Mono-Inverted    | T3A (F102)           | T 315mA (F101, F201)          |
| Stereo           | T 3A (F102, F402)    | T 315mA (F101, F201, F401, F501) |
| Stereo-Inverted  | T2A (F101, F402)     | T250mA (F102, F201, F401, F501)  |

**Problems:**
1. Fuse ratings are different: Normal variants use 3A + 315mA, Inverted variants use 2A + 250mA.
   Is this intentional due to the inverted circuit design, or an error?
2. In Stereo-Inverted, the part designators are swapped: F101 is the HV fuse and F102 is the LV
   fuse, which is the opposite of the Stereo variant.

**Recommendation:** Verify whether the different fuse ratings are intentional. If not, align them.
Also verify the F101/F102 assignment in Stereo-Inverted.

---

### 4. R629 and R630: 1k vs 2.7k (Potential Circuit Error)

| BOM              | R629/R630 Value | 1k Total | 2.7k Total |
|------------------|-----------------|----------|------------|
| Stereo           | 1k              | 13       | 4          |
| Stereo-Inverted  | 2.7k            | 11       | 6          |

**Problem:** R629 and R630 are listed as 1k resistors in the Stereo BOM but as 2.7k resistors in
the Stereo-Inverted BOM. The total counts shift accordingly (Stereo has 13x 1k and 4x 2.7k,
while Stereo-Inverted has 11x 1k and 6x 2.7k).

**This is the most significant finding** — one of these BOMs has the wrong resistor value for
R629/R630. This could affect the circuit behavior.

**Recommendation:** Check the schematic to determine the correct value for R629 and R630.

---

### 5. Tube Part Designator Assignment in Stereo-Inverted

| BOM              | ECC88 (Input Tubes)       | EL84 (Output Tubes)         |
|------------------|---------------------------|-----------------------------|
| Stereo           | V101, V103, V401, V403    | V102, V104, V402, V404      |
| Stereo-Inverted  | V103, V104, V401, V403    | V101, V102, V402, V404      |

**Problem:** In the Stereo-Inverted BOM, V104 is listed as an ECC88 (input tube) and V101 is
listed as an EL84 (output tube). In every other BOM, even-numbered tubes (V102, V104) are always
EL84 and odd-numbered tubes (V101, V103) are always ECC88.

**Recommendation:** Verify whether this swap is intentional for the inverted layout or if V101
should be ECC88 and V104 should be EL84.

---

## Summary Table

| #  | Issue                                          | Severity | Action Needed         |
|----|------------------------------------------------|----------|-----------------------|
| 1  | 100u/25V vs 100uF/25V vs 100u/25 naming       | Low      | Standardize naming    |
| 2  | "T 3A" vs "T3A" spacing                        | Low      | Standardize naming    |
| 3  | Fuse ratings: 3A/315mA vs 2A/250mA             | Medium   | Verify if intentional |
| 4  | R629/R630: 1k (Stereo) vs 2.7k (Stereo-Inv)   | High     | Check schematic       |
| 5  | V101/V104 tube type swap in Stereo-Inverted    | Medium   | Verify if intentional |
