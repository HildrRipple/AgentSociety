# AgentSociety

**AgentSociety** 是一个基于社会学第一原理构建的社会模拟引擎和社会科学研究工具包，利用大型模型代理。它旨在推动社会科学研究方法论的范式转变，促进从行为模拟到心智建模，从静态推导到动态共存，以及从实验室工具到社会基础设施的发展。
论文可在 [arXiv](https://arxiv.org/abs/2502.08691) 获取：

```
@article{piao2025agentsociety,
  title={AgentSociety: Large-Scale Simulation of LLM-Driven Generative Agents Advances Understanding of Human Behaviors and Society},
  author={Piao, Jinghua and Yan, Yuwei and Zhang, Jun and Li, Nian and Yan, Junbo and Lan, Xiaochong and Lu, Zhihong and Zheng, Zhiheng and Wang, Jing Yi and Zhou, Di and others},
  journal={arXiv preprint arXiv:2502.08691},
  year={2025}
}
```

<img src="_static/framework-overview.jpg" alt="AgentSociety的整体结构" style="zoom=28%;" />

## 新闻

版本1.3.0已发布！

查看[版本1.3](./02-version-1.3/index.md)了解最新更新和新功能🎇。

## 特点

- 🌟 **大模型驱动的社会人类代理**：基于社会学理论，构建具有"类人心智"的社会代理，赋予他们情感、需求、动机和认知能力。这些代理在这些心理属性的驱动下执行复杂的社会行为，如移动、就业、消费和社交互动。我们还支持[代理的自定义](./05-custom-agents/index.md)。
- 🌟 **真实的城市社会环境**：它准确地模拟了对社会人类生存至关重要的城市空间，复制了交通、基础设施和公共资源。这使代理能够在现实世界的约束下互动，形成生动的社会生态系统。
- 🌟 **大规模社会模拟引擎**：通过采用异步模拟架构和[Ray](https://www.ray.io/)分布式计算框架结合代理分组，实现了代理之间的高效、可扩展的互动和社会行为模拟。
- 🌟 **社会科学研究工具包**：它全面支持一系列社会学研究方法，包括[访谈和调查](./04-experiment-design/01-survey-and-interview.md)、[消息控制工具](./04-experiment-design/03-message-interception.md)和[指标提取器](./04-experiment-design/02-metrics-collection.md)，提供各种自动化数据分析工具，促进从定性研究到定量分析的深入社会科学研究。

## 在线演示

<!-- ![AgentSocietyDemo](_static/agentsociety-demo.png) -->

![AgentSociety](_static/ui-demo.gif)

我们提供了模拟平台的[在线演示](https://agentsociety.fiblab.net/)。

体验我们的在线演示，它模拟了飓风事件期间个人的行为模式，基于飓风多里安对南卡罗来纳州哥伦比亚的实际影响。
详细信息和用例说明可在[飓风影响](./07-use-case/04-hurricane-impact.md)中获取。

## 安装

参考快速入门部分了解[先决条件](./01-quick-start/01-prerequisites.md)和[安装](./01-quick-start/02-start-your-first-simulation.md#step-0-installation)说明。

## 联系我们

我们诚挚邀请社会科学、大语言模型和代理领域的学者探索我们的平台。
研究人员可以通过[电子邮件](mailto:agentsociety.fiblab2025@gmail.com)联系我们并提交您的研究提案。获批的申请者将获得测试版凭证，在我们团队的指导下在平台上进行实验。

我们欢迎通过我们的平台推进社会科学研究的合作机会。

## 微信群

<img src="_static/wechat.png" alt="微信" style="width: 30vw;" />

## 目录

```{toctree}
:maxdepth: 2

``` 