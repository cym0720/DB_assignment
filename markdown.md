# 事务划分
  sql 连接后有自动创建事务的功能，不用手动添加start_transaction语句，通过commit区分事务并提交事务。

# 数据问题
fastapi默认接受json数据，但是我写的html发出的是表单数据

# post与get
  GET 是「查数据」（只读、无副作用），POST 是「提交 / 改数据」（写数据、有副作用）。
GET 示例（你的 /users/{username} 接口）：
请求 URL 是 http://127.0.0.1:8000/users/lty，用户名 lty 直接拼在地址栏里，肉眼可见；
POST 示例（你的 /users/login 接口）：
请求 URL 还是 http://127.0.0.1:8000/users/login，但用户名 / 密码藏在「请求体」里（你前端代码里的 body: JSON.stringify({username, password})），地址栏看不到。


# div是做分区
主要要用css控制样式，不要用div来做布局，div的作用是用来分区的，不要用来做布局，然后js读分区的id或其他东西来控制样式的切换。

### 1. 前端由数据驱动界面
- 页面展示状态（是否显示预约表格、提示信息）由后端返回的数据决定
- 使用 JavaScript 控制 DOM 的 `display` 属性实现状态切换

```js
element.style.display = 'none';
element.style.display = 'block'; // 或 table
```

### 2. DOM 元素职责划分
- `table`：控制表格整体是否显示
- `tbody`：负责渲染和清空数据行
- 不推荐单独控制 `tbody` 的显示状态

---

## 二、HTML 结构与 div 的使用原则

- `div` 是无语义容器，用于结构分区、样式控制和 JS 操作
- 如果元素本身具有完整语义（如 `table`），不需要额外嵌套 `div`
- HTML 结构应尽量简洁，避免无意义嵌套

---

## 三、class 的职责划分

一个元素可以拥有多个 class，但每个 class 只承担一种职责：

```html
<button class="btn btn-delete js-delete">取消预约</button>
```

| class 名称 | 职责 |
|-----------|------|
| btn | 通用按钮样式 |
| btn-delete | 删除按钮的外观样式 |
| js-delete | JavaScript 行为标识 |

优点：
- 样式与逻辑解耦
- 便于维护和扩展

---

## 四、事件绑定方式选择

### 1. 固定按钮
- 页面加载时已存在
- 使用 `getElementById + addEventListener`

```js
btn.addEventListener('click', handler);
```

### 2. 动态生成按钮（推荐事件委托）
- 表格中循环生成的按钮
- 使用父元素统一监听事件

```js
tableBody.addEventListener('click', (e) => {
  const btn = e.target.closest('.js-delete');
  if (!btn) return;
});
```

---

## 五、使用 data-* 属性传递行数据

- 将当前行数据绑定到按钮上
- 避免依赖唯一 id

```html
<button
  class="js-delete"
  data-court-id="2"
  data-reserve-date="2025-12-19"
  data-reserve-time-str="08:00:00"
>
```

```js
btn.dataset.courtId;
btn.dataset.reserveDate;
btn.dataset.reserveTimeStr;
```

---

## 六、时间数据处理与一致性

- 前端展示时间与后端存储格式可能不同
- 前后端必须约定统一格式

```js
function int2time(sec) {
  ...
  return "08:00:00";
}
```

- 删除预约时，时间字符串必须与数据库中的 TIME 字段完全一致

---

## 七、HTML 属性拼接常见错误

错误示例（引号未闭合）：
```html
data-reserve-time-str="${reserve_time_str}
```

正确示例：
```html
data-reserve-time-str="${reserve_time_str}"
```

---

## 八、Fetch 接口返回处理注意事项

- 后端可能返回 `204 No Content`
- 不能盲目调用 `response.json()`

```js
if (response.ok) {
  // 成功处理
} else {
  const result = await response.json();
}
```

---

## 九、页面跳转实现

```html
<button onclick="location.href='user.html'">返回用户中心</button>
```

- 若在 `form` 中使用按钮，需加 `type="button"`

---
