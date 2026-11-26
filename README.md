# Full review diff for PR 706

The comparison covers base `51e475ad077ec88d60f9e8c561dc0415ca9855aa` and head `694ec791f5dde3f1aeee888551157a5fabfa10f3`. The 30 numbered text files contain every hunk of the GitHub API unified diff. Read the parts in order; each is at most 6,500 bytes and ends on a full line. [Pull request](https://github.com/InferMatrixLab/InferRSI/pull/706)

The GitHub file manifests report 37 files, 3,268 added lines and 35 deleted lines. Each API patch was checked against its reported counts. The concatenated parts reproduce all 189,953 bytes and 3,876 lines of the API diff, SHA-256 `786ab1ab826a1851f9683fda79b3c8a941815f6fa2d04752b6aa4be0b9ff0bb2`. Applying the full patch to the base Git index reproduced the exact tree of the reviewed head.

```sh
cat [0-9][0-9].patch > full.diff
shasum -a 256 full.diff
git -C <clean-checkout-at-base> apply --check < full.diff
```

| Part | Original diff lines | Bytes |
| --- | --- | ---: |
| [01.patch](01.patch) | 1–78 | 6431 |
| [02.patch](02.patch) | 79–207 | 6483 |
| [03.patch](03.patch) | 208–318 | 6438 |
| [04.patch](04.patch) | 319–421 | 6451 |
| [05.patch](05.patch) | 422–535 | 6467 |
| [06.patch](06.patch) | 536–678 | 6497 |
| [07.patch](07.patch) | 679–830 | 6500 |
| [08.patch](08.patch) | 831–973 | 6479 |
| [09.patch](09.patch) | 974–1122 | 6496 |
| [10.patch](10.patch) | 1123–1260 | 6492 |
| [11.patch](11.patch) | 1261–1385 | 6487 |
| [12.patch](12.patch) | 1386–1526 | 6451 |
| [13.patch](13.patch) | 1527–1684 | 6453 |
| [14.patch](14.patch) | 1685–1815 | 6471 |
| [15.patch](15.patch) | 1816–1949 | 6459 |
| [16.patch](16.patch) | 1950–2070 | 6465 |
| [17.patch](17.patch) | 2071–2191 | 6495 |
| [18.patch](18.patch) | 2192–2321 | 6480 |
| [19.patch](19.patch) | 2322–2511 | 6472 |
| [20.patch](20.patch) | 2512–2656 | 6495 |
| [21.patch](21.patch) | 2657–2783 | 6463 |
| [22.patch](22.patch) | 2784–2929 | 6481 |
| [23.patch](23.patch) | 2930–3048 | 6445 |
| [24.patch](24.patch) | 3049–3183 | 6491 |
| [25.patch](25.patch) | 3184–3306 | 6500 |
| [26.patch](26.patch) | 3307–3419 | 6456 |
| [27.patch](27.patch) | 3420–3542 | 6467 |
| [28.patch](28.patch) | 3543–3673 | 6482 |
| [29.patch](29.patch) | 3674–3824 | 6464 |
| [30.patch](30.patch) | 3825–3876 | 2242 |
