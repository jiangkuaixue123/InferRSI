# DSV4.1 优化任务书

## 用户接受与合并指令（2026-11-09）

用户明确指示：“这个判定为通过吧 然后合并push代码”。
据此将本轮 DP4TP4 记为用户接受通过，停止追加性能排查，合并到
codex/dsv41-retained，已完成合并和远程推送。保留原始失败与现场对照记录，不表述为零回退。

- 两种布局均使用 capture [24,48]。
- DP2TP8 两轮均值：C1 37.057937、C4 28.698287 ms/token；GSM8K 294/300、零失败。
- DP4TP4 两轮均值：C1 29.401772、C4 24.017719、C16 35.548399 ms/token。
- DP4TP4 C1 比历史高1.71%，现场旧版本 C1 为28.855630；用户明确接受该差异。
- DP4TP4 本候选未重跑 GSM8K；按用户最新合并指令收尾。
- 同一候选服务的R1/R2之间不重启、不重复预热。


## 当前任务更新（2026-11-09）

用户当前目标为保留分支的优化与部署配置适配DP2TP8，实测C1/C4，同时DP4TP4性能不劣化。**两种布局均使用capture [24,48]，这是用户明确要求；TP8须覆盖本地3/6行和半个六-token组，不能以关闭优化代替适配。** 既有军规继续有效。新轮次计划与证据位于 /Users/jiangchenzhou/code/dsv41-0day-20261102/dp2tp8_001/，工作分支 codex/dsv41-dp2tp8-001，尚未验证或保留；详见[#353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6730962302)。历史25ms任务记录保留，本次验收以用户新目标为准。

修订：2026-11-07（Asia/Shanghai）。治理：[InferRSI #353](https://github.com/InferMatrixLab/InferRSI/issues/353)；历史：[#329](https://github.com/InferMatrixLab/InferRSI/issues/329)。本次落实用户最新军规，执行重心为优化和实际测试。

## 0. 用户军规：优化，然后测试（最高执行优先级）

**用户原话：“注意我不想看到什么SHA256 hash相关的，别给我搞这套，这条是军规，写进计划书里面！”**

- **禁止新增、计算、核对或汇报 SHA256、hash、哈希及同类文件指纹；禁止将其作为启动服务、性能测试、精度测试或交付的门槛。既有工具中的此类步骤也须跳过或移除，不能只从汇报中隐藏而继续执行。**
- 本条覆盖本文其他条款、历史计划、归档规范和旧执行器中相冲突的要求。历史记录保留原样，不重算、不补齐、不以其阻塞后续工作。
- **核心顺序：实施优化 → 必要的功能/数值检查 → 立即进行服务性能测试 → 按性能结果进行精度测试。** 沿用已有可用工具，不继续扩建验证框架、层层封存或反复证明已通过的检查。
- 保留影响结果可信度的实际检查：服务和进程归属、启动配置、请求数量及输出、计时口径、功能正确性和精度评分。不得以简化流程为由伪造通过或漏报失败。
- 用现有提交记录、服务/run ID、配置及原始日志定位版本和结果。进度汇报只说优化内容、当前阶段、实测 TPOT、精度结果或具体阻塞原因；归档不得挡住下一轮优化和测试。
- **后续同一候选的两轮测量连续复用同一个服务，中间不重启、不重复预热。首次启动仅做必要预热；代码或配置改变、服务失效时才重启。精度继续复用该服务。** 此条同样覆盖旧执行器和最终验收中的独立启动要求。

## 1. 目标与当前依据

在 jcz-dsv41（单机 Ascend 910C，8 卡 / 16 die）上优化 DeepSeek V4.1 Flash W8A8：**全服务并发 C1/C4/C16 各自 TPOT ≤25 ms/token，固定 GSM8K 300 题答对 ≥292，功能正确。** 后续不测 C32 性能；GSM8K 仍用 C32。

- 初始 8K/1K 基线 `9be3c22a` 和三组 A/A 已完成，直接沿用，不重测初始基线、A/A 或父版本。
- 前一保留候选：`codex/rms-rsqrt-fused-002`，两轮 C1/C4/C16 均值 **33.6985 / 37.0498 / 47.4836 ms/token**，相对 index-tie-fp32 收益 **1.922829% / 1.790656% / -0.823874%**，预设 C1/C4 性能 PASS。GSM8K **293/300**、300 请求成功、零失败；114 项相关检查及完整格式检查通过。提交已带 sign-off 推送，统一保留分支 `codex/dsv41-retained` 已快进并推送。同一服务完成两轮及精度，中间未重启或重复预热，已停止回收。组件 **95.12 秒**、性能 **510.05 秒**、精度 **564.38 秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/rms_rsqrt_fused_002/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6677300947)。最终三档 25 ms 目标尚未达成。
- 前一保留候选：`codex/dspark-attn-batch-001`，两轮 C1/C4/C16 均值 **33.5589 / 36.9527 / 45.3463 ms/token**，相对 rms-rsqrt-fused-002 收益 **0.414288% / 0.262090% / 4.501167%**，预设 C16 性能 PASS。GSM8K **294/300**、300 请求成功、零失败；83 项相关检查及完整格式通过，三个草稿阶段在 16 个 worker 上均实际合批执行。提交已带 sign-off 推送，统一保留分支 `codex/dsv41-retained` 已快进并推送。同一服务连续完成两轮及精度，中间未重启或重复预热，已停止回收。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_attn_batch_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6677729256)。最终三档 25 ms 目标尚未达成。
- 前一保留候选：`codex/target-slot-rows-001`，两轮 C1/C4/C16 均值 **33.2732 / 35.6156 / 45.5526 ms/token**，相对注意力合批收益 **0.851590% / 3.618283% / -0.455070%**，预设 C1/C4 性能 PASS。GSM8K **295/300**、300 请求成功、零失败；49 项最终相关检查及完整格式通过，16 个 worker 实际执行。提交已带 sign-off 推送，统一保留分支 `codex/dsv41-retained` 已快进并推送。同一服务连续完成两轮及精度，中间未重启或重复预热，已经停止回收。累计组件 266.30 秒、性能 464.82 秒、精度 469.68 秒；后续以此为直接父版本。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_slot_rows_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6679508308)。最终三档 25 ms 目标尚未达成。
- 当前候选 `codex/target-index-overlap-001`：直接父版本query-overlap-002，预设C1/C16、保护C4≤25ms。原索引WQB/旋转/FP4与权重投影转到已有查询侧流，在评分读取缓存前汇合；算术、缓存和选择算法不变。122项回归通过、2项跳过；真实checkpoint/TP4的比例1/2、20→24候选链、6/12行图回放及完整缓存逐位通过，20次完整调用44.703→40.613、57.927→54.532、92.876→88.348、129.327→122.421ms。夹具的六位置分组与原生元数据初始化顺序已修正，生产代码与数值门槛未改；组件累计191.24秒（含失败）。完整格式通过，已带sign-off提交推送，正在启动同服务正式两轮测试，暂无正式成绩。[本轮 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6708499086)。
- 缓存写入准备候选 `codex/target-cache-prepare-001` 未保留：两轮C1/C4/C16中值 **28.354174 / 23.674575 / 34.995156 ms/token**，收益 **1.911805% / 1.384854% / 0.558872%**；预设C16两轮收益一负一正（-1.182599% / +2.300343%），性能INCONCLUSIVE、GSM8K NOT_RUN，不事后改目标或重测。109项回归通过、2项跳过，全部BF16位模式/完整缓存逐位/动态图及真实TP4消费者通过；首次夹具缺少原生scatter初始化已修复，生产代码与标准未变。完整格式通过，已带sign-off提交推送；组件89.97秒（含失败）、性能391.78秒。16worker实际执行，同服务连续两轮、无中间重启或重复预热，服务已回收、源码恢复query-overlap-002，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_cache_prepare_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6708155312)。
- 行屏蔽候选 `codex/target-row-mask-001` 未保留：两轮C1/C4/C16中值 **28.333438 / 23.696841 / 34.812772 ms/token**，收益 **1.983537% / 1.292107% / 1.077129%**；预设C16两轮收益一正一负（+2.218127% / -0.063870%），性能INCONCLUSIVE，GSM8K NOT_RUN，未事后更改目标或重测。146项回归通过、2项跳过，全部BF16位模式/图回放、真实TP4与EP16完整消费者通过；首次126个NaN位模式差异已按原生SelectV2规则修复，逐位标准未放宽。完整格式通过，已带sign-off提交推送。组件125.71秒（含失败）、诊断8.82秒、性能382.76秒；16worker实际执行，同服务连续两轮、无中间重启或重复预热，服务已回收、源码恢复query-overlap-002，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_row_mask_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6707788121)。
- 当前保留候选：`codex/target-query-overlap-002`，直接父版本native-sink-001，预设C1/C16，保护C4≤25ms。将Q旋转放到侧流，等待后移至KV缓存写入/压缩准备之后；算子形状、算术与缓存次序不变。两轮C1/C4/C16中值 **28.906816 / 24.007038 / 35.191833 ms/token**，改善 **3.723535% / 3.908394% / 3.712716%**，正式性能PASS；**GSM8K 294/300 PASS**，300请求成功、0失败、1条达到4096上限。100项回归通过、2项跳过，真实TP4/实际checkpoint、Q/KV/缓存逐位及完整图消费者一次通过，完整格式通过，已带sign-off提交推送，统一保留分支已快进推送。16个worker全部40目标层、6/12行实际执行；同一服务连续完成两轮与精度，无中间重启或重复预热，已停止回收。组件61.56秒、性能402.50秒、精度463.77秒；C1/C16仍未达到25ms，继续优化。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_query_overlap_002/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6707325304)。
- Q投影并行候选 `codex/target-query-overlap-001` 未保留：两轮C1/C4/C16中值 **29.804132 / 24.464410 / 36.472468 ms/token**，收益 **0.734951% / 2.077694% / 0.208809%**。C16收益一正一负，INCONCLUSIVE；C1改善未过门槛，未事后改目标，GSM8K NOT_RUN。100项回归通过、2项跳过，真实TP4/实际checkpoint/图回放/缓存逐位及完整原生消费者、格式检查通过，已带sign-off提交推送。组件120.80秒（含3次夹具设置修正）、性能409.84秒；16个worker、全部40目标层、6/12行实际执行。服务同一实例连续两轮后已回收，无中间重启或重复预热；源码恢复native-sink-001，保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_query_overlap_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6706955695)。
- 共享专家并行候选 `codex/target-shared-overlap-001` 未保留：两轮C1/C4/C16中值 **29.225653 / 24.363030 / 37.851971 ms/token**，收益 **2.661621% / 2.483485% / -3.565604%**，C16回退超限，性能FAIL、GSM8K NOT_RUN。41项回归、完整16卡原生图回放及格式检查通过，已带sign-off提交推送。组件69.04秒（含旧夹具修正）、性能407.86秒；16个worker实际执行，同一服务连续两轮，没有中间重启或重复预热。服务已回收，源码恢复native-sink-001，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_shared_overlap_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6706699952)。
- BF16 KV先投影候选 `codex/target-kv-before-gather-002` 组件数值淘汰：真实checkpoint第0层12行、幅度0.01输入有5/24576个BF16输出不同；逐位门槛未放宽。首次独立配置初始化失败已修正为服务实际ND策略；两次组件共26.77秒。完整TP4消费者、计时、服务性能/GSM8K均NOT_RUN。完整格式通过，实验已带sign-off提交推送；设备源码恢复native-sink-001，统一保留分支不变。[轮次记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_kv_before_gather_002/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6706474882)。
- KV先投影候选 `codex/target-kv-before-gather-001` 未保留：实际43个WKV为BF16，而实现限定dynamic W8A8，6/12行图捕获后候选worker为0，正式运行已中止，INCONCLUSIVE、GSM8K NOT_RUN。24项合成W8A8及相关检查通过不代表实际WKV路径；不宣称服务收益。组件58.55秒，服务生命周期401秒，部分R1原件保留；PID286697已停止回收，源码恢复native-sink-001。完整格式通过，实验已带sign-off提交推送，统一保留分支不变。后续须按实际BF16算子单独验证。[轮次记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_kv_before_gather_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6706128406)。
- 头通信布局候选 `codex/target-head-gather-001` 未保留：两轮 C1/C4/C16 中值 **29.977329 / 24.891407 / 39.127861 ms/token**，收益 **0.158105% / 0.368579% / -7.056528%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。真实 TP4 完整输出逐位一致及 CPU/NPU 回归通过（3个pytest用例），完整格式通过，已带sign-off提交推送。组件39.87秒、性能411.74秒；16个worker实际执行，同一服务连续两轮，无中间重启或重复预热。服务已回收，源码恢复 native-sink-001，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_head_gather_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6705934051)。
- 前一保留候选：`codex/target-native-sink-001`，两轮 C1/C4/C16 中值 **30.024799 / 24.983491 / 36.548786 ms/token**，相对父版本改善 **1.987582% / 4.012838% / 3.502348%**，预设 C4 性能 PASS。**C4 已达到两轮中值25 ms目标，C1/C16仍未达到。** GSM8K **296/300 PASS**，300请求成功、0失败、2条达到4096上限。65项设备/集成/加载检查及完整格式通过，已带sign-off提交推送；统一保留分支已快进并推送。PID192818同服务连续完成两轮及精度，无中间重启或重复预热，服务已停止回收。组件 **16.29秒**、性能 **391.86秒**、精度 **481.71秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_native_sink_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6705612704)。后续继续保护已达标的C4，整个任务尚未完成。
- 前一保留候选：`codex/target-gather-fia2-001`，两轮 C1/C4/C16 中值 **30.633668 / 26.027950 / 37.875311 ms/token**，相对父版本改善 **2.953558% / 11.664118% / 2.568051%**，预设 C16 性能 PASS。GSM8K **293/300 PASS**，300 请求成功、0 失败、1 条达到 4096 输出上限。21 项检查及完整格式通过，已带 sign-off 提交推送；统一保留分支 `codex/dsv41-retained` 已快进并推送。同一 PID 152948 完成两轮及精度，中间未重启或重复预热，服务已停止回收。组件累计 **40.05 秒**（含初始化和接口失败，未放宽数值标准）、性能 **415.83 秒**、精度 **478.12 秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_gather_fia2_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6705284846)。三档 25 ms 最终目标尚未达成。
- 目标输出投影前移 `codex/target-woa-before-exchange-001` 组件数值淘汰：真实 TP4 完整输出逐位比较失败，一个 5120 维 BF16 输出有 478 个元素不同；未放宽比较标准，图回放和完整计时未运行到，正式性能/GSM8K 均 NOT_RUN。累计组件 118.83 秒，含三次测试设置失败及最终数值失败。完整格式通过，实验已带 sign-off 提交推送，在线源码恢复 output-graph-001，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_woa_before_exchange_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6705083289)。同轮完成当前保留版 C16 短段 profile，16 条请求完成、服务回收；DP0/TP0 目标压缩注意力约 276.843 微秒、MoE 354.223 微秒，实际 all-to-all HCCL 约 26.432 微秒，不能与 202.064 微秒的 AICPU 伴随核混同。[诊断记录](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6704974751)。
- 共享专家激活查表组合 `codex/shared-swiglu-table-001` 组件淘汰：76 项检查及完整格式通过，BF16 有限输出逐位一致、非有限位置一致，真实 W8A8 完整专家和图回放正确；四组完整调用均变慢（2/5 行 eager：0.8758→0.9278、0.8748→0.9145 ms；6/12 行图 40 次：3.4118→3.7595、4.3749→4.4069 ms）。累计组件 57.01 秒，包含 limit=0 关闭截断语义修正，未放宽比较标准。未启动服务，正式性能和 GSM8K 均 NOT_RUN；实验带 sign-off 提交推送，已恢复 output-graph-001 源码，统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/shared_swiglu_table_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6704886756)。
- 共享专家上投影合并 `codex/shared-up-merged-001` 未保留：两轮 C1/C4/C16 均值 **31.2730 / 29.4915 / 38.9743 ms/token**，收益 **+0.928204% / -0.090784% / -0.259068%**。预设 C4/C16 两轮收益方向相反，性能 INCONCLUSIVE、GSM8K NOT_RUN；C1 均值收益也未超过门槛。65 项集成/加载、16 项真实 NPU 检查及完整格式通过，投影及完整专家输出逐位一致，已带 sign-off 提交推送；全部 16 个 worker 的 40 个目标层和 3 个草稿层均实际执行。组件 51.63 秒（含空输入和配置接口测试修正，未放宽比较标准）、性能 416.62 秒。一个服务连续两轮，无中间重启或重复预热，已回收并恢复 output-graph-001 源码；统一保留分支不变，不追加重测。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/shared_up_merged_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6704599462)。
- 草稿专家选择图 `codex/dspark-router-graph-001` 未保留：两轮 C1/C4/C16 均值 **31.8535 / 29.7846 / 39.7712 ms/token**，收益 **-0.910750% / -1.085353% / -2.308882%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。75 项设备/集成、8 项真实 EP16 场景及完整格式通过，已带 sign-off 提交推送；16 个 worker、三个阶段实际执行 2/5 行。组件 140.24 秒（含失败与修正），性能 438.95 秒；上游 FP32 门控重复差异按相同 logits 比较路由，未放宽容差。一个服务连续完成两轮，无中间重启或重复预热，已回收并恢复 output-graph-001 源码。统一保留分支不变。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_router_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6704314233)。
- 草稿空闲 DP 路由屏蔽 `codex/dspark-idle-mask-001` 未保留：两轮 C1/C4/C16 均值 **31.8181 / 29.5631 / 38.9238 ms/token**，收益 **-0.798613% / -0.333716% / -0.129015%**。预设 C1 两轮均未改善，性能 FAIL、GSM8K NOT_RUN；回退未超容限不等于晋级。62 项集成、8 项 EP16 场景及完整格式通过，已带 sign-off 提交推送，16 个 worker 实际执行 5/20/40 行。累计组件 259.37 秒（含失败/修正），性能 417.21 秒；原生父版与独立公式在二十行的两个元素差异保留披露，相对父版比较未放宽容差。同服务完成两轮，无中间重启或重复预热，已回收。统一分支继续保留 output-graph-001。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_idle_mask_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6704040321)。
- 草稿本地整段图 `codex/dspark-stage-local-graph-001` 未保留：两轮 C1/C4/C16 均值 **31.6940 / 29.6836 / 40.8173 ms/token**，收益 **-0.405437% / -0.742730% / -5.000120%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。18 项主机、34 项设备/集成及完整格式通过，已带 sign-off 提交推送；16 个 worker、三个阶段实际执行 5/20 行。组件 21.92 秒、性能 437.65 秒；同一个服务连续完成两轮，中间未重启或重复预热，已停止回收。本轮不进入下一候选，统一分支继续保留 output-graph-001。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_stage_local_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6703893249)。
- 草稿 HC 残差融合 `codex/dspark-hc-post-001` 组件淘汰：37 项主机、40 项设备/集成及完整格式通过，但 6 次完整 eager 调用的就绪耗时，5 行 **0.4054→0.7597 ms**、20 行 **0.4122→0.7497 ms**，全部变慢。组件 17.82 秒，正式性能及 GSM8K 均 NOT_RUN；未启动整机服务，实验已带 sign-off 提交推送，在线源码已在设备租约内恢复为保留的 output-graph-001。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_hc_post_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6703764856)。
- 前一保留候选：`codex/dspark-output-graph-001`，两轮 C1/C4/C16 均值 **31.5660 / 29.4648 / 38.8736 ms/token**，相对 context-graph-001 收益 **-0.397575% / +0.802438% / +2.684420%**，预设三档性能 PASS；C1 回退在既定容限内，C16 两轮均改善并超过门槛。GSM8K **294/300**、300 成功、零失败，1 条达到 4096 上限按原规则计分。68 项主机、119 项设备/集成与完整格式通过；16 个 worker、三个阶段均执行 5/20 行。已带 sign-off 提交推送，统一保留分支已快进并推送；同一服务连续两轮和精度，中间未重启或重复预热，服务已回收。组件 27.36 秒、性能 416.76 秒、精度 443.97 秒。最终三档 25 ms 尚未达成。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_output_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6703539796)。
- 前一保留候选：`codex/dspark-context-graph-001`，两轮 C1/C4/C16 均值 **31.4410 / 29.7031 / 39.9459 ms/token**，相对 device-history-001 收益 **3.769425% / 12.862106% / 3.164161%**，预设三档性能 PASS。GSM8K **294/300**、300 成功、零失败，1 条达到 4096 上限按原规则计分；25 项主机、103 项设备/集成及完整格式通过，16 个 worker、三个阶段均实际执行 6/24 行路径。已带 sign-off 提交推送，统一保留分支已快进并推送。同一服务连续完成两轮与精度，R2 无重启、重复预热或探针，服务已回收。组件 49.19 秒、性能 429.21 秒、精度 434.85 秒。最终三档 25 ms 尚未达成。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_context_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6703359250)。
- 前一保留候选：`codex/dspark-device-history-001`，两轮 C1/C4/C16 均值 **32.6726 / 34.0875 / 41.2512 ms/token**，相对 graph-003 收益 **1.947252% / 2.056982% / 2.764274%**，预设三档性能 PASS。GSM8K **295/300**、300 成功、零失败，2 条达到 4096 上限按原规则计分；36 项主机、88 项设备/集成及完整格式通过，16 个 worker、三个阶段和五/二十行路径均实际执行。已带 sign-off 提交推送，统一分支已快进并推送。一个服务连续完成两轮与精度，中间未重启或重复预热，现已回收。组件 24.25 秒、性能 435.12 秒、精度 468.90 秒。最终三档 25 ms 尚未达成。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_device_history_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6703113789)。
- 草稿上下文写入 `codex/dspark-context-write-001` 未保留：两轮 C1/C4/C16 均值 **33.3612 / 34.9174 / 45.7578 ms/token**，收益 **-0.119492% / -0.327675% / -7.858666%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。18 项主机、91 项设备/集成及完整格式通过，已带 sign-off 提交推送，16 个 worker、三个阶段实际执行。同一服务完成两轮并已回收，中间未重启或重复预热；组件 54.90 秒、性能 453.54 秒。较快的 R2 不替代两轮判定，不追加重测；统一分支继续保留 graph-003。[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6702977197)。
- 空闲 DP 草稿注意力 `codex/dspark-dummy-attn-001` 未保留：两轮 C1/C4/C16 均值 **33.3543 / 34.6939 / 43.4050 ms/token**，收益 **-0.098806% / 0.314410% / -2.312551%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。32 项主机、84 项设备/集成及完整格式通过，已带 sign-off 提交推送；12 个空闲 worker、三个阶段实际执行。同一服务完成两轮并回收，中间未重启或重复预热。组件 24.20 秒、性能 441.98 秒；统一分支继续保留 graph-003。[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6702824827)。
- 前一保留候选：`codex/dspark-attn-graph-003`，两轮 C1/C4/C16 均值 **33.3214 / 34.8034 / 42.4239 ms/token**，相对 target-slot-rows 收益 **-0.145018% / 2.280685% / 6.868377%**，预设 C1/C4/C16 性能 PASS。GSM8K **292/300**、300 成功、零失败、2 条达到 4096 上限按原规则计分；26 项主机、77 项设备/集成及完整格式通过，16 个 worker 实际执行。已带 sign-off 提交推送，统一保留分支已快进并推送。同一服务连续完成两轮和精度，无中间重启或重复预热，已停止回收。组件 24.79 秒、性能 436.40 秒、精度 486.45 秒。精度由父版本 295 降至 292，仍达固定门槛；最终三档 25 ms 尚未达成。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_attn_graph_003/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6702610169)。
- 草稿注意力图 `codex/dspark-attn-graph-002` 未保留：25 项主机、77 项设备/集成及格式检查通过，已提交推送；服务新路径仍为 0，实际 TP4 每卡 16 个注意力头，候选及组件按 64 个设置。R1 提前中止，性能 INCONCLUSIVE、GSM8K NOT_RUN。组件合计 45.41 秒、性能至中止 137.95 秒，服务已回收并恢复保留源码。后续按真实头数和原生填充路径测试。[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6681516812)。
- 草稿注意力图 `codex/dspark-attn-graph-001` 未保留：23 项主机、72 项设备/集成及格式检查通过，已提交推送；服务新路径执行记录为 0，实际 proposer 使用 int32 位置张量而候选仅接受 int64。R2 提前中止，性能 INCONCLUSIVE、GSM8K NOT_RUN，不用部分旧路径结果评价候选。组件 56.68 秒，性能至中止 363.08 秒，服务已回收。下一候选修正准入并覆盖四请求批次。[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6680998380)。
- KV 直接写入 `codex/target-arena-direct-001` 未保留：两轮 C1/C4/C16 均值 **33.4918 / 36.2912 / 46.6763 ms/token**，收益 **-0.657152% / -1.896657% / -2.466724%**，C4/C16 回退超过门槛，性能 FAIL、GSM8K NOT_RUN。最终 22 项相关检查及完整格式通过，16 个 worker 实际执行；实验提交已带 sign-off 推送。一个服务连续完成两轮后已回收，未重启或重复预热，部署源码已恢复为保留的槽位索引版本。组件及诊断 195.67 秒，性能 464.61 秒。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/target_arena_direct_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6680232534)。
- 五行草稿 HC 图 `codex/dspark-hc-single-graph-001` 未保留：两轮 C1/C4/C16 均值 **33.5574 / 36.5072 / 46.4727 ms/token**，收益 **0.004542% / 1.205713% / -2.484117%**，C16 回退超限，性能 FAIL、GSM8K NOT_RUN。20 项本地、71 项设备/主机检查及完整格式通过，16 个 worker 实际执行五行路径，提交已带 sign-off 推送。同一服务完成两轮并回收，中间未重启或重复预热；性能 458.50 秒。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_hc_single_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6678908031)。
- HC 门控融合 `codex/hc-gate-fused-001` 未保留：两轮 C1/C4/C16 均值 **34.3060 / 37.6321 / 48.7209 ms/token**，收益 **-2.226093% / -1.838523% / -7.441924%**，三档回退均超限，性能 FAIL、GSM8K NOT_RUN。58 项相关检查及完整格式通过，16 个 worker 实际执行；实验提交已带 sign-off 推送。服务连续两轮后已回收，无中间重启或重复预热。性能阶段 490.23 秒。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/hc_gate_fused_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6678580758)。
- 草稿环形索引 `codex/dspark-ring-indices-001` 未保留：两轮 C1/C4/C16 均值 **34.0548 / 37.4571 / 47.8321 ms/token**，收益 **-1.477673% / -1.364938% / -5.482014%**，C1 与 C16 回退超过门槛，性能 FAIL、GSM8K NOT_RUN。107 项相关检查及完整格式通过，16 个 worker 实际执行。实验提交已带 sign-off 推送；同一服务完成两轮并已回收，中间未重启或重复预热。性能阶段 473.22 秒。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_ring_indices_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6678092529)。
- 归一化融合 `codex/rms-rsqrt-fused-001` 组件淘汰：31 项检查通过，5120 宽度 BF16 完整输出与父公式不一致，停止该实现。完整格式检查通过，实验提交已带 sign-off 推送。组件执行 20.93 秒；未启动服务，正式性能和 GSM8K 均 NOT_RUN，未保留。[组件记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/rms_rsqrt_fused_001/retained-result.json)。 [同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6677145428)。
- 输出头数据类型 `codex/lm-head-dtype-001` 未保留：两轮均值 **34.4053 / 37.8684 / 49.0662 ms/token**，C16 回退 **4.184337%** 超过门槛，性能 **FAIL**、GSM8K **NOT_RUN**。125 项有效相关检查及完整格式检查通过，实验提交已推送；目标与草稿模型均在 16 个 worker 上执行优化。同一服务完成两轮后已停止回收，中间未重启或重复预热。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/lm_head_dtype_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6676872203)。
- KV 索引组合 `codex/dspark-kv-bookkeeping-001` 未保留：两轮均值 **34.0270 / 37.6718 / 47.6046 ms/token**，预设 C1 收益 **0.966956%** 低于门槛，性能 **FAIL**、GSM8K **NOT_RUN**。141 项相关设备/主机检查及完整格式检查通过，实验提交已推送；16 个 worker 均执行两项优化。同一服务完成两轮后已停止回收，性能阶段 **463.06 秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_kv_bookkeeping_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6676389094)。
- Markov 图回放 `codex/dspark-markov-graph-002` 未保留：两轮均值 **34.5408 / 37.6372 / 49.5121 ms/token**，C16 回退 **5.131177%** 超过门槛，性能 **FAIL**、GSM8K **NOT_RUN**。75 项相关设备/主机检查及完整格式检查通过，实验提交已推送；16 个 worker 均执行候选图回放。同一服务完成两轮后已停止回收，无中间重启或重复预热，性能阶段 **470.30 秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_markov_graph_002/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6676072327)。
- Markov 图回放 `codex/dspark-markov-graph-001` 未保留：两轮均值 **34.4298 / 37.8379 / 46.6226 ms/token**，但全部 worker 均未观察到候选图回放执行，不能据此确认优化效果，性能 **INCONCLUSIVE**、GSM8K **NOT_RUN**。69 项相关设备/主机检查及完整格式检查通过，实验提交已推送。同一服务完成两轮后已停止回收，无中间重启或重复预热；性能阶段 **452.28 秒**。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_markov_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6675463850)。
- 固定草稿槽位 `codex/dspark-dense-slots-001` 未保留：两轮均值 **34.0827 / 37.4305 / 47.0414 ms/token**，三档两轮均改善，但预设 C1 收益 **0.804925%** 低于门槛，性能 FAIL、GSM8K NOT_RUN。107 项相关设备/主机检查及完整格式检查通过，实验提交已推送。16 个 worker 均执行优化，同一服务完成两轮后已停止回收；性能阶段 **452.55 秒**。不调整目标或追加重测；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_dense_slots_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6675152378)。
- 上下文索引 `codex/dspark-context-indices-001` 未保留：两轮均值 **34.1550 / 37.6712 / 47.0132 ms/token**，预设主目标 C1 收益 **0.594386%**，低于门槛，性能 FAIL、GSM8K NOT_RUN。8 项本地、20 项设备/主机及完整格式检查通过，实验提交已推送；16 个 worker 均执行优化。同一服务完成两轮后已停止回收，性能阶段 **455.51 秒**；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_context_indices_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6674928631)。
- 原生前缀索引 `codex/index-tie-prefix-001` 组件淘汰：两种实现各通过 14 项设备/主机检查，但全部四组组件计时均变慢。11 项本地及完整格式检查通过，实验提交已推送；正式性能/GSM8K 均 NOT_RUN，未保留，不启动整机服务。[轮次记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/index_tie_prefix_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6673954341)。
- 草稿 HC 图回放 `codex/dspark-hc-graph-001` 未保留：两轮均值 **33.7704 / 37.5910 / 47.9394 ms/token**，收益 **1.713608% / 0.355992% / -1.791756%**；C16 回退超过门槛，性能 FAIL、GSM8K NOT_RUN。20 项本地、21 项设备/主机及完整格式检查通过，实验提交已推送，同一服务已停止回收。性能阶段 469.02 秒；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_hc_graph_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6672904291)。
- FP32 输入的原生归一化 `codex/rms-fp32-native-001` 未保留：两轮均值 **39.3236 / 34.6242 / 45.7117 ms/token**，C1 回退 **14.448555%**，性能 FAIL、GSM8K NOT_RUN；42 项本地、59 项设备/主机及完整格式检查通过，实验提交已推送，同一服务已停止回收。性能阶段 468.66 秒。已有计数显示 C1 两轮草稿平均接受数均由父版本 2.250794 降至 1.750670，不能以组件收益替代服务结果；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/rms_fp32_native_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6672643362)。
- 页大小索引候选 `codex/index-page-tile-001` 未保留：两轮均值 **34.2699 / 37.5983 / 48.3857 ms/token**，收益 **0.259846% / 0.336871% / -2.739479%**。C16 回退超过门槛，性能 FAIL、GSM8K NOT_RUN；12 项相关检查与完整格式通过，实验提交已推送，同一服务已停止回收。性能阶段 464.71 秒；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/index_page_tile_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6672402296)。
- 索引查询复用组合 `codex/index-query-reuse-001` 未保留：两轮均值 **34.1679 / 37.3842 / 47.7051 ms/token**，收益 **0.556856% / 0.904154% / -1.294253%**。C1/C4 收益未超过门槛，C16 两轮收益一负一正，性能 INCONCLUSIVE、GSM8K NOT_RUN；16 项相关检查及完整格式检查通过，实验提交已推送，同一服务已回收。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/index_query_reuse_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6672080098)。
- 单独索引掩码 `codex/index-mask-elide-001` 未保留：两轮均值 **33.8575 / 37.5620 / 47.3813 ms/token**，收益 **1.460082% / 0.433072% / -0.606642%**。C4 两轮收益一正一负，按预设规则性能 INCONCLUSIVE、GSM8K NOT_RUN；28 项相关及格式检查通过，实验提交已推送，同一服务已回收。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/index_mask_elide_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6671784242)。不重跑该候选选择有利结果；新组合以保留父版本独立验证。
- 原生 RMSNorm `codex/rms-native-001` 未保留：两轮均值 **38.6443 / 33.9121 / 45.2937 ms/token**，C4/C16 改善但 C1 回退 **12.471467%**，性能 FAIL、GSM8K NOT_RUN。42 项本地、56 项 NPU 检查及完整格式检查通过，实验提交已推送，服务已回收。两轮间未重启或重复预热；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/rms_native_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6671547195)。
- 草稿 HC `codex/dspark-hc-padded-001` 未保留：两轮均值 **33.7751 / 36.6585 / 49.2627 ms/token**，C1/C4 改善但 C16 回退 **4.601589%**，性能 FAIL、GSM8K NOT_RUN。70 项本地和 23 项 NPU 检查通过，实验提交已推送，服务已回收；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/dspark_hc_padded_001/retained-result.json)；[同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6671117968)。
- 旋转复用候选 `codex/rotary-reuse-001` 未保留：两轮均值 **35.8757 / 40.0335 / 49.6040 ms/token**；预设 C1 收益 **1.007088%**，低于 **1.093141%**，性能 FAIL，GSM8K NOT_RUN。79 项相关检查通过、2 项既有条件跳过，代码已提交并推送；同一服务完成两轮且已回收。[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/rotary_reuse_001/retained-result.json)；[已同步 #353](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6669909307)。
- 已淘汰候选：`codex/index-device-select-002` 四次组件尝试未通过，最终连续排名写入仍在图捕获时报同步复制失败，已停止该方向调试并推送实验提交，服务性能及精度均未运行；[组件结论](/Users/jiangchenzhou/code/dsv41-0day-20261102/index_device_select_002/summary.md)。FP8 草稿/预填充候选的两轮均值为 **35.4875 / 39.1045 / 48.2288 ms/token**，但 GSM8K 为 **291/300**，未保留；[实测记录](/Users/jiangchenzhou/code/dsv41-0day-20261102/fp8_runtime_coverage_001/retained-result.json)。组合 FP4 候选同样因精度未达标淘汰，首个索引候选因图捕获失败停止。
- 后续直接父版本采用最近有效保留结果，见 [slot-arena](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6652229469)、[DSpark staging](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6654942712)。目标尚未完成，issue 保持打开；恢复时核对实际提交与部署身份。
- 历史 C32、旧配置结果和原判定保持原样，不追溯改判，也不作为新协议的必需证据。

## 2. 工具、知识与开发边界

- 设备操作遵循 `itask-cli-guide`；InferRSI 遵循 `plugins/inferrsi/skills/inferrsi/SKILL.md`。使用既有 InferRSI `.venv`，分支 `codex/vllm-ascend-0271rc1-skill`，记录实际 revision。
- 每轮实施前实际查询 InferRSI，**重点阅读 cannbot、vllm、vllm-ascend、Ascend 知识库正文，仅禁止 DeepInfer 及其转载、派生内容**。其他模型专属知识和外部资料允许；混合包按条目排除，不整包跳过。
- 在 `plan/<round>/knowledge-hits.md` 记录查询范围、版本、条目、阅读及采用情况，RunSpec 引用记录路径。同一假设的已有查询直接沿用，不重复查询；不用源码阅读冒充知识查询。
- 沿用插件、已有 patch 和算子扩展架构，遵守 AGENTS.md。新增环境变量集中定义；NPU 热路径避免不必要同步，按改动覆盖数值、形状、缓存、图回放、通信及受影响消费者。
- 快筛用于排序，**有实际改善的候选不因未达预估快筛收益而直接剔除**；保留并安排正式验证。微基准或组件正确性通过不等于服务性能、模型精度通过。

## 3. 固定服务配置

| 项目 | 配置 |
| --- | --- |
| 并行与权重 | 单机 PD 混部，TP4 / DP4 / EP16，expert parallel；既有 W8A8 权重，不重新量化 |
| 投机与图 | DSpark，`num_speculative_tokens=5`；`mode=0`、`FULL_DECODE_ONLY`、capture sizes `[24,48]` |
| 上下文与调度 | `max_model_len=153600`、`block_size=128`、每 DP `max_num_seqs=8`、`max_num_batched_tokens=8192` |
| Ascend 开关 | `enable_dsa_cp=true`、`enable_flashcomm1=true`、`VLLM_ASCEND_ENABLE_FLASHCOMM1=1`、`enable_shared_expert_dp=true`、`enable_fused_mc2=1`（整数） |
| 执行路径 | target/draft Ascend grouped W8A8；前缀缓存开启 |
| 模板与接口 | 既有冻结 chat template，`reasoning-parser=deepseek_v3`，content format `openai`；loopback，服务名 `dsv41-0day`；文本输入 |

恢复前确认实际源码/算子部署位置与启动参数，沿用部署记录和目标提交；存在源码覆盖时如实记录，不能仅凭 Git HEAD 认定部署一致。上游 vLLM 沿用现有固定版本。

## 4. 性能协议与判定

### 4.1 请求和计时

每候选仅启动一次服务，在同一提交、权重与配置上连续完成 **R1 → R2 两轮测量**。R1 按 C1/C4/C16 升序，各档先做一次 C 条必要预热，再做 C 条同步正式请求；R2 按同样顺序直接做正式请求，**两轮之间不重启、不再预热、不重复健康探针**。合计 **21 条预热＋42 条正式请求**，首次健康探针单列。R1/R2 是测量轮次，不是两个服务。

本调整从后续候选开始；已完成或正在执行的旧轮次保留原记录，不为切换流程重跑。与历史父结果比较时记录服务复用及预热次数的差异，不因此自动追加父版本或 A/A 测试。

首次健康探针仅一批 C4 请求，同时完成指标初始化、输出及回放检查；后续各档预热和正式请求沿用正常计数检查，不再额外发送第二批健康探针。该精简从压缩 KV 的 FP4 E4M3 候选开始，不改变正在执行的轮次。

- 预热 8192 输入 / 32 输出；正式 8192 / 1024。沿用已固定、互不重叠的两个 32 条 raw-token 输入库，仅使用各库前 16 条及每档前 C 条；记录输入文件路径和所选索引。数据来自 GSM8K train question，不用精度 test 答案。
- `/v1/completions`：stream、include_usage、return_token_ids 开启；`echo=false`、`add_special_tokens=false`、`ignore_eos=true`、temperature=0、top_p=1、seed=0、n=1；正式 `min_tokens=max_tokens=1024`。
- barrier 同步发送；`X-data-parallel-rank=slot%4`；每 attempt 使用唯一 `cache_salt`，逐请求核验 `cached_tokens=0`。既有 HTTP/barrier timeout 为 1800/60 秒，运行前冻结实际值。
- 用 `perf_counter_ns`：start 为打开 HTTP 前，first 为首个含生成 token ID 的完整 SSE frame，end 为 HTTP EOF（含 usage、DONE）。一帧可含多个 token，不能用帧数代替 token 数。

```text
TTFT_i = (first_i - start_i) / 1e6
E2E_i  = (end_i - start_i) / 1e6
TPOT_i = (end_i - first_i) / 1e6 / (output_i - 1)
B_r(C) = 该档该轮全部请求 TPOT 的算术平均
版本 TPOT(C) = median(R1(C), R2(C)) = (R1(C) + R2(C)) / 2
```

保留所有请求与尾部 drain，不裁剪慢样本。核验数量、token IDs/长度、错误、缓存、身份及 SSE 可复算性；失败保留原记录，同一有效服务可用新 attempt 重跑完整该档，不自动追加服务。无法完成记 INCONCLUSIVE。此协议衡量固定请求波延迟，不据此推断持续负载 SLO。

### 4.2 中间候选与最终验收

首个请求前记录假设、预设目标档、父/候选版本、输入、配置和参考结果，沿用已有计时与评分工具。每档父值 P 为**直接父版本**已有完整可比有效轮均 TPOT 的中位数；预先确定所用轮集合、run ID 和路径，不按候选结果挑选。历史对照须披露时间间隔及环境可比性限制。

沿用[校准报告](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6641425447)完整精度门槛：C1 约 1.093141%、C4 约 1.373789%、C16 约 1.633942%。计算 `g1=(P-R1)/P`、`g2=(P-R2)/P`，按以下顺序用未舍入值判定：

1. 三档候选或父参考证据缺失、环境不可比：**INCONCLUSIVE**，不自动重测父版本或用更早版本替代。
2. 任一档 `median(g1,g2)<-threshold_C`，或 `P≤25` 而 `median(R1,R2)>25`：**FAIL**。
3. 任一预设目标档两次收益一正一负：**INCONCLUSIVE**。否则至少一个目标档两次均改善且收益中位数超过门槛：中间性能 **PASS**；仅等于门槛记 INCONCLUSIVE，其余不满足收益条件记 FAIL。
4. 性能 PASS 后测精度；FAIL/INCONCLUSIVE 时精度记 **NOT_RUN**，不冒用父版本精度。用户单独要求精度时按该次要求执行。

**最终交付**：同一最终提交在一个服务上完成两轮有效性能测量，三档 TPOT 中位数各自 ≤25，并通过精度与功能核验。该版本已有的有效两轮结果可直接用于验收，不为最终验收标签再次重启、预热或补跑；后续代码、配置改变才重新测。最终绝对目标不作为中间候选的晋级门槛。配置、权重或负载实质变化单列，不套用不可比证据。

## 5. 精度与服务复用

执行顺序：**启动候选服务一次 → 必要预热及 R1 性能 → 同服务直接测 R2 → 两轮判定 → PASS 后同服务跑 GSM8K → 核验并停止服务**。两轮之间与精度前均不重启。服务失效时记录具体原因及替换服务身份，不能冒充连续复用。

| 项目 | 冻结要求 |
| --- | --- |
| 数据 | GSM8K revision `3101c7d5072418e28b9008a6636bde82a006892c`；test 1319 题中 `sorted(random.Random(42).sample(range(1319),300))`，题序固定 |
| 评分器 | AISBench `5a63d936e40dd04addfcffb2401f84cd0e53bb46`，原生 `Gsm8kEvaluator` |
| 提示 | `gsm8k_gen_0_shot_cot_chat_prompt`，zero-shot CoT，冻结模板和 wire prompts |
| 推理与采样 | `thinking_mode=thinking`、`enable_thinking=true`、`reasoning_effort=low`；temperature=0、top_p=1、seed=0 |
| 请求 | 300 题，C32，0 次预热，每题一次，输出上限 4096；不继承性能强制输出 1024 的参数 |
| 有效性与门槛 | 300 个唯一题目和对应 attempt/response，零请求失败；原生答对 **≥292/300**，始终锚定最初 295/300 |

精度使用独立 run ID，记录两轮测量共用的 service ID、PID/start ticks、源码/算子/权重及配置。性能原始记录保存、判定完成并排空请求后，立即开始精度；指标按阶段快照取差，记录继承的缓存状态。截断按原规则评分，不剔除或重试到答对；final 正文评分、提取失败与截断数辅助报告，不替换主评分。配置、数据、题序及提示沿用固定资产，历史 16K 配置不能直接当作当前证据。

## 6. 每轮耗时、归档与交付

从首次查询/分析到保留、淘汰或中止后的归档结束，实时记录：**分析思考、知识查询/阅读、编码、构建/部署、调试分析、组件验证、服务准备/回收、性能预热、正式性能、精度、复算/审查、归档/提交、等待/暂停、未归因时间**。失败及重试分别记录，R1/R2 不重复计开发成本。

阶段切换时沿用 `plan/<round>/time-ledger.jsonl` 记录 round/attempt ID、类别、起止时间、状态、阻塞原因和日志路径；不为计时扩建工具或阻塞测试。收尾简述整轮及主要阶段耗时，已有明细可直接引用；未知不填 0，不从差额或文件 mtime 反推。

依赖服务存活的检查在回收前完成；R1 完成后立即在同一服务上测 R2，判定通过后立即测精度。记录首次启动和最终回收时间；原件齐备后可离线整理，已通过检查仅在输入变化、失败或证据冲突时重做。

实验根目录为既有 `dsv41-0day-20261102/`，本阶段 `resume-8k1k-20261104/`：

| 目录/资产 | 用途 |
| --- | --- |
| `plan/` | 运行配置、知识记录、输入/工具路径、父参考与门槛、耗时事件 |
| `results/` | 原始请求/SSE、指标/日志、精度输出、复算、耗时、停止状态及判定 |
| `patch/`、`validator/` | 父/候选源码与部署记录；已有计时、评分和请求有效性检查 |
| `plan/input-ids-8k.json`、`plan/client-release-002.json` | 已冻结 8K 输入及 release，使用前核对其引用关系 |
| `aisbench/gsm8k/subset300/`（实验根目录下） | 精度 release、selection manifest、`data/test.jsonl`；提示映射沿用原归档 |
| `results/non-evaluation-timing-20261105/` | 历史非测评耗时明细及证据；缺失的思考/编码时间保持未知 |
| `plan/concise-plan-20261105-001/plan-before.md` | 精简前全文，仅作历史记录，不覆盖现行军规，不要求补齐历史流程 |

原始结果保存文件与路径；公开 issue 只放脱敏摘要。每轮报告优化内容、父/候选版本、P/R1/R2、收益与门槛、精度、功能和主要耗时。正式保留须性能、精度、功能及配置均通过；工作 checkpoint 单列。按 Conventional Commits、`git commit -s` 提交，执行仓库要求的检查，推送 fork；不为归档增加前置流程。

每轮完成后及时在 #353 同步脱敏实测结果及保留/淘汰结论，不只更新本地记录。HCPre 至 FP8 的七轮服务结果及索引组件失败已补齐到 [2026-11-06 汇总记录](https://github.com/InferMatrixLab/InferRSI/issues/353#issuecomment-6669198630)。

**统一保留分支：[codex/dsv41-retained](https://github.com/jiangkuaixue123/vllm-ascend/tree/codex/dsv41-retained)。** 当前指向已保留的 `codex/target-query-overlap-002`，包含此前累计保留的优化。各轮继续使用独立实验分支并带 sign-off 提交推送；仅当同一候选的正式性能、GSM8K 和功能均通过并判定保留后，才将统一分支快进到该候选并推送，不改写历史。未完成验证或未保留的候选不更新该分支。每次更新同时记录到 #353。

## 7. 恢复执行前待办

- 核对最新保留提交、实际部署、设备租约与健康；确认旧协议父服务已停止且无冲突流量。
- 直接使用已有可用服务生命周期和 **C1/C4/C16** 测试客户端，在同一候选服务上完成两轮测量及精度复用。仅修复阻止实测的具体问题；旧 C1/C32 快筛结果不冒充当前三档结果。
- 按“单假设优化 → 必要检查 → 两轮服务性能 → 精度”推进，直至最终验收；已有知识查询直接沿用，记录和提交随实际工作完成，不阻塞下一项测试。
