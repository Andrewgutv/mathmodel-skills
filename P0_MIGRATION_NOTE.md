# P0 整改迁移说明

当前第一轮 `P0` 整改已经新增以下现代版脚本：

- `scripts/parse_prompt_modern.py`
- `scripts/summarize_results_modern.py`
- `scripts/run_pipeline_modern.py`

## 目的

由于旧版脚本存在历史编码乱码与契约不一致问题，第一轮整改先采用“新增现代版脚本并切换入口”的方式推进，避免在旧文件上做高风险原地修补。

## 当前建议入口

在整改期间，优先使用：

```powershell
python scripts/run_pipeline_modern.py <项目路径> --stage all
```

如果只跑解析阶段：

```powershell
python scripts/parse_prompt_modern.py <项目路径>
```

如果只跑结果汇总阶段：

```powershell
python scripts/summarize_results_modern.py <项目路径>
```

## 已完成的 P0 内容

- 题面输入支持扩展到 `pdf / docx / markdown / 图片`
- 新增 OCR 不可用、OCR 失败、题面为空、零问题识别等状态区分
- 新增“所有问题都要有真实结果”校验，避免 `solve` 假通过
- 新增更严格的结果汇总前置校验
- 旧入口 `parse_prompt.py / run_pipeline.py / check_paper.py` 已收敛为 modern 包装器
- 新脚手架模板默认改为指向 `run_pipeline_modern.py` 与 `parse_prompt_modern.py`

## 尚未完成的 P0 内容

- 旧脚手架入口模板切换到现代版脚本
- `check_paper.py` 通用化
- `SKILL.md` 中必须项/按需项契约收敛

## 后续处理原则

- 短期：继续在现代版脚本上推进整改
- 中期：在完成 P0 后，将现代版脚本回收为正式入口名
- 长期：删除旧版乱码脚本或将其保留为历史兼容层
