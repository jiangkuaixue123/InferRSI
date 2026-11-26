# Full review diff for PR 706

The comparison covers base `51e475ad077ec88d60f9e8c561dc0415ca9855aa` and head `0fb750231a94174fc26b092e5d526280dfbbb349`. The 31 numbered text files contain every hunk of the GitHub API unified diff. Read the parts in order; each is at most 6,500 bytes and ends on a full line. [Pull request](https://github.com/InferMatrixLab/InferRSI/pull/706)

The GitHub file manifests report 37 files, 3,350 added lines and 35 deleted lines. Each API patch was checked against its reported counts. The concatenated parts reproduce all 194,534 bytes and 3,958 lines of the API diff, SHA-256 `725a86a3875ea2f363c0909c7ad8c246cbbc467572e527cce93ad06b807d2292`. Applying the full patch to the base Git index reproduced the exact tree of the reviewed head.

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
| [04.patch](04.patch) | 319–418 | 6428 |
| [05.patch](05.patch) | 419–534 | 6451 |
| [06.patch](06.patch) | 535–677 | 6477 |
| [07.patch](07.patch) | 678–824 | 6487 |
| [08.patch](08.patch) | 825–966 | 6463 |
| [09.patch](09.patch) | 967–1109 | 6481 |
| [10.patch](10.patch) | 1110–1244 | 6466 |
| [11.patch](11.patch) | 1245–1378 | 6431 |
| [12.patch](12.patch) | 1379–1507 | 6494 |
| [13.patch](13.patch) | 1508–1665 | 6489 |
| [14.patch](14.patch) | 1666–1798 | 6462 |
| [15.patch](15.patch) | 1799–1941 | 6437 |
| [16.patch](16.patch) | 1942–2064 | 6486 |
| [17.patch](17.patch) | 2065–2174 | 6472 |
| [18.patch](18.patch) | 2175–2306 | 6461 |
| [19.patch](19.patch) | 2307–2473 | 6453 |
| [20.patch](20.patch) | 2474–2650 | 6429 |
| [21.patch](21.patch) | 2651–2768 | 6499 |
| [22.patch](22.patch) | 2769–2905 | 6457 |
| [23.patch](23.patch) | 2906–3042 | 6459 |
| [24.patch](24.patch) | 3043–3168 | 6491 |
| [25.patch](25.patch) | 3169–3296 | 6494 |
| [26.patch](26.patch) | 3297–3419 | 6485 |
| [27.patch](27.patch) | 3420–3535 | 6455 |
| [28.patch](28.patch) | 3536–3658 | 6461 |
| [29.patch](29.patch) | 3659–3788 | 6469 |
| [30.patch](30.patch) | 3789–3949 | 6466 |
| [31.patch](31.patch) | 3950–3958 | 579 |
