# MemorialHall

这是一个纯静态的纪念堂/英灵殿页面项目。项目没有构建步骤，也没有前端框架；页面、样式和脚本都写在 HTML 文件内，主要内容由同目录下的 `data.json` 驱动。

## 快速运行

推荐用本地静态服务器打开，避免 `fetch('./data.json')` 在直接双击 HTML 时受到浏览器本地文件策略影响。

```powershell
python -m http.server 8000
```

然后访问：

- 前台页面：`http://localhost:8000/index.html`
- 管理后台：`http://localhost:8000/admin.html`

## 项目结构

```text
.
├── index.html                  # 前台展示页：读取 data.json 并动态渲染首页、人物纪念堂、文章和计时器
├── admin.html                  # 管理后台：读取/编辑人物数据，并可通过 GitHub API 更新 data.json
├── data.json                   # 站点核心数据源
├── images/                     # 人物图片资源
│   ├── im.jpg
│   ├── ml.jpg
│   ├── golf.jpg
│   ├── eggplant.jpg
│   └── chendie.png
└── .github/workflows/deploy.yml # GitHub Pages 部署 workflow，推送 main 后部署整个仓库
```

## Agent 维护要点

- 这是无依赖静态项目：不要引入构建工具、包管理器或框架，除非用户明确要求。
- `index.html` 和 `admin.html` 内联了 CSS 与 JavaScript；小改动优先在对应 HTML 内完成。
- `data.json` 是最重要的内容入口。新增/修改人物、横幅、文章时通常只需要改 `data.json`。
- 文件内容是 UTF-8。读取中文时请显式使用 UTF-8，PowerShell 示例：`Get-Content -Encoding UTF8 data.json`。
- 修改 `data.json` 后应验证 JSON 合法性，例如：

```powershell
Get-Content -Raw -Encoding UTF8 data.json | ConvertFrom-Json | Out-Null
```

- 前台通过 `fetch('./data.json?t=' + Date.now())` 加载数据，因此 `data.json` 必须与 `index.html` 保持同级。
- 图片路径写在数据字段 `imagePath` 中，通常是 `images/xxx.jpg` 或 `images/xxx.png`。新增图片时同步检查路径大小写和扩展名。
- 当前目录不一定是 Git 仓库；执行 Git 操作前先确认 `.git` 是否存在。

## 数据结构说明

`data.json` 顶层结构：

```json
{
  "siteTitle": "素草英灵殿",
  "footer": "页脚文字",
  "characters": []
}
```

`characters` 中每个人物对象的主要字段：

| 字段 | 用途 |
| --- | --- |
| `id` | 唯一标识，用于生成视图 ID 和计时器 ID。建议使用英文、数字、下划线或短横线。 |
| `name` | 首页相框下方显示的人物名。 |
| `status` | 状态类型。现有样式支持 `honor`、`purged`，其他值会按普通状态显示。 |
| `statusText` | 首页人物状态文案。 |
| `imagePath` | 人物图片路径。 |
| `deathDate` | 计时器起始日期，格式为 `YYYY-MM-DD`。 |
| `deathDateLabel` | 计时器标题中的事件描述。 |
| `bgColorFrom` | 纪念堂主背景起始色。 |
| `borderColor` | 边框、文章标题、强调线等主题色。 |
| `coupletLeft` / `coupletRight` | 水晶棺两侧挽联文字。 |
| `hallTitle` / `hallSubtitle` | 人物纪念堂标题与副标题。 |
| `hasStamp` / `stampText` | 是否在首页图片上显示印章，以及印章文字。 |
| `funeralCommittee` | 侧栏“治丧委员会”内容，支持 HTML。 |
| `banners` | 纪念堂横幅列表，点击后加载指定文章。 |
| `sidebarNav` | 右侧文章导航列表。 |
| `articles` | 文章内容列表，正文支持 HTML。 |

横幅对象：

```json
{
  "text": "横幅文字",
  "style": "im-style",
  "articleKey": "editorial"
}
```

`style` 现有可用值：

- `im-style`：蓝色横幅
- `denied`：灰色划线横幅
- `critical`：红色警告横幅
- `""`：默认样式

导航对象：

```json
{
  "tag": "社论",
  "label": "沉痛悼念Im同志",
  "articleKey": "editorial",
  "style": ""
}
```

文章对象：

```json
{
  "key": "editorial",
  "title": "文章标题",
  "meta": "来源/日期",
  "body": "<p>正文内容。</p>"
}
```

注意：`banners[].articleKey` 和 `sidebarNav[].articleKey` 必须能在同一人物的 `articles[].key` 中找到，否则点击后不会显示文章。

## 管理后台说明

`admin.html` 会从本地 `data.json` 加载 `characters`，支持：

- 新增、删除、编辑人物
- 编辑人物状态、图片路径、日期、主题色、挽联
- 编辑横幅、侧边导航和文章
- 通过 GitHub API 将新的 `data.json` 推送到仓库

后台的 GitHub 配置保存在浏览器 `localStorage` 中，包括用户名、仓库名、分支和 token。不要把 token 写入仓库或 README。

发布逻辑只会更新仓库根目录的 `data.json`。它不会上传图片；如果新增图片，需要手动把图片文件放进 `images/` 并提交。

## 部署说明

`.github/workflows/deploy.yml` 使用 GitHub Pages 官方 action：

- 触发条件：推送到 `main` 分支，或手动 `workflow_dispatch`
- 部署内容：仓库根目录全部文件
- 入口页面：`index.html`

如果页面部署后没有更新，优先检查：

- GitHub Pages 是否启用并使用 GitHub Actions 部署
- workflow 是否成功运行
- `data.json` 是否是合法 JSON
- 新增图片是否已经提交到 `images/`

## 常见修改流程

1. 修改 `data.json` 中对应人物或文章。
2. 校验 JSON 格式。
3. 用本地静态服务器打开 `index.html` 检查页面效果。
4. 如果新增图片，确认 `images/` 中有对应文件且 `imagePath` 正确。
5. 提交并推送到 `main`，等待 GitHub Pages 自动部署。
