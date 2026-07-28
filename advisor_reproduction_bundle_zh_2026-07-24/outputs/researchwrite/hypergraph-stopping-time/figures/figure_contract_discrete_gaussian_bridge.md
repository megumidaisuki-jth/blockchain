# 图件合同：离散—高斯停止时间桥接

- 核心结论：两通道原子路由路径上的确定性 Poisson 数值解收敛到中心高斯生存序预测，而最小有限尺度说明该定理不能表述为有限 \(N\) 符号律。
- Figure archetype: quantitative grid with two aligned validation panels.
- 目标/输出：中文论文验证图；依照作者持续有效的偏好仅输出 PNG。
- Backend: Python/matplotlib only.
- Final size: 183 mm × 86 mm, white background, 600 dpi.
- 面板 a：\(N=1,2,\ldots,256\) 的确定性归一化相关/独立代理 Poisson 数值均值及极限基准。
- 面板 b：确定性归一化差值及外推高斯极限，显式保留零线。
- Evidence hierarchy: deterministic Poisson solutions are primary; the analytic independent Brownian series is an independent numerical benchmark; asymptotic extrapolation is supporting evidence rather than proof.
- Statistics: no sampling and no error bars; report linear-system residuals, series truncation discrepancy, and extrapolation-window sensitivity.
- Source data: all nine scales, both exact means, residuals, analytic benchmark and extrapolation diagnostics are retained in CSV/JSON.
- Image integrity: no observations omitted; no smoothing; plotted lines connect computed grid values only.
- 审稿风险：正的极限估计不得与普遍有限尺度符号定理混淆；\(N=1\) 的负效应必须保留；双精度 Poisson 解不得称为解析精确值。
