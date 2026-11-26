# Full review diff for PR 706

The comparison covers base `51e475ad077ec88d60f9e8c561dc0415ca9855aa` and head `d8131f62dad69e63c81562f2ffa4c626b676bf9c`. The 32 numbered text files contain every hunk of the GitHub API unified diff. Read the parts in order; each is at most 6,500 bytes and ends on a full line. [Pull request](https://github.com/InferMatrixLab/InferRSI/pull/706)

The GitHub file manifests report 38 files, 3,434 added lines and 46 deleted lines. Each API patch was checked against its reported counts. The concatenated parts reproduce all 206,863 bytes and 4,156 lines of the API diff, SHA-256 `cdc0d70db5a3d0c23d06e6eef4c42781d28da68b4d6813c9a1bd85e02b7537de`. Applying the full patch to the base Git index reproduced the exact tree of the reviewed head.

```sh
cat [0-9][0-9].patch > full.diff
shasum -a 256 full.diff
git -C <clean-checkout-at-base> apply --check < full.diff
```

| Part | Original diff lines | Bytes |
| --- | --- | ---: |
| [01.patch](01.patch) | 1–75 | 6472 |
| [02.patch](02.patch) | 76–195 | 6492 |
| [03.patch](03.patch) | 196–311 | 6499 |
| [04.patch](04.patch) | 312–414 | 6494 |
| [05.patch](05.patch) | 415–528 | 6465 |
| [06.patch](06.patch) | 529–648 | 6472 |
| [07.patch](07.patch) | 649–778 | 6436 |
| [08.patch](08.patch) | 779–934 | 6427 |
| [09.patch](09.patch) | 935–1093 | 6500 |
| [10.patch](10.patch) | 1094–1220 | 6447 |
| [11.patch](11.patch) | 1221–1357 | 6448 |
| [12.patch](12.patch) | 1358–1495 | 6475 |
| [13.patch](13.patch) | 1496–1627 | 6476 |
| [14.patch](14.patch) | 1628–1788 | 6444 |
| [15.patch](15.patch) | 1789–1926 | 6496 |
| [16.patch](16.patch) | 1927–2054 | 6471 |
| [17.patch](17.patch) | 2055–2169 | 6438 |
| [18.patch](18.patch) | 2170–2286 | 6487 |
| [19.patch](19.patch) | 2287–2414 | 6435 |
| [20.patch](20.patch) | 2415–2606 | 6487 |
| [21.patch](21.patch) | 2607–2753 | 6479 |
| [22.patch](22.patch) | 2754–2862 | 6480 |
| [23.patch](23.patch) | 2863–2987 | 6483 |
| [24.patch](24.patch) | 2988–3122 | 6475 |
| [25.patch](25.patch) | 3123–3250 | 6428 |
| [26.patch](26.patch) | 3251–3382 | 6457 |
| [27.patch](27.patch) | 3383–3514 | 6471 |
| [28.patch](28.patch) | 3515–3627 | 6445 |
| [29.patch](29.patch) | 3628–3744 | 6484 |
| [30.patch](30.patch) | 3745–3868 | 6479 |
| [31.patch](31.patch) | 3869–4005 | 6428 |
| [32.patch](32.patch) | 4006–4156 | 6393 |
