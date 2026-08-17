---
title: 项目笔记_Hexo_03字体
date: 2024-10-02
categories: 
tags: 
author: 
mtime: 2024-11-11
---

- 链接:[免费商用字体和 WebFonts 字体 CDN - ZeoSeven Fonts](https://fonts.zeoseven.com/)

```js
/*异步加载字体在main.js中*/
function loadCustomFont() {
    if (/Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent)) return;

    function loadFont(url, fallback) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onerror = function () {
            if (typeof fallback === 'function') fallback();
        };
        document.head.appendChild(link);
        document.documentElement.style.fontFamily = 'Source Han Sans HW SC VF';
        document.documentElement.style.fontWeight = 'normal';
    }

    loadFont('https://static.zeoseven.com/zsft/286/main/result.css', function () {
        loadFont('https://static-host.zeoseven.com/zsft/286/main/result.css');
    });
}
```

```
function loadCustomFont() {
    if (/Mobi|Android|iPhone|iPad|iPod|Windows Phone/i.test(navigator.userAgent)) return;

    function loadFont(url, fallback) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onerror = function () {
            if (typeof fallback === 'function') fallback();
        };
        document.head.appendChild(link);
        document.documentElement.style.fontFamily = 'Judou Sans UI Hans';
        document.documentElement.style.fontWeight = 'normal';
    }

    loadFont('https://static.zeoseven.com/zsft/135/main/result.css', function () {
        loadFont('https://static-host.zeoseven.com/zsft/135/main/result.css');
    });
}
```



- Source Han Sans HW 思源黑体 SC

```css
@import url('https://static.zeoseven.com/zsft/286/main/result.css');

html {
    font-family: "Source Han Sans HW SC VF";
    font-weight: normal;
}
```

- 霞鹜臻楷

```css
@import url('https://static.zeoseven.com/zsft/2/main/result.css');

html {
    font-family: "Zhuque Fangsong (technical preview)";
    font-weight: normal;
}
```

- 秋水書体

```css
@import url('https://static.zeoseven.com/zsft/245/main/result.css');

html {
    font-family: "QiushuiShotai Bright";
    font-weight: normal;
}
```

- 更纱黑体

```css
@import url('https://static.zeoseven.com/zsft/203/main/result.css');

html {
    font-family: "Sarasa Gothic HC";
    font-weight: normal;
}
```

- 霞鹜文楷

```css
@import url('https://static.zeoseven.com/zsft/293/main/result.css');

html {
    font-family: "LXGW WenKai Mono";
    font-weight: normal;
}
```

- 秋空󠄁黑体

```css
@import url('https://static.zeoseven.com/zsft/277/main/result.css');

html {
    font-family: "ChiuKong Gothic MN";
    font-weight: normal;
}
```

- 屏显臻宋

```css
@import url('https://static.zeoseven.com/zsft/79/main/result.css');

html {
    font-family: "Clear Han Serif";
    font-weight: normal;
}
```

- 更纱黑体

```css
@import url('https://static.zeoseven.com/zsft/205/main/result.css');

html {
    font-family: "Sarasa Gothic K";
    font-weight: normal;
}
```

- 更纱黑体 Mono SC

```css
@import url('https://static.zeoseven.com/zsft/159/main/result.css');

html {
    font-family: "Sarasa Mono SC";
    font-weight: normal;
}
```

- 思源宋体

```css
@import url('https://static.zeoseven.com/zsft/285/main/result.css');

html {
    font-family: "Noto Serif SC";
    font-weight: normal;
}
```


- ChiuKong Gothic 秋空󠄁黑體 秋空󠄁黑体 CL

```css
@import url('https://static.zeoseven.com/zsft/278/main/result.css');

html {
    font-family: "ChiuKong Gothic CL";
    font-weight: normal;
}
```

- YshiPen ShutiCL Y 式笔书 CL 特别版

```css
@import url('https://static.zeoseven.com/zsft/233/main/result.css');

html {
    font-family: "YShiPen-ShutiCL S";
    font-weight: normal;
}
```

- QiushuiShotai 秋水書体

```css
@import url('https://static.zeoseven.com/zsft/244/main/result.css');

html {
    font-family: "QiushuiShotai";
    font-weight: normal;
}
```

- LXGW WenKai 霞鹜文楷 Mono GB

```css
@import url('https://static.zeoseven.com/zsft/94/main/result.css');

html {
    font-family: "LXGW WenKai Mono GB";
    font-weight: normal;
}
```

- 未来圆 SC

```css
@import url('https://static.zeoseven.com/zsft/181/main/result.css');

html {
    font-family: "未来圆SC";
    font-weight: normal;
}
```

- LXGW WenKai 霞鹜文楷

```css
@import url('https://static.zeoseven.com/zsft/292/main/result.css');

html {
    font-family: "LXGW WenKai";
    font-weight: normal;
}
```

- YShiNewPen Shuti Yshi 新筆書

```css
@import url('https://static.zeoseven.com/zsft/231/main/result.css');

html {
    font-family: "YShiNewPen-Shuti";
    font-weight: normal;
}
```

- 全字库正楷体

```css
@import url('https://static.zeoseven.com/zsft/36/main/result.css');

html {
    font-family: "TW-Kai";
    font-weight: normal;
}
```
