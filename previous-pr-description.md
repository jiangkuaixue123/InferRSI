## Governing Issue and delivery slice

Refs #606

The issue author requested this implementation for review. The [scope decision](https://github.com/InferMatrixLab/InferRSI/issues/606#issuecomment-7166237001) accepts the first-phase design. The implementation and acceptance owners have yet to be recorded on the issue.

The existing primary-task router selects the task. The new `task intake evaluate`, `answer` and `summary` commands track field sources, conflicts, unknown values and the stages they block. Performance and Day-0 have field specifications. Interactive performance work now requires a numeric final goal, a quantitative quality gate on a named benchmark, and a separate approval of the full task brief before measurement. Anchors touched: none.

## Knowledge authorship declaration

```knowledge-model-policy
{
  "schema_version": 1,
  "head_sha": "2a5347959f3219afaf7df3625c39d066f5bbef03",
  "human_only": false,
  "material_ai_authors": [
    {
      "tool": "Claude Code",
      "model_id": "claude-fable-5-2",
      "effort": "xhigh",
      "role": "author"
    },
    {
      "tool": "Codex",
      "model_id": "gpt-6.2-astra",
      "effort": "xhigh",
      "role": "author"
    },
    {
      "tool": "Claude Code",
      "model_id": "claude-opus-5-5",
      "effort": "low",
      "role": "author"
    },
    {
      "tool": "Codex",
      "model_id": "unknown",
      "effort": "unknown",
      "role": "author"
    }
  ],
  "exception": {
    "paths": [
      "src/inferrsi/knowledge/data/skill_library/_compiled/_provenance.json",
      "src/inferrsi/knowledge/data/skill_library/_compiled/inputs.json",
      "src/inferrsi/knowledge/data/skill_library/tasks/inference-task-router/SKILL.md",
      "src/inferrsi/knowledge/data/skill_library/tasks/task-day-0/intake.json",
      "src/inferrsi/knowledge/data/skill_library/tasks/task-performance/SKILL.md",
      "src/inferrsi/knowledge/data/skill_library/tasks/task-performance/intake.json"
    ],
    "reason": "The protected knowledge files and generated indexes carry forward the earlier declared authorship. Claude Code with claude-opus-5-5 at low effort contributed follow-up tests and non-knowledge intake code. The Codex session that integrated the Harness refactor has an unknown exact model identifier and effort. Both contributions are disclosed here."
  }
}
```

Codex added the wheel resource checks, the user selection and gate-source handling, the desktop instructions, the quantified brief and its revision-specific approval, and regression tests.

## Verification on `2a534795`

- Synchronized with main at `ba4637e2`. Apps binds the approved brief to the staged plan. Harness Manager stages and initializes the campaign, and Evaluator applies the frozen quality and final performance conditions in both modes. Recorded service plans created before intake retain their native scoring scale.
- **153 focused tests passed** on macOS/Python 3.12. They covered the packaged execution bounds, old-record reopening, stale field replies, the AB/BA prepare → approve → start → score controls, and service-reuse pre-start and scorer checks. Ruff, the compiled skill index, coverage and SearchSpace projection checks passed.
- An isolated wheel smoke test verified **777 resources**. The installed CLI refused the old P95 reply after reissuing the P99 question, preserved the sibling card, and accepted the current reply. The full Linux jobs are in progress. This run did not replay Codex Desktop or run model/device acceptance. [Ready CI](https://github.com/InferMatrixLab/InferRSI/actions/runs/45929753371)
- The [review patches](https://github.com/jiangkuaixue123/InferRSI/blob/d3678aa6ef62e30fbd3c1071adaea137f20c8182/README.md) provide the full diff from `ba4637e2` and the earlier `d8131f62..9541e173` increment. Each part is at most 4,500 bytes. Both patches reconstructed the exact target Git tree.
- The declaration below requests owner approval for a knowledge-policy exception on this head. The attribution includes the follow-up and integration authors.

## Earlier verification on `a8b61998`

- **Quality units.** `7407ab71` binds the unit before the final approval, freezes it in AB/BA and checks the service configuration against it. Each numeric scorer receipt reports its unit. The evaluator converts an explicit fraction or ratio to the approved percent scale, rejects missing or incompatible units, and retains the raw receipt. Absolute error ≤ 1% rejects 0.02 fraction and accepts 0.005. Baseline tolerances compare both scores on the same scale and use an additive difference; 2% + 1 percentage point permits 3%. Both CLI entry points exercise prepare, approval and start. The lifecycle regressions also check candidate retention and independent final evaluation. [Unit finding](https://github.com/InferMatrixLab/InferRSI/pull/706#discussion_r4707999117)
- **Delayed card replies.** `a8b61998` binds each field token to its record, dependencies, wording, options and issuance revision. The P95 reply is rejected after the P99 question is reissued, with the record byte-for-byte unchanged. A sibling card with unchanged context remains usable, and the new P99 card accepts the reply. Separate cases cover foreign records, changed conflict options and open cards saved by older versions. Settled legacy answers retain their provenance. Removed the unused `set_primary_task()` helper mentioned in the review. [Stale-reply finding](https://github.com/InferMatrixLab/InferRSI/pull/706#discussion_r4707999123) · [Reviewer’s earlier CLI reproduction](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6073701594)
- **Local environment.** macOS, Python 3.12.13, pytest 9.2.0, Git 2.50.1. The focused selection recorded 139 passed, 1 Linux-only skip and 94 deselected. Ruff 0.17.6 (`ruff check src tests tools`), the declared-source skill index and skill coverage passed.
- The two review reproductions and their variants ran separately on this commit, with **13 passed**. An isolated installation verified 777 package resources and repeated the P95→P99 sequence via the installed CLI: stale delivery returned exit 2 without changing the record, the unrelated card kept its token, and the current card accepted its reply.
- macOS full suite (`pytest`) finished with **7,466 passed, 103 skipped, 136 failed and 675 passing subtests**. All 136 failing IDs match the 136 independently reproduced on the clean base on this host, with zero additions and zero removals. The local service lifecycle could not establish process cleanup on this host; its end-to-end result is tracked separately in Linux CI.
- **Boundaries on the new head.** The isolated wheel maps repetitions and rounds to `integer / task-input/v1 / count`, and max_minutes to `number / task-input/v1 / minutes`. The CLI regressions for both new answers and old approved records ran again: **6 passed**. [Exact tests](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_task_intake.py#L658-L709).
- **Increment for re-review.** The 14 changed files since `d8131f62` are preserved in [11 plain-text patches](https://github.com/jiangkuaixue123/InferRSI/blob/441444992849deb193ee86f646e50ab7c0834c24/increment/README.md). Each file is at most 4,500 bytes with real newlines. Concatenating them reproduces all 45,379 bytes / 802 lines and applying the patch reconstructs `a8b61998`.
- Both Linux matrix jobs are running. [Ready CI on this head](https://github.com/InferMatrixLab/InferRSI/actions/runs/45817603851).

## Changed artifacts and evidence

- `src/inferrsi/apps/cli/intake_contract.py` and `task_intake.py` implement the record and CLI. A card answer can propose an acceptance value. Intake binds issue values to the reference the user identified and frozen values to the selected file’s acceptance snapshot. Discovered performance choices become card suggestions. A changed file reopens the reference question.
- Every ordinary performance `campaign start` requires a matching preapproval. Preparation stages the executable settings, the final card binds them, and start compares the staged settings and approved conditions before creating the campaign. The frozen plan references the intake receipt with its brief ID, revision and SHA-256.
- `tests/apps/test_task_intake.py` exercises question selection, stale and duplicate replies, frozen-gate disagreement and campaign start. The previous CLI vague-prompt trial exercised the numbered fallback.

- The final brief includes the absolute metric bound or baseline-relative gain, quality benchmark, metric, comparison, threshold and unit, plus the applicable protocol, scope and budget. The host presents the brief in the user's language and asks for a separate approve-or-revise response. An edit invalidates the old question. Intake rechecks the selected local gate before campaign start and serializes record updates.
- Brief approval records an explicit host-delivered user response. Service and device execution still require their own authorization.

## Review follow-up

- [Resolving conflicting metric choices](https://github.com/InferMatrixLab/InferRSI/pull/706#discussion_r4703653221). An open card retains distinct alternatives across repeated imports. Selecting either metric resolves the card and leaves the choice proposed. The selected issue can confirm the matching value. An issue that disagrees with an explicit card choice opens a new conflict. CLI regressions exercise both P95 and P99 choices through authority confirmation.
- [Execution bounds before approval](https://github.com/InferMatrixLab/InferRSI/pull/706#discussion_r4704360688). New field values and card replies use the task-input/v1 numeric rules. Repetitions and rounds must be positive integers, minutes must be positive and at most seven days, and the minimum improvement percentage must be nonnegative. Reading an older record with an out-of-range value withdraws its approval and reopens the question. Regression tests also exercise failed campaign start, correction and a new final card.

## Earlier review on `d8131f62`

Linux Ready CI passed on `d8131f62`. Python 3.10 and 3.11 each recorded **7,603 passed, 89 skipped, one deselected and 675 passing subtests**. Both installed-package jobs, dashboard-browser and the advisory Windows and macOS jobs passed. The conditional skill-acceptance execution was skipped. [Python 3.10](https://github.com/InferMatrixLab/InferRSI/actions/runs/45788580340/job/139801545557) · [Python 3.11](https://github.com/InferMatrixLab/InferRSI/actions/runs/45788580340/job/139801545014)

`d8131f62` updates the ranking-policy parity assertion to check the entire quality receipt, including the approved dataset. The AB/BA guide now identifies the corpus label as self-reported and distinguishes an unscored explicit rejection from a scored receipt with missing identity. These four files are the entire increment since the formally reviewed `1a005543`. Production Python on these two heads is identical. [Review follow-up](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6070861169)

On this head, **205 focused tests passed and one Linux-only test was skipped on macOS**. The run includes the exact parity test, both wrong/missing-dataset CLI cases and the earlier search timeout. Ruff passed. The final macOS Python 3.12 full suite recorded **7,453 passed, 103 skipped, 136 failed**, plus 675 passing subtests. Comparing every failing test ID to the clean base on this host produced zero added and zero removed. The installed-wheel check verified 777 packaged resources. On `1a005543`, both Linux 3.10 and 3.11 full suites had exactly the same single failing test, the parity assertion fixed in this increment, with 7,601 passing on each. [Linux 3.11 log](https://github.com/InferMatrixLab/InferRSI/actions/runs/45784749966/job/139788636332). [Linux 3.10 log](https://github.com/InferMatrixLab/InferRSI/actions/runs/45784749966/job/139788636006)

The [bounds and receipt regressions](https://github.com/InferMatrixLab/InferRSI/blob/d8131f62dad69e63c81562f2ffa4c626b676bf9c/tests/apps/test_task_intake.py#L649-L700) already cover both an invalid new answer and a previously approved record containing invalid values. I reran both test functions and the exact changed ranking assertion on this head: **7 passed**. The installed wheel maps repetitions and rounds to `integer / task-input/v1 / count` and max_minutes to `number / task-input/v1 / minutes`. The cases include 0 repetitions, −1 rounds and −5 minutes. The legacy record test checks all three fields, blocks start, and requires fresh manual approval after correction. [Parity assertion](https://github.com/InferMatrixLab/InferRSI/blob/d8131f62dad69e63c81562f2ffa4c626b676bf9c/tests/apps/test_session_ranking_policy.py#L154-L175) · [Current declaration check](https://github.com/InferMatrixLab/InferRSI/actions/runs/45788630648) · [Current Ready CI](https://github.com/InferMatrixLab/InferRSI/actions/runs/45788580340)

<details><summary>Complete four-file increment since the previous review</summary>

````diff
diff --git a/docs/guides/optimization-workflow-unification.md b/docs/guides/optimization-workflow-unification.md
index 785f3d7e..18cde2bd 100644
--- a/docs/guides/optimization-workflow-unification.md
+++ b/docs/guides/optimization-workflow-unification.md
@@ -197,7 +197,7 @@ assessment 另附 `paired_statistics`：同一次重复内的第 k 个基线与
 结果协议：
 
 - 测量脚本正常结束并写 JSON，提供指定字段的有限正数。
-- 质量脚本在顶层 `dataset` 字段报告实际评分的数据集、版本及切分标识，与已批准的 `--quality-benchmark` 一致。缺少标识或标识不匹配时，质量证据为 `INCONCLUSIVE`。
+- 对于有评分的结果，质量脚本在顶层 `dataset` 字段自行报告数据集、版本和切分标识。Harness 将它与已批准的 `--quality-benchmark` 核对；缺少标识或标识不一致时，该评分结果为 `INCONCLUSIVE`。
 - 质量脚本正常结束并写 JSON，提供指定字段的严格布尔值。`false` 拒绝候选；基线拒绝说明协议/基线前提不成立。
 - 脚本可捕获已知候选错误，正常结束并写 `{"status":"candidate_failure","reason":"..."}`。候选失败保留为 FAIL 并消耗一轮，后续可修改。不要把设备故障捕获成候选错误。
 - 非零退出、超时、缺少或无法解析的输出不猜测为正确性失败，而是 INCONCLUSIVE，阻止继续把缺失证据当成有效比较。
diff --git a/docs/guides/task-intake.md b/docs/guides/task-intake.md
index 081ddb9d..e8258396 100644
--- a/docs/guides/task-intake.md
+++ b/docs/guides/task-intake.md
@@ -202,11 +202,15 @@ preapproval starts unattended. The frozen `plan.json` references a receipt in
 `plan/` with the SHA-256 and revision of the retained `intake.json`.
 
 For AB/BA the two approved measurement commands describe the same script with
-the candidate path supplied at execution. The quality command returns its
-identity of the dataset actually scored in the top-level `dataset` field. It must
-match both `--quality-benchmark` and the approved benchmark (including its version
-and split). Missing or mismatched identity makes the result `INCONCLUSIVE`.
-Also return the boolean acceptance key and a numeric result under the approved quality metric
+the candidate path supplied at execution. For a scored quality check, the
+frozen script self-reports the dataset it evaluated in the top-level `dataset`
+field. Harness compares that label with the approved `--quality-benchmark`,
+including its version and split. The script supplies the evidence for which
+corpus it loaded. A missing or mismatched label makes a scored result
+`INCONCLUSIVE`. An explicit `status: candidate_failure` is an unscored
+rejection. A candidate rejection is `FAIL`, and a baseline rejection leaves
+the comparison `INCONCLUSIVE`. A scored result also supplies the boolean
+acceptance key and a numeric result under the approved quality metric
 (JSON dotted paths are supported). A boolean metric on the acceptance key is
 compared as 1 or 0. The independent final checks the approved absolute bound or
 relative improvement against the pinned baseline. For service reuse, the first
diff --git a/plugins/inferrsi/skills/inferrsi/SKILL.md b/plugins/inferrsi/skills/inferrsi/SKILL.md
index ef146c19..e6118cc2 100644
--- a/plugins/inferrsi/skills/inferrsi/SKILL.md
+++ b/plugins/inferrsi/skills/inferrsi/SKILL.md
@@ -142,8 +142,9 @@ inputs through `--protocol`. Checks must use the retained `{candidate}`,
 `{baseline}`, `{protocol}` and output `{result}` paths as appropriate. Confirm
 they execute the submitted code, not an unrelated installed package or service.
 For AB/BA, pass the approved dataset version and split as `--quality-benchmark`.
-The quality script must report the identity of the corpus it actually scored in
-the top-level `dataset` field alongside the quality result.
+For a scored result, the quality script self-reports the corpus it evaluated in
+the top-level `dataset` field. Harness checks the reported label against the
+approved identity.
 This command uses the same Harness controller as the packaged task path below.
 
 Edit the returned working candidate. Submit each hypothesis and candidate with
diff --git a/tests/apps/test_session_ranking_policy.py b/tests/apps/test_session_ranking_policy.py
index 2b5b0b61..13c2ed32 100644
--- a/tests/apps/test_session_ranking_policy.py
+++ b/tests/apps/test_session_ranking_policy.py
@@ -167,7 +167,8 @@ def test_project_assessor_uses_the_same_measurements_quality_and_threshold(proje
         assert assessment["verdict"] == "PASS" and assessment["quality_passed"]
         directory = arm[-1] / read(arm[-1] / "state.json")["rounds"][0]["path"]
         samples = {p.parent.name: read(p) for p in (directory / "execution").glob("*/result.json")}
-        assert {"metric": 20} in samples.values() and {"correct": True} in samples.values()
+        assert {"metric": 20} in samples.values()
+        assert {"correct": True, "dataset": "fixture-exact-v1"} in samples.values()
         evidence.append((read(arm[-1] / "plan.json")["evaluation_settings"], samples,
                          assessment["verdict"], assessment["score"], assessment["quality_passed"]))
     assert evidence[0] == evidence[1]
````

</details>

## Earlier review and validation history

[Dong1017’s review](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6069795180) and [zengchuang-hw’s review](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6070016596) identified the missing default gate and the gap between approval and execution.

| Exercised path | Observed result |
| --- | --- |
| Start without an intake, with an incomplete intake, or with a planning-only approval | Exit 2 before campaign creation. |
| Prepare executable options, display the brief and record the separate approval, then start with matching options | The session starts unattended and retains the evaluated record. The SHA-256 in the frozen receipt matches the retained bytes. |
| Repeat preparation, then change the metric unit, measurement command, budget, warmups, quality key or AB/BA validator | Identical preparation preserves approval. Changed conditions block start and a revised launch needs a fresh approval. |
| Change the service quality threshold or a final-stage warmup after approval | Both changes block creation. Restoring the reviewed configuration starts successfully. |
| Synthetic candidate doubles the baseline metric but misses the final absolute or relative target | The search round can retain the candidate. The independent final records `FAIL`. A true boolean quality result also fails to override a missed numeric quality bound. |

[Service quality read-back](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6070351218) on `694ec791`. Absolute mode shows the fixed score inequality and metric direction. Baseline-comparison mode names the retained baseline for the current comparison epoch and shows the permitted decrease or increase. With a baseline accuracy of 90 and 0.1 points allowed degradation, the card states `accuracy >= baseline accuracy - 0.1 points`. The Harness accepts 89.95 and rejects 89.8. Four executable-card tests compare both modes and directions with the real scorer. A fifth test confirms that approval of the former wording reopens the final card. **70 tests passed** across intake and these service hand-off cases.

[Complete service quality read-back](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6070409619) on `0fb75023`. The card headline, structured conditions and text summary now use the candidate score direction. In relative mode the numeric allowance is labeled `protocol.quality_baseline_tolerance` and the comparison epoch’s retained score is identified as the reference. The four mode/direction tests exercise the full rendering and scorer; an older maximize approval storing `at_most` reopens the comparator question before start. **118 focused tests passed** (including module migrations). Ruff passed.

On `1a005543`, the AB/BA invocation must name the approved dataset, including its version and split, using `--quality-benchmark`. The frozen quality script reports the dataset actually scored in its result. A mismatched launch cannot create a campaign. A mismatched or missing result identity gives `INCONCLUSIVE` and retains the incumbent even with accuracy 100, an approved minimum of 95, and boolean success. Regression tests cover both invalid receipts. On the final code, 203 focused tests passed and one Linux-only test was skipped on macOS. Ruff and the three skill projection checks passed. The macOS full suite on `1a005543` finished: 7,452 passed, 103 skipped, 137 failed and 675 subtests passed. Comparing IDs against the clean base left one additional failure, `test_project_assessor_uses_the_same_measurements_quality_and_threshold`. The fixture expected exactly a boolean-only receipt; the actual passing receipt also carried the required dataset. [Reviewer reproduction](https://github.com/InferMatrixLab/InferRSI/pull/706#discussion_r4705647252)

Service planning cards now label unbound quality inputs provisional; the prepared card displays the executable inequality and asks separately for approval. The previous head's macOS and Ready outcomes are tracked separately. On `0fb75023`, Linux 3.11 full-check reported one timed-out search test (`test_skill_carry_reuses_winning_child_verification`). Its call path and fixture are unchanged from base, and the exact test passed in isolation locally. [Previous CI result](https://github.com/InferMatrixLab/InferRSI/actions/runs/45780653834/job/139775128096)

On `1a005543`, zengchuang-hw formally approved after independently checking all four service-quality cases and matched, missing and mismatched AB/BA corpus labels. The trusted knowledge-model declaration status also passed. [Review](https://github.com/InferMatrixLab/InferRSI/pull/706#pullrequestreview-6070844677) · [Declaration CI](https://github.com/InferMatrixLab/InferRSI/actions/runs/45784802989) · [Ready CI](https://github.com/InferMatrixLab/InferRSI/actions/runs/45784749966)

The earlier Desktop transcript below verified the planning brief and the separate human decision. The new executable-binding checks used the real CLI with synthetic project and service fixtures.

- Local focused run on `c8095959`: **232 passed, 1 skipped and 54 subtests passed**. The intake and service launch regressions also ran separately on that head: **65 passed**. Ruff, the skill index at its declared source revision, the search-space index, skill coverage, and the isolated installed-wheel smoke check (777 resources) passed. On `0fb75023`, macOS Python 3.12 ran the full suite: **7,449 passed, 103 skipped, 136 failed**, plus 675 passing subtests. The set of all 136 failing test IDs exactly matches the set independently reproduced on the clean PR base on this host (zero added and zero missing). The index, coverage checks, Ruff and the isolated wheel resource check also passed on this head.
- The base policy admits the two declared authors (`claude-fable-5-2`, `gpt-6.2-astra`, both `xhigh`). [PR #518](https://github.com/InferMatrixLab/InferRSI/pull/518) declares `deepseek-flash`, unknown effort and an explicit exception. The current PR declares no exception. The [trusted declaration check on `694ec791`](https://github.com/InferMatrixLab/InferRSI/actions/runs/45779743459) passed, as did the preceding head. [Executable model and effort rules](https://github.com/InferMatrixLab/InferRSI/blob/51e475ad077ec88d60f9e8c561dc0415ca9855aa/.github/knowledge-model-policy.json#L23-L49) · [Exception procedure](https://github.com/InferMatrixLab/InferRSI/blob/51e475ad077ec88d60f9e8c561dc0415ca9855aa/docs/knowledge-model-policy.md#explicit-exceptions-and-policy-review)
- The router skill adds two lines telling the agent to ask when two deliverables fit. The CLI changes register intake and the campaign hand-off. Existing primary-task selection remains in place and no `skills route` command was introduced.

## Review files on the current head

The [complete diff in 36 ordered parts](https://github.com/jiangkuaixue123/InferRSI/blob/441444992849deb193ee86f646e50ab7c0834c24/README.md) contains 227,854 bytes and 4,542 lines across 40 changed files. Applying it to the base index reproduced the current head tree. SHA-256 `8182418d03eca21916461df6de69acdcbde2909d81f19992f94bd03186831697`.

<details><summary>All 40 changed files at the current commit</summary>

- [`AGENTS.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/AGENTS.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-a54ff182c7e8acf56acfd6e4b9c3ff41e2c41a31c9b211b2deb9df75d9a478f9)
- [`docs/apps-module-migrations.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/apps-module-migrations.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-b28a4e82710c4f515615cf82e51ab8d571995a8a4951bde99db72f686389dbc7)
- [`docs/guides/operations.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/guides/operations.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-7314b4ac2527779e00c3804c371eaa49c60bb63a97bebee43d6e5116e681c10c)
- [`docs/guides/optimization-workflow-unification.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/guides/optimization-workflow-unification.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-84e66959af1f9a86e87b064296957729f3228af2a6c61562478bcf34142ed2ff)
- [`docs/guides/service-reuse-campaigns.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/guides/service-reuse-campaigns.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-38d5741849b51ed036e101a31a9bebff0db74281e485e6d37a22a981ba898d3a)
- [`docs/guides/task-input.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/guides/task-input.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-d35a29f1aa85b0e2a36e3905d8f5de2552ade83719466bf497f49ab42a36404a)
- [`docs/guides/task-intake.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/guides/task-intake.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-902240e9c5da59b3d5db068aae264f60dfd8c7828c05eb49d347dd0e2796f019)
- [`docs/searchspace-index.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/searchspace-index.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-3cf08dcaa641135aaf04553e02bac95565082ff74e2ac7b45a9ab937a0c278d9)
- [`docs/skill-coverage.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/docs/skill-coverage.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-203d1f435dc559bf98a35c5b3d8ce00fefd43ff071a88d04f7a4892f37fedbc0)
- [`plugins/inferrsi/skills/inferrsi/SKILL.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/plugins/inferrsi/skills/inferrsi/SKILL.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-3bc1b60dc7a1a9266965e8b65161bea0abb6510a2e2f242929ab2c75926eb26e)
- [`src/inferrsi/apps/cli/__init__.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/__init__.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-4acacea2fbd52a0c71bb56012b0c71e39dbf42c7a83ab8badb7d330bb816afd2)
- [`src/inferrsi/apps/cli/arguments.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/arguments.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-d432caa3d2889568cc2821a49981a23c78a10aeee7cab0e3cd1c76da55b0af1e)
- [`src/inferrsi/apps/cli/campaign_intake.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/campaign_intake.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-bee385be2c764dbf6c3e985e3a307742fa58e2a733bc27e761224859f0a3df25)
- [`src/inferrsi/apps/cli/intake_contract.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/intake_contract.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-acc90423348d1c29a3d79f3b831cc5c67c0c8a9884052d833ee814c2be882d4e)
- [`src/inferrsi/apps/cli/task_input.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/task_input.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-981bd4ea5bdcc9595cb162a665379d6965e2a09900d851750a24ddae5588f2e8)
- [`src/inferrsi/apps/cli/task_intake.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/apps/cli/task_intake.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-c330bbf041fe5cbe9cc6e9465f1398f82fb98fd7149eab3de509c7702afe74a3)
- [`src/inferrsi/harness/optimization_session.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/harness/optimization_session.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-99d8ceda6924793b8398e194ab5552f6044a7e64eff07ba8eefedeafe67b1fde)
- [`src/inferrsi/harness/project.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/harness/project.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-c8d53615ff0bab819b2b2b0450d4b4d5c052a068948199d34b5fd045ec0bfa0a)
- [`src/inferrsi/harness/project_service.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/harness/project_service.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-7550706306a3d226ccba8dbd8aa067381d25fc1161ba819f0f1afe45c6057ef8)
- [`src/inferrsi/knowledge/data/skill_library/_compiled/_provenance.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/_compiled/_provenance.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-cbc65dd412c88d7e99b35a987989f42fe7e3df46bfa579135915c041f4d59829)
- [`src/inferrsi/knowledge/data/skill_library/_compiled/inputs.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/_compiled/inputs.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-da58e9898fafec9cc37534b281e55bae9c25137d861c92f478538e379f8e3507)
- [`src/inferrsi/knowledge/data/skill_library/tasks/inference-task-router/SKILL.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/tasks/inference-task-router/SKILL.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-4758de3b17e10bbc640514f92591b5bd598d7759b03a303911721d59ae766eeb)
- [`src/inferrsi/knowledge/data/skill_library/tasks/task-day-0/intake.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/tasks/task-day-0/intake.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-a73e1886c0cf6861c5c5af8468da85df4ff0583a0a2aff246beb3b041b7bcd5e)
- [`src/inferrsi/knowledge/data/skill_library/tasks/task-performance/SKILL.md`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/tasks/task-performance/SKILL.md) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-34a9407d18f4b526cac791574aeb89f765bf59646768e2053956267a678e9f5e)
- [`src/inferrsi/knowledge/data/skill_library/tasks/task-performance/intake.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/src/inferrsi/knowledge/data/skill_library/tasks/task-performance/intake.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-a3de1637706fa662d5696cab15c0a0b7902f36d26e39b2fe817e7a0a2b8c16a8)
- [`tests/apps/test_engineering_benchmark_plugins.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_engineering_benchmark_plugins.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-75cdaf757a9bb8a3c8716b1fb9a935fce5f2fc771abd177219be27776a30eea1)
- [`tests/apps/test_project_explanation.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_project_explanation.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-9c334aef266f80e662524993d012c23ea738c4bb3fcc0682b9d655303bae025e)
- [`tests/apps/test_project_optimization.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_project_optimization.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-869dd44823288947b8caf224514afaa2200384436cf918d2c2bf58e53950db63)
- [`tests/apps/test_project_service_reuse.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_project_service_reuse.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-de68325f34addbd1e424068078b290609690925c38f8e123ea42629546e193d0)
- [`tests/apps/test_session_ranking_policy.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_session_ranking_policy.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-669eba0c46c56992ae8bdeb340bfa36f6a83ebe91ceefd24b3c9735fbbc394ca)
- [`tests/apps/test_task_intake.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/apps/test_task_intake.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-27bae40bcca6a17219c31dfcc93229f8fd060cc72dfb770fad04fb657905b63d)
- [`tests/fixtures/campaign_intake.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/campaign_intake.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-ab9e48d5634d73335d36cc216987e00a4af25af00af52155fe3bbe6ae49c9009)
- [`tests/fixtures/intake/performance/complete.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/intake/performance/complete.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-367121399baec418a127479639c451bcfc5c7eba64f6dff537a310a45d5d3248)
- [`tests/fixtures/intake/performance/frozen-gate.yaml`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/intake/performance/frozen-gate.yaml) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-e10e2cedafecfcc7a0510ee3f5f3c6da14891f782bea1ae01802d121a666c50d)
- [`tests/fixtures/intake/performance/frozen-mismatch.yaml`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/intake/performance/frozen-mismatch.yaml) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-386bd3b5ace9d03d764ac53a04b19334608969ecf782e84c66174f848c7e34c0)
- [`tests/fixtures/intake/performance/partial.json`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/intake/performance/partial.json) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-553a615e229a8c0406606b7fb1ca1f126c9c0a1fc888c7459ffea06f8eba4497)
- [`tests/fixtures/service_reuse.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/service_reuse.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-d8c50537ff0442dcaa57e3fde6a8ba68b36f496c694d4251da3a489267cceab7)
- [`tests/fixtures/service_reuse_protocol.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/fixtures/service_reuse_protocol.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-bee4136e5794bae2b8304182859b0c61d3468a8648307b04a2910c686f18a90a)
- [`tests/harness/test_service_reference_evidence.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/harness/test_service_reference_evidence.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-d2e39be183e229a1ca29750287e4faf9701db402cbda6a6b76ed608a158067de)
- [`tests/repository/check_installed.py`](https://github.com/InferMatrixLab/InferRSI/blob/a8b619985bbb86fe16906c071e3ced83eec85b93/tests/repository/check_installed.py) · [diff](https://github.com/InferMatrixLab/InferRSI/pull/706/files#diff-7ded4cba36297e1af8501b8fb9f13369021e6a1d853e0788d758473c7b127c67)

</details>

## Earlier checks on `cebe9271`

- On `cebe9271`, 304 focused tests passed with 43 passing subtests. These include intake, the shared YAML task contract, module migrations, coverage and the architecture checks. All 54 intake tests passed.
- macOS, Python 3.12, full suite with the virtual environment active: 7,432 passed, 103 skipped, 136 failed. The 136 failing test IDs exactly match those reproduced on the clean PR base `51e475ad` on the same host. There were no additional failing IDs on this head.
- Ruff passed. The skill index at its declared source revision, the search-space index and skill coverage all matched. The installed-wheel smoke check passed for 777 resources.
- Re-reading the retained desktop trial with this head produced revision 11, `brief_review: approved`, `status: ready` and `execution: not started`. The transcript below is from the original desktop trial.

## Codex Desktop verification of the performance intake

The test started a new chat in the ASR project with the original prompt: **“使用 ~/code/InferRSI 帮我优化一下性能”**. The native cards asked six questions in four rounds. The user authorized Codex to answer as a tester; the replies were sent through the test chat. No benchmark was run or ASR project file changed. RTF is transcription wall time divided by audio duration. P6 supplies the fixed English and Chinese clips, and P7 names the existing acceptance plan. The numbers below are acceptance targets for this replay.

| Round | What the card asked | Reply sent in the test chat |
| --- | --- | --- |
| 1 | 本轮优先优化什么指标、用哪个数值判定达标？ | 选“目标为实时”。以当时的 main 为基线，在 P6 中英文单条请求、并发 1 下，合并 RTF ≤ 1.0 秒/音频秒。 |
| 1 | 本轮用哪套质量验收？ | 沿用 P7。P6 和完整 Natural30 的原生稳定输出差异数 = 0，全部正常 EOS，相关 Metal 测试全部通过。质量失败就保留基线。沿用 P7 计时边界，每组预热 1 次，做 6 组交替对照。 |
| 2 | 是否选用这份验收记录？ | 选用。保留候选要求配对加速区间下界 > 1.0×。最终复测仍须达到合并 RTF ≤ 1.0。 |
| 2 | 任务书中的优化范围和预算是否沿用 P7？ | 沿用。范围限模型执行和 Metal 内核，最多试 1 个候选，预算 60 分钟，含最终复测。 |
| 3 | 完整复述后：是否批准刚展示的第 9 版任务书？ | 要求修改。把最终合并 RTF 上限从 1.0 收紧到 0.95 秒/音频秒，其余条件照旧。 |
| 4 | 复述修订版后：是否批准合并 RTF 上限为 0.95 的第 11 版任务书？ | 批准第 11 版。确认 RTF ≤ 0.95 和稳定输出差异数 = 0，记录审批后结束本次流程验证。 |

Before each approval reply, the campaign gate returned `blocked`, the brief was `awaiting_confirmation`, and only read-only preparation was allowed. An attempted answer using the obsolete revision 9 question ID was rejected without changing the record. Only the explicit revision 11 approval produced `ready` and `approved`. Execution remained `not started`.

## Remaining work and Issue closure

- Day-0 still needs equivalent end-to-end acceptance examples. Comparing normalized records from paired native-card and text-fallback runs remains outstanding.
- The issue remains open for the owner handoff, independent verification and acceptance.

