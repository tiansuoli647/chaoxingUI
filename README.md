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
    <img src="https://img.shields.io/badge/python-3.13+-blue.svg" alt="Python Version" />
    <img src="https://img.shields.io/badge/license-GPL--3.0-green.svg" alt="License" />
</p>

:muscle: **本项目的最终目的是通过开源消灭所谓的付费刷课平台**。希望有能力的朋友都可以为这个项目提交代码，支持本项目的良性发展。觉得有帮助的朋友可以点一个 **Star**。

---

## :sparkles: 核心功能特性

### 1. :desktop_computer: 北极光 Web 可视化控制台 (全新推出)
* **极光美学界面**：采用现代深色系极光主题（Vue 3 + Tailwind/Glassmorphism 视觉系统），设计优雅，体验丝滑。
* **可视化配置与登录**：支持输入账号密码登录或通过 Cookie 登录，一键获取当前账号下所有课程。
* **实时日志流与状态监测**：在网页端实时直观地查看详细运行日志、当前学习课程、学习章节与异常警示。
* **任务一键控制**：提供一键“开始刷课”与“安全退出”，内置智能 Monkeypatching 拦截技术，保证随时安全挂起与中断任务点。

### 2. :terminal: 经典 CLI 命令行模式
* 支持经典的命令行交互引导，对于低配置环境或轻量服务器运行更友好。
* 支持配置文件（`config.ini`）一键启动，也可通过 CLI 参数（`-u`, `-p`, `-l`, `-a`）快捷执行。

### 3. :brain: 智能题库适配与多端回退答题
* **广泛兼容**：支持对接 `TikuYanxi` (言溪题库)、`TikuLike` (LIKE 知识库)、`TikuAdapter`、`TikuGo` 等开放题库。
* **AI 强力赋能**：支持接入各大兼容 OpenAI 接口规范的 API（如 **DeepSeek-V3 / DeepSeek-R1**、硅基流动 SiliconFlow、GPT 等）进行智能大模型答题，支持联网搜索与图片视觉识别题目。
* **多级题库回退**：可配置多个题库并按优先级顺序依次查询，实现备用覆盖。
* **自定义提交行为**：支持配置提交阀值（覆盖率不足仅保存不提交，防止拉低平时分；或者章节解锁强制提交），充分保证答题安全。

### 4. :gear: 底层稳定保障
* **多线程并发**：支持多章节（Jobs）同时并行处理，视频倍速自适应（最大支持 2 倍速播放）。
* **关闭任务点智能重试**：遇到关闭的任务点支持重试上一个任务点（自动重试3次）、友好询问或直接跳过，完美应对章节解锁锁限制。
* **旧版 Python 兼容**：内置平滑降级机制，向下兼容不支持 `queue.ShutDown` 等新特性低版本 Python 环境。

---

## :point_up: 快速上手指南

### 方式 1：使用极简网页版（强烈推荐 :star:）

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

### 方式 2：使用源码命令行运行（Python 3.13+）

1. **克隆项目到本地**：
   ```bash
   git clone --depth=1 https://github.com/tiansuoli647/chaoxingUI.git
   cd chaoxingUI
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
   *(或使用 `pip install .` 通过 pyproject.toml 安装)*
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
> 如果您本地装有低版本 Python，或者不想全局安装依赖包，可以使用高速管理工具 `uv` 一键拉取 Python 3.13 并隔离运行：
> * **启动 Web 控制台**：`uv run --python 3.13 web_server.py`
> * **使用配置文件启动 CLI**：`uv run --python 3.13 main.py -c config.ini`

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
model =                 ; 选用模型，如果为空将根据 endpoint 智能识别 (如 deepseek-chat 等)
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

* 本代码遵循 **[GPL-3.0 License](https://github.com/tiansuoli647/chaoxingUI/blob/main/LICENSE)** 协议，允许开源/免费使用和引用/修改/衍生代码的开源/免费使用，**不允许修改和衍生的代码作为闭源的商业软件发布和销售**，禁止使用本代码盈利，以此代码为基础的程序**必须**同样遵守 GPL-3.0 协议。
* 本代码仅用于**技术与学术学习讨论**，禁止用于任何形式的盈利性商业刷课平台。
* 他人或组织使用本代码进行任何**违法或违规行为**，与本项目开发者及贡献者无关。
