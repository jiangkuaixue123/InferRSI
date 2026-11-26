# Full review diff for PR 706

The comparison covers base `51e475ad077ec88d60f9e8c561dc0415ca9855aa` and head `a8b619985bbb86fe16906c071e3ced83eec85b93`. The 36 numbered text files contain every hunk of the GitHub API unified diff. Read the parts in order; each is at most 6,500 bytes and ends on a full line. [Pull request](https://github.com/InferMatrixLab/InferRSI/pull/706)

The GitHub file manifests report 40 files, 3,679 added lines and 57 deleted lines. Each API patch was checked against its reported counts. The concatenated parts reproduce all 227,854 bytes and 4,542 lines of the API diff, SHA-256 `8182418d03eca21916461df6de69acdcbde2909d81f19992f94bd03186831697`. Applying the full patch to the base Git index reproduced the exact tree of the reviewed head.

```sh
cat [0-9][0-9].patch > full.diff
shasum -a 256 full.diff
git -C <clean-checkout-at-base> apply --check < full.diff
```

| Part | Original diff lines | Bytes |
| --- | --- | ---: |
| [01.patch](01.patch) | 1–75 | 6472 |
| [02.patch](02.patch) | 76–167 | 6476 |
| [03.patch](03.patch) | 168–293 | 6459 |
| [04.patch](04.patch) | 294–399 | 6468 |
| [05.patch](05.patch) | 400–499 | 6442 |
| [06.patch](06.patch) | 500–614 | 6472 |
| [07.patch](07.patch) | 615–750 | 6491 |
| [08.patch](08.patch) | 751–903 | 6473 |
| [09.patch](09.patch) | 904–1041 | 6499 |
| [10.patch](10.patch) | 1042–1193 | 6453 |
| [11.patch](11.patch) | 1194–1328 | 6444 |
| [12.patch](12.patch) | 1329–1455 | 6500 |
| [13.patch](13.patch) | 1456–1587 | 6497 |
| [14.patch](14.patch) | 1588–1743 | 6434 |
| [15.patch](15.patch) | 1744–1884 | 6457 |
| [16.patch](16.patch) | 1885–2029 | 6454 |
| [17.patch](17.patch) | 2030–2151 | 6499 |
| [18.patch](18.patch) | 2152–2273 | 6453 |
| [19.patch](19.patch) | 2274–2387 | 6488 |
| [20.patch](20.patch) | 2388–2517 | 6496 |
| [21.patch](21.patch) | 2518–2702 | 6456 |
| [22.patch](22.patch) | 2703–2859 | 6447 |
| [23.patch](23.patch) | 2860–2973 | 6467 |
| [24.patch](24.patch) | 2974–3086 | 6496 |
| [25.patch](25.patch) | 3087–3218 | 6444 |
| [26.patch](26.patch) | 3219–3346 | 6456 |
| [27.patch](27.patch) | 3347–3481 | 6471 |
| [28.patch](28.patch) | 3482–3613 | 6462 |
| [29.patch](29.patch) | 3614–3742 | 6459 |
| [30.patch](30.patch) | 3743–3857 | 6452 |
| [31.patch](31.patch) | 3858–3973 | 6473 |
| [32.patch](32.patch) | 3974–4098 | 6444 |
| [33.patch](33.patch) | 4099–4217 | 6485 |
| [34.patch](34.patch) | 4218–4355 | 6455 |
| [35.patch](35.patch) | 4356–4514 | 6488 |
| [36.patch](36.patch) | 4515–4542 | 1472 |
