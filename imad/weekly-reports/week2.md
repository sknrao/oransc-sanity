# O-RAN-SC CVE  
**Week Starting: 08 Sept**

---

## Updates
- Identified repositories active in the last 3 years but not yet scanned (using the Activity Report Summary
).
- Built the [Nexus IQ patch table](../docs/nexus-iq-table.md) (Repo Name, Patch Link, PTL Approval, Issues).
- Tried understanding synk
- created a [script](../scripts/synk.sh) to scan the active repos using synk (the script has issues, needs to be fixed, have to debug further)
- Completed Grype scans for the remaining active repositories.
- Click to view grype scan reports:
    - [aimlfw-dep](../cve-scan-results/)
    - [awmf/tm](../cve-scan-results/tm.md)
    - [it/test](../cve-scan-results/it-test.md)
    - [plt/rappmanager](../cve-scan-results/rappmanager.md)
    - [oam](../cve-scan-results/oam.md)
    - [smo/teiv](../cve-scan-results/teiv.md)

---

## Challenges
- the synk script has issues, needs to be fixed

---

## Support Required
- Reacing out to the PTLs
