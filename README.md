# 素槽群史 · 素槽英灵殿

静态的“纪、传、表、志”综合网站。首页为群史目录，可切换纵向时间线；人物头像进入原有深色英灵殿，默认阅读人物列传。无业务服务器、注册系统或数据库，部署到 GitHub Pages，日常编纂通过 admin.html 完成。

## 本地运行

需要 Node.js 22 或更新版本；普通阅读不需要 Node.js。使用 HTTP 服务，不能直接双击 HTML（模块与数据读取受浏览器 file 协议限制）。

```sh
python -m http.server 8000 --bind 127.0.0.1
```

打开 http://127.0.0.1:8000/ 阅读，打开 http://127.0.0.1:8000/admin.html 编纂。固定使用同一地址和端口，本地草稿按浏览器来源隔离。

```sh
npm test           # 当前内容校验、迁移回归、原子发布与冲突测试
npm run build      # 校验后将公开站点写入 dist/
npm run test:browser
```

浏览器测试默认使用本机 Codex 的 Playwright 和 Edge，可用 PLAYWRIGHT_PATH 指定已安装的 playwright 包、BROWSER_CHANNEL 指定浏览器（默认 msedge）。测试只操作独立浏览器上下文中的本地工作区，不会调用真实 GitHub 发布。截图位于 tmp/qa/。测试需要完整 Git 历史中的 60e40f6，以核对旧站原文。

## 页面与数据

| 文件 | 用途 |
| --- | --- |
| index.html / assets/app.js / assets/site.css | 目录、时间线、纪事、英灵殿、表、志、搜索 |
| admin.html / assets/admin.js / assets/admin.css | 六个编纂工作区及发布界面 |
| assets/core.js | 前后台共用的排序、卷号、时间、搜索、清洗和校验 |
| assets/store.js | IndexedDB 草稿、预览快照与图片保存 |
| assets/publish.js | GitHub 基线检查、Git 对象原子提交、部署状态 |
| data.json | schemaVersion: 2 的统一内容 |
| images/ | 头像与正文插图 |
| sources/history.pdf | 随站保留的完整 18 页原稿 |
| assets/vendor/ | Quill 2.0.3、DOMPurify 3.2.7 及许可证，无 CDN |
| scripts/ | 一次性迁移记录及静态打包 |
| tests/fixtures/migration-v2.json | 初次迁移的回归基准；不是线上编辑数据 |

哈希链接可以直接分享、刷新、前进和后退：

- #/chronicle 和 #/chronicle?view=timeline
- #/chronicle/generation/:id、volume/:id、period/:id、event/:id
- #/people、#/person/:id、#/person/:id/article/:key
- #/tables/main、night、shantou、admins；支持 group、record、person 等筛选参数
- #/gazetteers、#/gazetteers/:id?chapter=:chapterId
- #/search?q=关键词、#/about

ID 是稳定链接身份，标题和名字可以改。卷号按领导集体顺序与代内卷顺序统一生成；上移、下移或拖拽调整代内卷序，改所属领导集体可以跨代移动，界面显示全书重编号预览。

数据模块为 generations、volumes、periods、events、characters、groups、groupStages、tenures、treatises、media、sources。时期最多两层。群聊实体和历史阶段分开；任期按一次任职一条记录，支持兼任、再任和跨代连续任期。人物与领导集体的成员关联在后台双向同步。

时间对象使用 label（保留原始文案）、start/end、precision、dates（不连续日期）和 ongoing。未知不填写精确日期；只有确知仍持续才勾选至今。deathDate 只用于旧英灵殿计时，不推导新群史日期。

## 编纂与本地恢复

1. 进入纪、传、表、志或设置，选中条目编辑。正文使用可视化编辑器，可插入人物、事件、群聊、志链接和图库图片。
2. 内容完成度与发布状态分开：完整／未完／待补是写作进度；草稿／已发布控制公开导出。已发布且待补可以进入目录。
3. 自动保存约延迟 650ms；显示“本地已保存”后才表示已写入 IndexedDB。页面跳转前也会保存，未保存时关闭页面会提示。刷新会恢复同一浏览器的工作区。
4. “整站预览”使用同一套前台渲染器，支持桌面和手机。预览显示将公开的条目，含待补正文；草稿不会出现在公开预览中。预览链接限当前浏览器工作区使用，24 小时后过期。
5. 图片可上传 JPG/PNG/WebP/GIF，单张最多 12MB。生成唯一文件名，保存在本地；编辑器和预览立即可见，正文保存稳定图片路径。
6. 定期导出工作区备份。备份包含本地文字、草稿和未发布图片，不包含 Token。导入前会保存恢复快照。清除浏览器数据会删除未备份的工作区。
7. 删除前会检查下级、关联、站内正文链接、头像和图片引用。先移动下级或解除引用，再删除条目。

