# PSI-MOD Validation Report

## Summary

- Terms checked: **1978**
- Errors: **9**
- Warnings: **67**
- Info: **0**
- Fixable: **68**

## Issues

| Severity | ID | Category | Message |
|----------|-----|----------|---------|
| WARNING | MOD:00010 | smiles | SMILES not in canonical form: `C[C@H](N-*)C(-*)=O` -> `*N[C@@H](C)C(*)=O` |
| WARNING | MOD:00011 | smiles | SMILES not in canonical form: `NC(N)=NCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCN=C(N)N)C(*)=O` |
| WARNING | MOD:00012 | smiles | SMILES not in canonical form: `NC(=O)C[C@H](N-*)C(-*)=O` -> `*N[C@@H](CC(N)=O)C(*)=O` |
| WARNING | MOD:00013 | smiles | SMILES not in canonical form: `OC(=O)C[C@H](N-*)C(-*)=O` -> `*N[C@@H](CC(=O)O)C(*)=O` |
| WARNING | MOD:00014 | smiles | SMILES not in canonical form: `SC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CS)C(*)=O` |
| WARNING | MOD:00015 | smiles | SMILES not in canonical form: `OC(=O)CC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCC(=O)O)C(*)=O` |
| WARNING | MOD:00016 | smiles | SMILES not in canonical form: `NC(=O)CC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCC(N)=O)C(*)=O` |
| ERROR | MOD:00571 | mass | MassMono mismatch: SMILES gives 111.032028, annotation says 112.039853 (diff: 1.007825 Da) |
| ERROR | MOD:00571 | mass | Formula mismatch: SMILES gives C 5 H 5 N 1 O 2, annotation says C 5 H 6 N 1 O 2 |
| WARNING | MOD:00648 | smiles | SMILES not in canonical form: `CC(=O)N[C@@H](COC(C)=O)C(-*)=O` -> `*C(=O)[C@H](COC(C)=O)NC(C)=O` |
| WARNING | MOD:00719 | smiles | SMILES not in canonical form: `CS(=O)CC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCS(C)=O)C(*)=O` |
| WARNING | MOD:00719 | smiles | Undefined stereocenter(s) at atom index(es): 1 |
| WARNING | MOD:00720 | smiles | SMILES not in canonical form: `C(*)(=O)[C@@H](N*)CC[S@](=O)C` -> `*N[C@@H](CC[S@@](C)=O)C(*)=O` |
| WARNING | MOD:00721 | smiles | SMILES not in canonical form: `C(*)(=O)[C@@H](N*)CC[S@@](=O)C` -> `*N[C@@H](CC[S@](C)=O)C(*)=O` |
| WARNING | MOD:00855 | smiles | SMILES not in canonical form: `C[N+](C)(C)CCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCC[N+](C)(C)C)C(*)=O` |
| WARNING | MOD:01048 | smiles | SMILES not in canonical form: `*-C(=O)[C@@H]1CCC(=O)N1` -> `*C(=O)[C@@H]1CCC(=O)N1` |
| WARNING | MOD:01060 | smiles | SMILES not in canonical form: `NC(=O)CSC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CSCC(N)=O)C(*)=O` |
| WARNING | MOD:01171 | smiles | SMILES not in canonical form: `C[C@@H](OC(C)=O)[C@H](N-*)C(-*)=O` -> `*N[C@H](C(*)=O)[C@@H](C)OC(C)=O` |
| WARNING | MOD:01221 | smiles | SMILES not in canonical form: `C[C@@H](OC=O)[C@H](N-*)C(-*)=O` -> `*N[C@H](C(*)=O)[C@@H](C)OC=O` |
| WARNING | MOD:01222 | smiles | SMILES not in canonical form: `*-N[C@@H](COC=O)C(-*)=O` -> `*N[C@@H](COC=O)C(*)=O` |
| WARNING | MOD:01228 | smiles | SMILES not in canonical form: `Oc1ccc(C[C@H](N-*)C(-*)=O)cc1I` -> `*N[C@@H](Cc1ccc(O)c(I)c1)C(*)=O` |
| WARNING | MOD:01398 | smiles | SMILES not in canonical form: `CCC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)CC)C(*)=O` |
| WARNING | MOD:00038 | smiles | Undefined stereocenter(s) at atom index(es): 4 |
| WARNING | MOD:00039 | smiles | Undefined stereocenter(s) at atom index(es): 5 |
| WARNING | MOD:00040 | smiles | SMILES not in canonical form: `*-C(=O)[C@@H]1CCC(=O)N1` -> `*C(=O)[C@@H]1CCC(=O)N1` |
| WARNING | MOD:00050 | smiles | SMILES not in canonical form: `C[C@H](NC(C)=O)C(-*)=O` -> `*C(=O)[C@H](C)NC(C)=O` |
| WARNING | MOD:01781 | smiles | SMILES not in canonical form: `C(*)([C@@H](N*)CCCCNC(CCC)=O)=O` -> `*N[C@@H](CCCCNC(=O)CCC)C(*)=O` |
| WARNING | MOD:01819 | smiles | SMILES not in canonical form: `OC(=O)CCC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)CCC(=O)O)C(*)=O` |
| WARNING | MOD:01892 | smiles | SMILES not in canonical form: `CC=CC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)C=CC)C(*)=O` |
| WARNING | MOD:01893 | smiles | SMILES not in canonical form: `OC(=O)CC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)CC(=O)O)C(*)=O` |
| WARNING | MOD:02095 | smiles | SMILES not in canonical form: `OC(=O)CCCC(=O)NCCCC[C@H](N*)C(*)=O` -> `*N[C@@H](CCCCNC(=O)CCCC(=O)O)C(*)=O` |
| WARNING | MOD:00057 | smiles | SMILES not in canonical form: `CC(=O)N[C@@H](CCCCN)C(-*)=O` -> `*C(=O)[C@H](CCCCN)NC(C)=O` |
| WARNING | MOD:00059 | smiles | SMILES not in canonical form: `CC(=O)N1CCC[C@H]1C(-*)=O` -> `*C(=O)[C@@H]1CCCN1C(C)=O` |
| WARNING | MOD:00064 | smiles | SMILES not in canonical form: `CC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(C)=O)C(*)=O` |
| WARNING | MOD:00460 | smiles | SMILES not in canonical form: `OS(=O)(=O)C[C@H](N-*)C(-*)=O` -> `*N[C@@H](CS(=O)(=O)O)C(*)=O` |
| WARNING | MOD:00464 | smiles | SMILES not in canonical form: `[H]C(=O)Nc1ccccc1C(=O)C[C@H](N-*)C(-*)=O` -> `*N[C@@H](CC(=O)c1ccccc1NC=O)C(*)=O` |
| WARNING | MOD:00076 | charge | SMILES has formal charge 1 but no FormalCharge annotation |
| ERROR | MOD:00076 | mass | MassMono mismatch: SMILES gives 185.140236, annotation says 184.132411 (diff: 1.007825 Da) |
| ERROR | MOD:00076 | mass | Formula mismatch: SMILES gives C 8 H 17 N 4 O 1, annotation says C 8 H 16 N 4 O 1 |
| WARNING | MOD:00077 | charge | SMILES has formal charge 1 but no FormalCharge annotation |
| ERROR | MOD:00077 | mass | MassMono mismatch: SMILES gives 185.140236, annotation says 184.132411 (diff: 1.007825 Da) |
| ERROR | MOD:00077 | mass | Formula mismatch: SMILES gives C 8 H 17 N 4 O 1, annotation says C 8 H 16 N 4 O 1 |
| WARNING | MOD:00078 | smiles | SMILES not in canonical form: `CNC(=N)NCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCNC(=N)NC)C(*)=O` |
| WARNING | MOD:00083 | smiles | SMILES not in canonical form: `C[N+](C)(C)CCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCC[N+](C)(C)C)C(*)=O` |
| WARNING | MOD:00084 | smiles | SMILES not in canonical form: `C(N(C)C)CCC[C@@H](C(*)=O)N*` -> `*N[C@@H](CCCCN(C)C)C(*)=O` |
| ERROR | MOD:00327 | smiles | Invalid SMILES (RDKit cannot parse): `*N[C@H](C(*)=O)C(O)c1cnc2ccccc12` |
| WARNING | MOD:00216 | smiles | SMILES not in canonical form: `C(*)([C@@H](N*)CCCCNC([H])=O)=O` -> `*N[C@@H](CCCCNC=O)C(*)=O` |
| WARNING | MOD:00126 | smiles | SMILES not in canonical form: `*-N[C@@H](CCCCNC(=O)CCCC[C@@H]1SC[C@@H]2NC(=O)N[C@H]12)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)CCCC[C@@H]1SC[C@@H]2NC(=O)N[C@@H]21)C(*)=O` |
| WARNING | MOD:00420 | smiles | SMILES not in canonical form: `*-C(=O)[C@@H]1CCC(=O)N1` -> `*C(=O)[C@@H]1CCC(=O)N1` |
| WARNING | MOD:00477 | smiles | SMILES not in canonical form: `OC1C[C@H](N(-*)C1)C(-*)=O` -> `*C(=O)[C@@H]1CC(O)CN1*` |
| WARNING | MOD:00477 | smiles | Undefined stereocenter(s) at atom index(es): 1 |
| ERROR | MOD:00477 | mass | MassMono mismatch: SMILES gives 113.047678, annotation says 84.044939 (diff: 29.002739 Da) |
| ERROR | MOD:00477 | mass | Formula mismatch: SMILES gives C 5 H 7 N 1 O 2, annotation says C 4 H 6 N 1 O 1 |
| WARNING | MOD:00478 | smiles | SMILES not in canonical form: `*N[C@@H](CCC([H])=O)C(*)=O` -> `*N[C@@H](CCC=O)C(*)=O` |
| WARNING | MOD:00479 | smiles | SMILES not in canonical form: `*N[C@@H](CCC([H])=O)C(*)=O` -> `*N[C@@H](CCC=O)C(*)=O` |
| WARNING | MOD:00492 | smiles | SMILES not in canonical form: `NCC(=O)NCC(=O)NCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC(=O)CNC(=O)CN)C(*)=O` |
| WARNING | MOD:00277 | smiles | SMILES not in canonical form: `CC(CC[C@H](N-*)C(-*)=O)NC(N)=N` -> `*N[C@@H](CCC(C)NC(=N)N)C(*)=O` |
| WARNING | MOD:00277 | smiles | Undefined stereocenter(s) at atom index(es): 1 |
| WARNING | MOD:00310 | smiles | SMILES not in canonical form: `CN(CCC[C@H](N-*)C(-*)=O)C(N)=N` -> `*N[C@@H](CCCN(C)C(=N)N)C(*)=O` |
| WARNING | MOD:00085 | smiles | SMILES not in canonical form: `CNCCCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCCCNC)C(*)=O` |
| WARNING | MOD:00096 | smiles | SMILES not in canonical form: `NC(=O)[C@H](CCC(O)=O)N-*` -> `*N[C@@H](CCC(=O)O)C(N)=O` |
| WARNING | MOD:00017 | smiles | SMILES not in canonical form: `*-NCC(-*)=O` -> `*NCC(*)=O` |
| WARNING | MOD:00018 | smiles | SMILES not in canonical form: `*-N[C@@H](Cc1cnc[nH]1)C(-*)=O` -> `*N[C@@H](Cc1cnc[nH]1)C(*)=O` |
| WARNING | MOD:00019 | smiles | SMILES not in canonical form: `CC[C@H](C)[C@H](N-*)C(-*)=O` -> `*N[C@H](C(*)=O)[C@@H](C)CC` |
| WARNING | MOD:00020 | smiles | SMILES not in canonical form: `CC(C)C[C@H](N-*)C(-*)=O` -> `*N[C@@H](CC(C)C)C(*)=O` |
| WARNING | MOD:00021 | smiles | SMILES not in canonical form: `NCCCCC(N-*)C(-*)=O` -> `*NC(CCCCN)C(*)=O` |
| WARNING | MOD:00021 | smiles | Undefined stereocenter(s) at atom index(es): 5 |
| WARNING | MOD:00022 | smiles | SMILES not in canonical form: `CSCC[C@H](N-*)C(-*)=O` -> `*N[C@@H](CCSC)C(*)=O` |
| WARNING | MOD:00023 | smiles | SMILES not in canonical form: `*-N[C@@H](Cc1ccccc1)C(-*)=O` -> `*N[C@@H](Cc1ccccc1)C(*)=O` |
| WARNING | MOD:00024 | smiles | SMILES not in canonical form: `*-N1CCC[C@H]1C(-*)=O` -> `*C(=O)[C@@H]1CCCN1*` |
| WARNING | MOD:00025 | smiles | SMILES not in canonical form: `OCC(N-*)C(-*)=O` -> `*NC(CO)C(*)=O` |
| WARNING | MOD:00025 | smiles | Undefined stereocenter(s) at atom index(es): 2 |
| WARNING | MOD:00026 | smiles | SMILES not in canonical form: `C[C@@H](O)[C@H](N-*)C(-*)=O` -> `*N[C@H](C(*)=O)[C@@H](C)O` |
| WARNING | MOD:00027 | smiles | SMILES not in canonical form: `*-N[C@@H](Cc1c[nH]c2ccccc12)C(-*)=O` -> `*N[C@@H](Cc1c[nH]c2ccccc12)C(*)=O` |
| WARNING | MOD:00028 | smiles | SMILES not in canonical form: `Oc1ccc(C[C@H](N-*)C(-*)=O)cc1` -> `*N[C@@H](Cc1ccc(O)cc1)C(*)=O` |
| WARNING | MOD:00029 | smiles | SMILES not in canonical form: `CC(C)[C@H](N-*)C(-*)=O` -> `*N[C@H](C(*)=O)C(C)C` |