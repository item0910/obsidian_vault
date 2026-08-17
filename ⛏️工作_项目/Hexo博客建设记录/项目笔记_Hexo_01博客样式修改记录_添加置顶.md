---
title: 项目笔记_Hexo博客修改记录
date: 2024-08-11
categories: hexo博客建设
tags: 项目笔记/日常态项目/Hexo
author: 自己
mtime: 2024-09-25
---

### 添加置顶标签

#### 操作

1.打开博客目录，打开博客目录下的“node_modules\hexo-generator-index\lib”目录，其中的“generator.js”文件就是我们所要修改的文件。

实现该功能需要在 const posts = locals.posts.sort(config.index_generator.order_by);
代码下添加一下内容：

```js
  posts.data = posts.data.sort(function(a, b) {
    if(a.top && b.top) { // 两篇文章都有top，top大的在前
        if(a.top == b.top)
			return b.date - a.date; // 若top值一样，最新的文章在前面
        else
			return b.top - a.top; // top大的在前面
    }
    else if(a.top && !b.top) { // 以下是只有一篇文章top有定义，那么将有top的排在前面
        return -1;
    }
    else if(!a.top && b.top) {
        return 1;
    }
    else return b.date - a.date; 	//都没有top标签，最新的文章在前面
});
```

#### 使用

使用时只需要在文章中加入 top 属性即可，top 越大文章越靠前。

### 给首页文章加图片

在 head.ejs 最后加

```js
  <script>
	  document.addEventListener("DOMContentLoaded", function() {
		if (window.location.pathname === "/" || window.location.pathname === "/index.html") {
		  var images = document.querySelectorAll(".specialImage");
		  images.forEach(function(image) {
			image.style.display = "block";
		  });
		}
	  });
  </script>
```

- 需要在首页展示的图片格式: `<img class="specialImage" src="https://s2.loli.net/2024/09/01/lQmp6HwntdZxAW7.jpg" style="width:100px; display:none; margin:0;">`

### 加 sider 的背景

`E:\hexo\themes\yilia\layout\_partial` 下的 head.ejs
在

```ejs
<% var defaultCtnBg = 'linear-gradient(200deg,#a0cfe4,#e8c37e)' %>
```

后面这句添加

```
container.show {
      background: <%= theme.style && theme.style.slider ? theme.style.slider : defaultCtnBg %>;
      <!--background-image: url('');-->
```

url 里面是下面的图片的 data64 编码

![|300](附件/image/项目笔记_Hexo博客修改记录_添加置顶-1725191914943.jpeg)

### 添加图片, 修改大小和描述

```html
<figure>
	<img src="https://s2.loli.net/2024/09/01/lQmp6HwntdZxAW7.jpg" style="width:300px;">
	<figcaption style="text-align: center;">
	这是图片的描述
	</figcaption> 
</figure>
```

- 以上是需要图片描述的情况, 没有特殊情况可以直接用原 `![]()` 方式
- 如果需要改大小 (非 300px), 也需要用 `<img>` 的方式
- 效果如下:
<figure>
<img src="https://s2.loli.net/2024/09/01/lQmp6HwntdZxAW7.jpg" style="width:300px;"><figcaption style="text-align: center;">这是图片的描述</figcaption> </figure>

### 隐藏元素

#### 问题描述

评论区的下面有一个 powered by valine 的 div, 因为太多链接, 显得很繁杂, 于是想把他去除

#### 解决方式

在 `E:\hexo\themes\yilia\source` 的 main.css 最上面添加了一个根据 class 来不显示元素的 style, 完成目标

```js
/*隐藏元素*/
.vpower {
  display: none !important;
}
```

#### 隐藏的元素

1. 评论区的网址链接

### 增加友圈的分享 ico

- 压缩图片尽可能小 ( 10% )
- 在文章前面添上一行 `<link rel="Shortcut Icon" href="https://s2.loli.net/2024/08/26/6VKvJQDEmdiI5YS.jpg" type="image/x-icon" />`
	- 这样既不会在网页显示图片, 也容易被第一张读到

### 站内链接格式

`<a href="{% post_path 杂谈/2024-8-31推荐大伙多看电视 %}" target="_self">推荐大伙多看电视</a>`

### 网页分享研究

1. 微信需要企业认证, 然后需要接口啥的, 300 元认证一年
2. ![ | 100](附件/image/项目笔记_Hexo博客修改记录_添加置顶-1725409167909.jpeg ) 二维码也挺好

### ~~添加一个看不见的 icon~~

基本解决了分享文章封面的问题, 已经弃用

```html
<link rel="Shortcut Icon" href="https://s2.loli.net/2024/08/26/6VKvJQDEmdiI5YS.jpg" type="image/x-icon" />
```

### 添加背景图片

- 比例为 1275 * 425 大约为 3:1
- 所以先压缩图片之后, 取合适的一截, 当然在选的时候就要以这个长幅比例作为参考
