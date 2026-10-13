# 麦田烘焙 · Maitian Bakehouse

> 烘焙工作室展示网页（零构建静态 Demo）：温馨文艺取向的落地页，展示招牌产品、品牌故事、顾客好评与门店信息。

## 一、定位

`apps/samples/` 下的示例/原型类应用。纯 HTML/CSS/JS，无构建、无依赖、无后端，直接打开 `index.html` 即可预览，适合作为「手作/餐饮/生活方式」类品牌落地页的视觉与结构参考。

## 二、目录结构

```
apps/samples/maitian-bakehouse/
├── index.html    -- 页面结构（语义化分区：#menu / #about / #reviews / #contact）
├── styles.css    -- 全部样式（CSS 变量主题 + 响应式）
├── script.js     -- 交互（移动端导航、滚动渐显、轻量视差）
└── README.md     -- 本文件
```

## 三、页面内容

1. 首屏大图：工作室名称「麦田烘焙」、口号「用心烘焙，温暖每一天」、「查看菜单」按钮与数据条。
2. 招牌产品：6 款人气产品卡片（图片占位 + 名称 + 价格 + 描述），含「人气 No.1 / 晨间限定 / 秋冬限定」等标签。
3. 关于我们：品牌故事 + 主理人理念引言 + 店内环境插画占位。
4. 顾客好评：3 条评价，含头像与星级评分。
5. 联系与地址：营业时间 / 地址 / 电话 + 地图占位（含定位气泡）。

## 四、设计要点

- 主色为奶油色与棕色（CSS 变量统一定义于 `styles.css` 顶部 `:root`），圆角卡片、温暖纸感。
- 标题使用手写体 `Ma Shan Zheng`，正文使用 `LXGW WenKai`（Google Fonts / jsDelivr CDN，含回退字体栈）。
- 插画（首屏场景、店内环境）全部由内联 SVG 绘制，不依赖任何外部图片。
- 交互：`IntersectionObserver` 滚动渐显、卡片悬停上浮、首屏轻量视差；遵循 `prefers-reduced-motion`。
- 响应式：桌面双栏 / 移动端单栏，移动端启用汉堡导航。

## 五、预览

```bash
# 任选一种静态服务器，在仓库根目录执行
python -m http.server 4173
# 浏览器打开 http://127.0.0.1:4173/apps/samples/maitian-bakehouse/index.html
```

也可直接用浏览器打开 `index.html`（字体与样式均为相对/CDN 引用，联网时手写体字体最佳）。

## 六、素材说明

所有「图片」均为设计占位（渐变 + 内联 SVG 插画），非真实实拍。替换为真实照片时，将 `.card-media`、`.photo-frame .inner`、`.about-photo` 内的 SVG 替换为 `<img>` 即可，布局与圆角保持不变。

## 七、来源

由 LobsterAI 助手为「麦田烘焙」需求生成，品牌名、创始人、地址电话等为示例内容，可按实际替换。
