# 学城私有数据智能检索与涉密大屏系统

> 专为政府工作人员打造的 **1600万级** 大数据离线检索、态势感知大屏与单机涉密管理系统。

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
│   │   ├── components/       # 大屏图表、水印、档案抽屉、审计抽屉组件
│   │   └── App.vue           # 指挥大屏与检索工作台主视图
│   └── dist/                 # 预编译好的纯本地离线静态资源包
├── data/                     # 数据专属目录 (.gitignore 严格隔离)
│   ├── csv_sources/          # 存放用户的 20+ 个原始 CSV 文件
│   └── xuecheng.duckdb       # 本地 DuckDB 物理数据库单文件
├── logs/                     # 涉密安全操作审计日志目录
├── tests/                    # 全链路自动化测试用例
├── start_mac.sh              # Mac/Linux 一键启动脚本
└── start_windows.bat         # Windows 一键启动脚本
```

---

## 🚀 快速启动指南

### 方式一：一键脚本启动 (推荐)

- **Mac / Linux**：
  ```bash
  ./start_mac.sh
  ```
- **Windows**：
  直接双击运行 `start_windows.bat`。

启动脚本会自动检测环境、准备数据库并在系统浏览器中自动打开：
👉 `http://127.0.0.1:8000`

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

运行内置全链路自动化测试套件：
```bash
.venv/bin/python tests/test_system.py
```
测试项包括：
- [x] 静态页面单机离线挂载
- [x] 1600w 级秒级大屏图表聚合接口
- [x] 多条件复合检索与毫秒响应
- [x] 人员全景档案卡片调阅
- [x] 涉密安全审计操作轨迹上报与留痕
- [x] 动态数据打码脱敏模式
