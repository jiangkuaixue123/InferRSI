# Full review diff for PR 706

The comparison covers base `51e475ad077ec88d60f9e8c561dc0415ca9855aa` and head `1a005543b28dcf130dd2a26da4f65b5c9d7963a7`. The 32 numbered text files contain every hunk of the GitHub API unified diff. Read the parts in order; each is at most 6,500 bytes and ends on a full line. [Pull request](https://github.com/InferMatrixLab/InferRSI/pull/706)

The GitHub file manifests report 37 files, 3,427 added lines and 45 deleted lines. Each API patch was checked against its reported counts. The concatenated parts reproduce all 205,481 bytes and 4,137 lines of the API diff, SHA-256 `5a3223b0a0c382b79c7d2cec90ad10c76f0c9c406ed436948c8ca8e1fd0a1b90`. Applying the full patch to the base Git index reproduced the exact tree of the reviewed head.

```sh
cat [0-9][0-9].patch > full.diff
shasum -a 256 full.diff
git -C <clean-checkout-at-base> apply --check < full.diff
```

| Part | Original diff lines | Bytes |
| --- | --- | ---: |
| [01.patch](01.patch) | 1–75 | 6472 |
| [02.patch](02.patch) | 76–195 | 6457 |
| [03.patch](03.patch) | 196–311 | 6499 |
| [04.patch](04.patch) | 312–413 | 6483 |
| [05.patch](05.patch) | 414–526 | 6413 |
| [06.patch](06.patch) | 527–646 | 6472 |
| [07.patch](07.patch) | 647–779 | 6425 |
| [08.patch](08.patch) | 780–935 | 6482 |
| [09.patch](09.patch) | 936–1094 | 6466 |
| [10.patch](10.patch) | 1095–1220 | 6469 |
| [11.patch](11.patch) | 1221–1355 | 6464 |
| [12.patch](12.patch) | 1356–1495 | 6465 |
| [13.patch](13.patch) | 1496–1627 | 6456 |
| [14.patch](14.patch) | 1628–1791 | 6482 |
| [15.patch](15.patch) | 1792–1929 | 6481 |
| [16.patch](16.patch) | 1930–2053 | 6435 |
| [17.patch](17.patch) | 2054–2169 | 6465 |
| [18.patch](18.patch) | 2170–2290 | 6495 |
| [19.patch](19.patch) | 2291–2420 | 6480 |
| [20.patch](20.patch) | 2421–2610 | 6472 |
| [21.patch](21.patch) | 2611–2754 | 6498 |
| [22.patch](22.patch) | 2755–2863 | 6470 |
| [23.patch](23.patch) | 2864–2987 | 6465 |
| [24.patch](24.patch) | 2988–3133 | 6454 |
| [25.patch](25.patch) | 3134–3259 | 6482 |
| [26.patch](26.patch) | 3260–3391 | 6488 |
| [27.patch](27.patch) | 3392–3517 | 6443 |
| [28.patch](28.patch) | 3518–3631 | 6425 |
| [29.patch](29.patch) | 3632–3751 | 6458 |
| [30.patch](30.patch) | 3752–3883 | 6490 |
| [31.patch](31.patch) | 3884–4014 | 6477 |
| [32.patch](32.patch) | 4015–4137 | 4998 |
