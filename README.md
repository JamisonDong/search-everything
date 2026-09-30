# 人员数据智能检索与态势分析大屏系统

> 专为政府工作人员打造的 **1600万级** 大数据离线检索、态势感知大屏与单机涉密管理系统。

![态势大屏预览 (1600 万条仿真数据)](docs/dashboard-preview.png)

---

## 🌟 核心特色与优势

1. **1600 万级数据秒级交互**：
   - 底层采用 **DuckDB** 嵌入式列存向量化执行引擎，宏观聚合统计（年龄金字塔、重点城市排行、收入梯次分布）耗时通常在 **20~50 毫秒** 以内。
   - 复合多条件搜索（姓名/外文名/身份证/街道地址关键字联动）响应迅速。
2. **100% 离线单机部署 (零外部依赖)**：
   - 不依赖 Docker，不依赖远程数据库服务，无需外网连接。
   - 所有可视化图表库（ECharts）、前端静态资源全部本地打包，杜绝任何外联请求。
3. **涉密与政务合规保障**：
   - **屏幕防拍动态水印**：Canvas 全屏浮动水印（工号 + 终端标识 + 实时秒级时间戳），防止手机拍照泄密，支持防审查元素篡改。
   - **安全操作审计日志**：自动记录所有搜索关键词、调阅人员档案、筛选条件及耗时，留存至本地防篡改日志文件 `logs/audit_log.jsonl`。
   - **一键敏感脱敏模式**：在向公众或非密级人员做汇报演示时，可一键切换为脱敏模式（姓名打码、身份证打码、收入掩码）。
4. **20+ 原始 CSV 智能导入管线**：
   - 自动识别 `UTF-8`、`GBK`、`GB18030` 等多种编码格式。
   - 自动执行数据清洗、类型推断、异常值兜底、基于 `id` 的主键排重与多维索引构建。
5. **汇报级态势大屏 + 检索工作台双视图**：
   - 默认打开 **态势大屏**：按 1920×1080 设计、任意分辨率等比铺满一屏，一键全屏，适合投屏/拼接屏向领导汇报。
   - 大屏只展示聚合统计（总量翻牌器、城市分布、年龄金字塔、性别与收入结构、审计动态），**不出现任何个人明细**；审计动态中的证件号自动打码、不显示检索关键词。
   - 点击城市柱图或排行榜可直接下钻到 **检索工作台** 做人员明细检索与档案调阅。

---

## 📁 目录结构

```
search-everything/
├── backend/                  # 后端服务源码 (Python 3 + FastAPI + DuckDB)
│   ├── app/
│   │   ├── api/              # RESTful API 接口路由
│   │   ├── core/             # 系统配置与安全定义
│   │   ├── db/               # DuckDB 数据库连接池
│   │   └── services/         # 大屏聚合、全文检索、安全审计服务
│   ├── scripts/
│   │   ├── import_csv.py     # 20+ CSV 1600w 数据高效导入与建索引脚本
│   │   └── generate_mock.py  # 高仿真脱敏测试数据生成器
│   ├── requirements.txt      # 后端依赖清单
│   └── main.py               # 服务启动主入口
├── frontend/                 # 涉密大屏前端源码 (Vue 3 + ECharts + TailwindCSS)
│   ├── src/
│   │   ├── views/            # DashboardScreen 态势大屏 / SearchWorkbench 检索工作台
│   │   ├── components/       # 大屏面板与翻牌器 (screen/)、水印、档案抽屉、审计抽屉组件
│   │   └── App.vue           # 视图切换外壳 (大屏 ⇄ 检索工作台)
│   └── dist/                 # 预编译好的纯本地离线静态资源包 (已提交入库，改动前端后需重新构建并提交)
├── data/                     # 数据专属目录 (.gitignore 严格隔离)
│   ├── csv_sources/          # 存放用户的 20+ 个原始 CSV 文件
│   └── personnel.duckdb      # 本地 DuckDB 物理数据库单文件
├── logs/                     # 涉密安全操作审计日志目录
├── tests/                    # 全链路自动化测试用例
├── start_mac.sh              # Mac/Linux 一键启动脚本
└── start_windows.bat         # Windows 一键启动脚本
```

---

## 🚀 快速启动指南

### 方式一：Windows 电脑一键安装启动 (目标机可联网，无需访问 GitHub)

1. **拿到安装包**：在能访问 GitHub 的电脑上下载本仓库 ZIP（或用 `git archive` 打包），通过 U 盘 / 内部网盘拷到目标机并解压。目标机不需要安装 Git、Node.js。
2. **放入数据**：把 20 多个原始 CSV 文件复制到 `data\csv_sources\` 目录（没有则新建）。
3. **双击 `start_windows.bat`**，首次运行会自动完成：
   - 未安装 Python 时，自动安装 Python 3.11 到当前用户目录（无需管理员权限，依次尝试 winget、国内镜像、官方源）；
   - 通过阿里云 / 清华镜像安装 DuckDB、FastAPI 等依赖；
   - **从 CSV 自动创建数据库** `data\personnel.duckdb` 并建立索引（嵌入式数据库，无需安装任何数据库软件；1600 万条约需 3~5 分钟）；
   - 配置本地访问域名：在本机 hosts 中加入 `127.0.0.1 dashboard.internal`（**首次会弹出一次管理员授权，请点“是”**），并将该域名加入系统代理的例外列表；
   - 启动服务，就绪后自动在浏览器打开大屏 👉 `http://dashboard.internal:8000`