人物列传是普通文选的一篇，由 defaultArticleKey 显式指定。旧文可切换、编辑或归档；初始迁移把空白占位文章归档，仍在后台与数据中保留。正文展示经过 DOMPurify 清洗。原稿红字在迁移与可视化编辑后保留颜色。

## GitHub 发布

首次上线必须用 Git 一次性提交网站代码、v2 数据、图片、依赖、原稿和工作流。旧站 data.json 仍为 v1 时，新版后台会拒绝将其当作 v2 编辑基线。日常后台发布只更新 data.json 和新图片，不更新代码。

推荐先提交到 codex/ 开头的测试分支，工作流执行测试和构建，并保存 soyo-static-site 下载工件；测试分支和 PR 不覆盖正式 Pages。确认后合入 main，才执行正式部署。仓库 Pages 设置选择 GitHub Actions。

后台填写 GitHub 用户／组织、仓库、分支和访问令牌。细粒度令牌需要目标仓库 Contents 读写权限，查询 Actions 部署状态需要 Actions 读取权限。Token 默认只放当前标签页会话，不写入数据、备份或仓库。

发布顺序：

1. 连接远端，读取分支 SHA 作为基线。远端数据变化时显示差异，保留本地草稿；可先导出再载入远端。
2. 预览、检查变更摘要和校验结果。重复 ID、断链、循环、非法日期、无效默认文章和缺图阻止发布。待补、原稿异说与时期重叠只提示。
3. 创建图片 blob、内容 blob、tree、commit，以 force: false 更新分支。所有图片与正文归于同一提交。
4. 若远端基线已变化，停止发布；若在最后更新时产生并发竞争，非强制更新失败，本地草稿和图片保持可重试。
5. “已提交到 GitHub”之后仍须检查部署。测试分支不会更新正式网站；main 的 Pages 工作流成功才表示网站已部署。

草稿只在工作区内。公开条目若链接了草稿，会在公开导出校验中显示失效关联；应一并发布被引用条目，或移除公开引用。

CI 只上传 dist/ 中的 index.html、admin.html、assets/、images/、sources/、公开 data.json 和 .nojekyll。迁移脚本、测试、临时截图和本地工作区备份不进入 Pages。回归测试使用固定迁移快照，正常增删公开条目不会因为初始人数或篇数改变而导致部署失败。

## 初次迁移与史料边界

已建立三代、五卷、六个时期（含子时期）、16 篇纪事、52 份人物档案、21 条群聊阶段、56 条任期和六个专题。原有 42 人物、50 篇文章的身份、文章 key 和正文可逐项追溯；新增十个人物档案。原稿涵盖的十篇列传已迁入，其余保留待补。第二、三代概述、第二代原始名单、全部已有专题、红字和原题均保留。

migration.sections 记录 52 个手工核定分段、页码、原题和 758 行映射；封面另存，原 PDF 原样随站。初始网页按纪传表志重排；每项附来源和页码。后续编辑不会自动重跑迁移。

- PDF 自身日期冲突保留校勘，例如绩溪卸任日 10 月 12 日／13 日。
- 沐鄉让恋与沐卿让恋、新溪与绩溪不自动合并。
- im 新群史日期采用 PDF；旧纪念计时不变。
- 两个旧头像文件缺失，改用姓名占位，原路径记入 legacyImagePath；不猜测身份匹配头像。
- 第二、三代未写卷章、空指导危机、猫槽及邦系与槽系等不补造正文。
- 原凡例仍作为史料展示，同时注明“网站版本经作者确认全文公开”。

迁移脚本用于审计，不是日常更新入口。migrate_history.py 会拒绝覆盖 v2；refine_migration.py 是一次性修订记录，不应在已编纂数据上重复执行。
