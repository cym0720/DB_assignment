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