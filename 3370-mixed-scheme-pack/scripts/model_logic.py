#!/usr/bin/env python3
"""
3370 GNR Mixed Scheme — model logic.
Self-contained recompute of the feasibility so any sensitivity row in the pack
can be COMPUTED (and labelled as computed), never guessed.

Running this reproduces the locked base case in data/mixed_scheme.json.
"""
GST = 1.15
SITE = 809
TARGET_MARGIN = 0.18   # developer hurdle used for residual land value

def feaso(
    n_1bed=16, n_dk=10,
    price_1bed=499_000, price_dk=599_000,
    build_1bed_psm=3_600, build_dk_psm=4_000, build_amenity_psm=3_400,
    amenity_gba=120, nsa_eff=0.83, title_m2=45,
    land=605_000, demo=25_000, rc=110_000, amenity_fitout=350_000,
    prof_pct=0.10, cont_pct=0.065, dc_per_title=25_000, site=80_000,
    months=14, rate=0.07, avg_drawn=0.50, mkt_pct=0.035,
):
    n = n_1bed + n_dk
    # GFA by product (titles are 45 m2 net; GFA = net / efficiency)
    gfa_1bed = n_1bed * title_m2 / nsa_eff
    gfa_dk   = n_dk   * title_m2 / nsa_eff
    gfa_amen = amenity_gba
    GFA = gfa_1bed + gfa_dk + gfa_amen

    build = gfa_1bed*build_1bed_psm + gfa_dk*build_dk_psm + gfa_amen*build_amenity_psm
    blended_psm = build / GFA

    grv_1bed = n_1bed * price_1bed
    grv_dk   = n_dk   * price_dk
    GRV_incl = grv_1bed + grv_dk
    GRV_ex   = GRV_incl / GST

    prof = build * prof_pct
    cont = build * cont_pct
    dc   = dc_per_title * n
    base = demo + build + prof + cont + dc + rc + site + amenity_fitout
    loan = (land + base) * 0.75
    equity = (land + base) * 0.25
    interest = loan * avg_drawn * rate * (months/12)
    sales = GRV_ex * mkt_pct
    total = land + base + interest + sales
    profit = GRV_ex - total
    margin = profit / GRV_ex * 100
    roe = profit / equity * 100
    # residual land value at target margin
    nonland = base - land + interest + sales  # base includes land; strip it
    nonland = (demo+build+prof+cont+dc+rc+site+amenity_fitout) + interest + sales
    land_resid = GRV_ex - nonland - GRV_ex*TARGET_MARGIN

    return {
        "n": n, "n_1bed": n_1bed, "n_dk": n_dk, "GFA": round(GFA),
        "blended_psm": round(blended_psm),
        "GRV_incl": round(GRV_incl), "GRV_ex": round(GRV_ex),
        "build": round(build), "total": round(total),
        "profit": round(profit), "margin": round(margin,1),
        "equity": round(equity), "loan": round(loan), "roe": round(roe),
        "land_resid": round(land_resid), "land_psm": round(land_resid/SITE),
    }

if __name__ == "__main__":
    base = feaso()
    print("BASE CASE (should match data/mixed_scheme.json):")
    for k,v in base.items():
        print(f"  {k}: {v:,}" if isinstance(v,(int,float)) else f"  {k}: {v}")
    print("\nBUILD-COST SENSITIVITY (vary dual-key build rate):")
    for bp in [3_800, 4_000, 4_300]:
        r = feaso(build_dk_psm=bp)
        print(f"  dual-key ${bp}/m2 -> blended ${r['blended_psm']}/m2, "
              f"margin {r['margin']}%, land ${r['land_psm']:,}/m2")
    print("\nMIX SENSITIVITY (vary the 60/40 split, total ~26):")
    for a,b in [(18,8),(16,10),(14,12)]:
        r = feaso(n_1bed=a, n_dk=b)
        print(f"  {a} x 1-bed + {b} x dual-key -> margin {r['margin']}%, land ${r['land_psm']:,}/m2")
