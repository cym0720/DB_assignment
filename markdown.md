# 事务划分
  sql 连接后有自动创建事务的功能，不用手动添加start_transaction语句，通过commit区分事务并提交事务。

# 数据问题
fastapi默认接受json数据，但是我写的html发出的是表单数据