之后每次使用直接双击 `start_windows.bat` 即可；关闭命令行窗口即停止服务。

- **域名与端口**：在 `start_windows.bat` 顶部的 `APP_DOMAIN`、`APP_PORT` 修改。域名只映射到本机 `127.0.0.1`，其他电脑无法访问。若拒绝了管理员授权或被安全软件拦截，会自动改用 `http://127.0.0.1:8000`。
- **没有 CSV 时**：脚本会提示放入 CSV；也可选择生成 20 万条演示数据（单独存放在 `data\demo_csv\`，不会混入真实数据）。
- **更换 / 追加数据**：把 CSV 放入 `data\csv_sources\` 后，先关闭大屏窗口，再双击 `import_csv.bat`，按提示确认后会按目录中的全部 CSV 重建数据库。

### 方式二：Mac / Linux 一键启动
```bash
./start_mac.sh
```

---

### 方式二：手动运行步骤

#### 1. 初始化后端环境
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows 下使用: .venv\Scripts\activate
pip install -r backend/requirements.txt
```

#### 2. 导入您的 20 多个真实 CSV 文件
将您的 20 多个 CSV 文件复制到 `data/csv_sources/` 目录下，然后执行导入：
```bash
python backend/scripts/import_csv.py
```
> 若当前处于开发阶段暂无真实文件，可运行生成测试数据：
> `python backend/scripts/generate_mock.py --total 200000 --num-files 20`

#### 3. 编译前端静态文件 (若改动前端代码)
仓库已附带编译好的 `frontend/dist`，只有修改了 `frontend/src` 才需要重新构建，并把新的 `dist` 一并提交：
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 4. 启动服务
```bash
python backend/main.py
```
访问浏览器 `http://127.0.0.1:8000` 即可使用。

---

## 🧪 自动化测试验证

运行内置全链路自动化测试套件（测试客户端需额外安装 `httpx`）：
```bash
.venv/bin/pip install httpx
.venv/bin/python tests/test_system.py
```
测试项包括：
- [x] 静态页面单机离线挂载
- [x] 1600w 级秒级大屏图表聚合接口
- [x] 多条件复合检索与毫秒响应
- [x] 人员全景档案卡片调阅
- [x] 涉密安全审计操作轨迹上报与留痕
- [x] 动态数据打码脱敏模式

---

## 🔒 纯断网物理隔离单机部署指南 (完全无法联网)

针对目标电脑**完全无法连接外网**的严苛涉密机房环境，系统提供了全链路纯离线交付方案：

### 第一步：在有网电脑上生成离线分发包
在有网络连接的电脑上拉取工程，按**目标机的操作系统**选择打包工具：

- **目标机是 Windows**（最常见，打包机可以是 Mac/Linux/Windows）：
  ```bash
  python3 backend/scripts/package_windows.py --output personnel_dashboard_windows_v1.0.zip --py-version 311
  ```
  `--py-version` 必须与目标机安装的 Python 版本一致（如 3.11 填 `311`，3.12 填 `312`）。
- **目标机与打包机为同一操作系统和 Python 版本**：
  ```bash
  python3 backend/scripts/package_offline.py --output personnel_dashboard_offline_v1.0.zip
  ```
  注意 `package_offline.py` 只下载**打包机本机平台**的依赖，在 Mac 上打的包无法装到 Windows 断网机上。
> 若希望将已导入好的 1600 万数据库直接带入目标机，可追加 `--include-db` 参数：
> `python3 backend/scripts/package_offline.py --output personnel_dashboard_offline_v1.0.zip --include-db`

打包脚本会自动：
1. 预先构建前端静态文件至 `frontend/dist`（**断网机无需安装 Node.js/npm**）。
2. 将后端所需的全部 Python 依赖以二进制 Wheel 下载至 `offline_wheels/`。
3. 封装为单一压缩包 `personnel_dashboard_offline_v1.0.zip`（仅约 20MB）。

### 第二步：介质拷贝与安全摆渡
通过涉密合规光盘刻录或专用安全摆渡 U 盘，将 `personnel_dashboard_offline_v1.0.zip` 拷贝至目标断网机并解压。

### 第三步：断网机一键初始化与启动
目标机只需预先安装 Python 3.10+，解压后直接执行：

- **Windows 断网机**：
  1. 双击运行 `install_offline.bat`（自动利用本地 `offline_wheels/` 零网络安装依赖）。
  2. 双击运行 `start_windows.bat`（配置本地域名、启动服务并自动打开 `http://dashboard.internal:8000`）。
- **Mac / Linux 断网机**：
  1. 运行 `./install_offline.sh`。
  2. 运行 `./start_mac.sh`。

### 第四步：数据就绪
- 若打包时使用了 `--include-db`，解压即自带 1600 万数据，**开箱即用、秒级查询**。
- 若现场导入真实数据，只需将 20+ 个 CSV 复制到 `data/csv_sources/` 目录，执行 `.venv/bin/python backend/scripts/import_csv.py` 即可现场建库。
