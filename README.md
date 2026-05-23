# :compass: 超星学习通全自动刷课与答题系统 (北极光控制台)

<p align="center">
    <a href="https://github.com/tiansuoli647/chaoxingUI" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/stars/tiansuoli647/chaoxingUI" alt="Github Stars" />
    </a>
    <a href="https://github.com/tiansuoli647/chaoxingUI" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/forks/tiansuoli647/chaoxingUI" alt="Github Forks" />
    </a>
    <a href="https://github.com/tiansuoli647/chaoxingUI" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/languages/code-size/tiansuoli647/chaoxingUI" alt="Code-size" />
    </a>
    <a href="https://github.com/tiansuoli647/chaoxingUI" target="_blank" style="margin-right: 20px; font-style: normal; text-decoration: none;">
        <img src="https://img.shields.io/github/v/release/tiansuoli647/chaoxingUI?display_name=tag&sort=semver" alt="version" />
    </a>
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/license-GPL--3.0-green.svg" alt="License" />
</p>

:muscle: **本项目的最终目的是通过开源消灭所谓的付费刷课平台**。希望有能力的朋友都可以为这个项目提交代码，支持本项目的良性发展。觉得有帮助的朋友可以点一个 **Star**。

---

## :link: 项目来源与致谢

本项目基于优秀的开源项目 **[Samueli924/chaoxing](https://github.com/Samueli924/chaoxing)** 二次开发与重构。

在此，对原作者 **Samueli924** 以及所有上游贡献者表示由衷的感谢与敬意！原项目提供了一个极为扎实且稳定的超星协议层底层机制，为本项目的高级扩展奠定了坚实的基础。

---

## :rocket: 我们的核心新特性

在原项目强大的底层协议基础上，本项目进行了深度的用户体验升级与环境适配，推出了以下独有特性：

### 1. :desktop_computer: 全新推出「北极光 Web 可视化控制台」
* **告别枯燥的命令行**：为不懂技术的普通用户量身打造，通过漂亮的网页界面，彻底告别复杂的终端参数输入。
* **极光美学 UI 设计**：采用精心设计的深色系极光主题（Vue 3 + Glassmorphism 玻璃拟态），界面灵动响应，尽显高级质感。
* **可视化操作流**：
  * **登录阶段**：支持一键输入账号密码或粘贴 Cookie 登录，登录成功自动保存配置。
  * **课程选择**：登录后自动获取名下的所有课程，提供复选框自由勾选想要学习的课程，免去手动查找课程 ID 的烦恼。
  * **配置管理**：支持在网页端直接编辑配置选项，无缝读取并保存至本地 `config.ini`。
* **实时日志流与状态面板**：实时流式输出刷课运行日志，以卡片形式直观展示当前课程、当前章节和发生的错误提示。
* **安全进程控制机制**：内置创新的网络与线程 Monkeypatching 劫持技术，随时点击“安全停止”，底层会自动捕获并优雅退出正在执行的任务队列，杜绝线程死锁与卡死。

### 2. :snake: Python 旧版本环境平滑兼容 (Backward Compatibility)
* **降低运行门槛**：原项目要求 Python 3.13+ 以支持其高级队列特性。
* **平滑回退机制**：本项目重构了并发任务调度模块，对低版本 Python（如 Python 3.8+）中缺失的 `queue.ShutDown` 异常和 `.shutdown()` 方法进行了优雅的向下兼容处理，使您无需强行升级系统 Python 即可直接运行。

### 3. :brain: 智能大模型（如 DeepSeek-V3 / DeepSeek-R1）答题健壮性提升
* **大模型零配置智能识别**：重构了 AI 答题接口层，支持如果用户未指定模型类型，程序将自动分析大模型 Endpoint。当检测到 `deepseek` 等关键字时，自动回退并应用 `deepseek-chat` 作为默认模型，避免因未填写模型参数而导致程序崩溃。
* **健壮的参数解析**：增强了配置项的参数容错（如 `min_interval_seconds` 自动纠错解析），即便配置文件填写格式有瑕疵，系统也能保障稳健调用。

---

## :point_up: 快速上手指南

### 方式 1：使用网页控制台（强烈推荐 :star:）

网页版提供全图形化配置与实时状态控制，最适合新手用户。

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
2. **启动 Web 控制台**：
   ```bash
   python web_server.py
   ```
3. **开始使用**：
   在浏览器中打开：[http://127.0.0.1:5000](http://127.0.0.1:5000)，在“配置管理”中配置好您的账号密码或题库（首次运行会自动以 `config_template.ini` 为模版生成 `config.ini`），在主页点击“开始刷课”即可。

---

### 方式 2：使用源码命令行运行 (CLI)

1. **克隆项目到本地**：
   ```bash
   git clone --depth=1 https://github.com/tiansuoli647/chaoxingUI.git
   cd chaoxingUI
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
3. **选择启动模式**：
   * **直接运行 (交互式输入)**：
     ```bash
     python main.py
     ```
   * **使用配置文件运行**：
     将项目根目录下的 `config_template.ini` 复制并重命名为 `config.ini`，修改其中的配置项，然后执行：
     ```bash
     python main.py -c config.ini
     ```
   * **命令行参数单次运行**：
     ```bash
     python main.py -u 手机号 -p 密码 -l 课程ID1,课程ID2...(可选) -a [retry|ask|continue](可选)
     ```

> [!TIP]
> **高效工具推荐 (`uv` 运行)**：
> 如果您不想全局安装依赖包，可以使用高速管理工具 `uv` 一键拉取并隔离运行：
> * **启动 Web 控制台**：`uv run web_server.py`
> * **使用配置文件启动 CLI**：`uv run main.py -c config.ini`

---

### 方式 3：使用 Docker 容器化运行

1. **构建 Docker 镜像**：
   ```bash
   docker build -t chaoxing-ui .
   ```
2. **运行 Docker 容器**：
   ```bash
   # 挂载自定义配置文件启动
   docker run -it -v /您的本地路径/config.ini:/config/config.ini chaoxing-ui
   ```

---

## :notebook_with_decorative_cover: 核心配置选项解读 (`config.ini`)

在项目目录的 `config.ini` 文件中，您可以对其进行深度定制：

```ini
[common]
; 使用 Cookie 登录，填写 true 则忽略账号密码，直接从 cookies.txt 读取
use_cookies = false
username = xxx          ; 手机号账号 (必填)
password = xxx          ; 登录密码 (必填)
course_list = xxx,xxx   ; 要学习的课程 ID 列表 (用英文逗号隔开，选填)
speed = 1.0             ; 视频播放倍速 (默认 1.0，最大 2.0)
jobs = 4                ; 同时进行的章节数量
notopen_action = retry  ; 遇到关闭任务点时的行为 (retry-重试, continue-继续, ask-询问)

[tiku]
; 选填，支持配置多个题库回退查询，如：provider = TikuYanxi,TikuGo,AI
provider = TikuYanxi    ; 选用的题库，大小写必须一致
submit = false          ; 是否自动提交答题（true: 覆盖率达标自动提交；false: 仅保存答案不提交）
cover_rate = 0.9        ; 最低题库覆盖率 (搜到答案占比达到 90% 才考虑提交)
tokens =                ; 言溪题库/LIKE知识库需要的 Token 密钥

; AI大模型/DeepSeek智能答题配置
endpoint =              ; API Endpoint 地址 (例如: https://api.deepseek.com/v1)
key =                   ; 您的 API 密钥 Key
model =                 ; 选用模型，如果为空将自动识别
```

---

## :shield: 隐私与安全保障

为了您的信息安全，以下敏感文件已被默认写入 `.gitignore` 中，**绝对不会**被提交或上传到任何公开仓库，您可以放心在本地使用：
* `config.ini` / `config*.ini` (包含明文账号密码)
* `cookies.txt` / `.cookies.txt` (包含登录 Cookie)
* `chaoxing.log` (运行日志，包含课程细节与账号名)
* `cache.json` (临时缓存文件)

---

## :warning: 免责声明

* 本代码遵循 **[GPL-3.0 License](https://github.com/tiansuoli647/chaoxingUI/blob/main/LICENSE)** 协议，允许开源/免费使用和引用/修改/衍生代码的开源/免费使用，**不允许修改和衍生的代码作为闭源的商业软件发布 and 销售**，禁止使用本代码盈利，以此代码为基础的程序**必须**同样遵守 GPL-3.0 协议。
* 本代码仅用于**技术与学术学习讨论**，禁止用于任何形式的盈利性商业刷课平台。
* 他人或组织使用本代码进行任何**违法或违规行为**，与本项目开发者及贡献者无关。
