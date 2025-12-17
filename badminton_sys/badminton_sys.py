import os
import mysql.connector
import hashlib

class User:
  def __init__(self, user_id, username, email, password):
    self.user_id  = user_id
    self.name = username
    self.email    = email
    self.password = password

class Account(User):
  def __init__(self, id, balance, hobby_project, level):
    self.id            = id
    self.balance       = balance
    if hobby_project not in Account.hobby_projects:
      raise(Exception(f"Invalid hobby_project: {hobby_project}"))
    self.hobby_project = hobby_project
    self.level         = level
  
  hobby_projects = ["单打", "双打", "混合双打", "休闲"]

class Court:
  def __init__(self, court_id, level, is_free):
    self.court_id = court_id
    self.level    = level
    self.is_free  = is_free
  
  levels = ["初级", "中级", "专业级"]

class CourtReservation:
  def __init__(self, court_id, subscriber, reserve_date, reserve_time):
    self.court_id     = court_id
    self.subscriber   = subscriber
    self.reserve_date = reserve_date
    self.reserve_time = reserve_time

class BadmintonSystem(Account, Court, CourtReservation) :
  def __init__(self):
    # Connect to the database
    self.db = mysql.connector.connect(
      host     = 'localhost',
      user     = 'badminton_user',
      password = '123456',
      database = 'badminton'
    ) 
    self.cursor = self.db.cursor(buffered=True)
  

  def close_db(self):
    self.cursor.close()
    self.db.close()
  
  #------------------------检查对象是否存在的函数------------------------------
  #TODO: 处理重名情况
  def check_user_exist(self, username):
    try:
      sql = "SELECT * FROM User WHERE name = %s"
      self.cursor.execute(sql, (username,))
      return self.cursor.fetchone() is not None
    except mysql.connector.Error as err:
      print("Something went wrong at check_user_exist: {}".format(err))
      return False

  def check_court_exist(self, court_id):
    try:
      sql = "select * from Courts where court_id = %s"
      self.cursor.execute(sql, court_id)
      return self.cursor.fetchone() is not None
    except mysql.connector.Error as err:
      print("Something went wrong at check_court_exist: {}".format(err))
      return False

  def check_court_reservation_exist(self, court_id, reserve_date, reserve_time):
    try:
      sql = "select * from CourtReservations where court_id = %s and reserve_date = %s and reserve_time = %s"
      self.cursor.execute(sql, (court_id, reserve_date, reserve_time))
      return self.cursor.fetchone() is not None
    except mysql.connector.Error as err:
      print("Something went wrong at check_court_reservation_exist: {}".format(err))
      return False
  
  def check_password(self, username, password):
    try:
      sql = "SELECT password FROM User WHERE name = %s"
      self.cursor.execute(sql, (username,))
      result = self.cursor.fetchone()
      if result is None:
        return False
      stored_password = result[0]
      return stored_password == self._encrypt_password(password)
    except mysql.connector.Error as err:
      print("Something went wrong at check_password: {}".format(err))
      return False

  #------------------------加密与解密使用的函数------------------------------------------------------
  def _encrypt_password(self, password):
    md5 = hashlib.md5()
    md5.update(password.encode('utf-8'))
    return md5.hexdigest()
  
  #------------------------增删改查账户与场地的函数，增加场地预定的函数放到后面-------------------------
  def create_account(self,user_id, balance, hobby_project, level) :
    try:
      # if self.check_user_exist(self.name) :
      #   raise(Exception(f"User aready exists: {self.name}"))
      
      sql_insert_account = "INSERT INTO Account (id, balance, hobby_project, level) VALUES (%s, %s, %s, %s)"
      self.cursor.execute(sql_insert_account, (user_id, balance, hobby_project, level))
      # self.db.commit()
      return True

    except Exception as e:
      print("创建账户失败：{}", e)
      return False
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at create_account: {format(err)}")
      self.db.rollback()
      return False

  def create_user(self, username, email, password) :
    try:
      if self.check_user_exist(username):
        raise(Exception(f"User already exists: {username}"))

      #创建事务
      # self.db.start_transaction()

      sql_select_user_id = "SELECT MAX(id) FROM User"
      self.cursor.execute(sql_select_user_id)
      result = self.cursor.fetchone()
      user_id = 1 if result[0] is None else result[0] + 1
      password = self._encrypt_password(password)

      sql_insert_user = "INSERT INTO User (id, name, email, password) \
                          VALUES (%s, %s, %s, %s)"
      self.cursor.execute(sql_insert_user, (user_id, username, email, password))

      #创建一个空账户
      self.create_account(user_id ,0.0, "休闲", 1)
      self.db.commit()
      return True

    except mysql.connector.Error as err:
      print(f"mysql went wrong at create_user: {format(err)}")
      self.db.rollback()
      return False
    
    except Exception as e:
      if "User already exists" in str(e):
        print(e)
        return False
      self.db.rollback()
      print("创建失败：{}", e)
      return False

  def create_court(self, level, is_free) :
    try:
      #创建事务
      # self.db.start_transaction()
      sql_select_court_id = "SELECT MAX(court_id) FROM Courts"
      self.cursor.execute(sql_select_court_id)
      result = self.cursor.fetchone()
      court_id = 1 if result[0] is None else result[0] + 1
      sql_insert_court = "INSERT INTO Courts (court_id, level, is_free) \
                          VALUES (%s, %s, %s)"
      self.cursor.execute(sql_insert_court, (court_id, level, is_free))
      self.db.commit()
      return True
    except mysql.connector.Error as err:
      print(f"mysql went wrong at create_court: {format(err)}")
      self.db.rollback()
      return False

    except Exception as e:
      if "Court already exists" in str(e):
        print(e)
      else : print("创建场地失败：{}", e)
      return False

  #TODO:对于场地预定，需要处理高并发场景，因此需要加锁
  def create_court_reservation(self, court_id, subscriber, reserve_date, reserve_time) :
    try:
      if self.check_court_reservation_exist(court_id, reserve_date, reserve_time):
        raise(Exception(f"Court reservation already exists: {court_id}, {reserve_date}, {reserve_time}"))
      #创建事务
      # self.db.start_transaction()
      sql_insert_court_reservation = "INSERT INTO CourtReservations (court_id, subscriber, reserve_date, reserve_time) \
                                      VALUES (%s, %s, %s, %s)"
      self.cursor.execute(sql_insert_court_reservation, (court_id, str(subscriber), reserve_date, reserve_time))
      self.db.commit()
      return True

    except mysql.connector.Error as err:
      print(f"mysql went wrong at create_court_reservation: {format(err)}")
      self.db.rollback()
      return False

    except Exception as e:
      if "Court reservation already exists" in str(e):
        print(e)
      else : print("创建场地预定失败：{}", e)
      return False

# -------------------------------------删除函数--------------------------------------
  def delete_account(self, username) :
    try:
      if not self.check_user_exist(username):
        raise(Exception(f"User not exists: {username}"))
      #创建事务
      self.db.start_transaction()
      sql_select_account_id = "SELECT id FROM Account WHERE name = %s"
      self.cursor.execute(sql_select_account_id, username)
      result = self.cursor.fetchone()
      account_id = result[0]
      sql_delete_account = "DELETE FROM Account WHERE id = %s"
      self.cursor.execute(sql_delete_account, account_id)
      self.db.commit()
      return True

    except mysql.connector.Error as err:
      print(f"mysql went wrong at del_account: {format(err)}")
      self.db.rollback()
      return False
    
    except Exception as e:
      if "User not exists" in str(e):
        print(e)
      else : print("删除账户失败：{}", e)
      return False

  def delete_user(self, username, password) :
    try:
      if not self.check_user_exist(username):
          raise(Exception(f"User not exists: {username}"))
      
      #创建事务
      # self.db.start_transaction()
      sql_delete_user = "DELETE FROM User WHERE name = %s and password = %s"
      self.cursor.execute(sql_delete_user, (username, self._encrypt_password(password)))
      self.db.commit()
      return True
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at del_user: {format(err)}")
      self.db.rollback()
      return False
    except Exception as e:
      if "User not exists" in str(e):
        print(e)
      else : print("删除用户失败：{}", e)
      return False

  def delete_count(self, court_id) :
    try:
      if not self.check_court_exist(court_id):
        raise(Exception(f"Court not exists: {court_id}"))
      #创建事务
      self.db.start_transaction()
      sql_delete_court = "DELETE FROM Courts WHERE court_id = %s"
      self.cursor.execute(sql_delete_court, court_id)
      self.db.commit()
      return True
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at del_court: {format(err)}")
      self.db.rollback()
      return False
    
    except Exception as e:
      if "Court not exists" in str(e):
        print(e)
      else : print("删除场地失败：{}", e)
      return False

  def delete_court_reservation(self, court_id, reserve_date, reserve_time) :
    try: 
      if not self.check_court_reservation_exist(court_id, reserve_date, reserve_time):
        raise(Exception(f"Court reservation not exists: {court_id}, {reserve_date}, {reserve_time}"))
      #创建事务
      self.db.start_transaction()
      sql_delete_court_reservation = "DELETE FROM CourtReservations WHERE court_id = %s and reserve_date = %s and reserve_time = %s"
      self.cursor.execute(sql_delete_court_reservation, (court_id, reserve_date, reserve_time))
      self.db.commit()
      return True
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at del_court_reservation: {format(err)}")
      self.db.rollback()
      return False
    
    except Exception as e:
      if "Court reservation not exists" in str(e):
        print(e)
      else : print("删除场地预定失败：{}", e)
      return False
    
# -------------------------------------更新函数--------------------------------------
  def update_account(self, username, balance, hobby_project, level) :
    try:
      if not self.check_user_exist(username):
        raise(Exception(f"User not exists: {username}"))
      #创建事务
      self.db.start_transaction()
      sql_update_account = "UPDATE Account SET balance = %s, hobby_project = %s, level = %s WHERE name = %s"
      self.cursor.execute(sql_update_account, (balance, hobby_project, level, username))
      self.db.commit()
      return True
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at update_account: {format(err)}")
      self.db.rollback()
      return False
    
    except Exception as e:
      if "User not exists" in str(e):
        print(e)
      else : print("更新账户失败：{}", e)
      return False

# -------------------------------------查找代码--------------------------------------
  def find_user(self, username: str = None, user_id: int = None):
    """
    查询用户详情：基本信息 + 账户信息 + 预约列表。
    至少传 username 或 user_id 之一。
    返回示例：
    {
        "user_id": 1,
        "username": "tom",
        "email": "tom@example.com",
        "balance": 100.0,
        "level": 1,
        "reservations": [
            {
                "court_id": 3,
                "reserve_date": date(...),
                "reserve_time": "18:00:00"
            }
        ]
    }
    """
    try:
      # 参数校验
      if username is None and user_id is None:
        raise ValueError("find_user 需要至少提供 username 或 user_id 之一")

      # 基础 SQL
      sql = """
        SELECT 
          u.id AS user_id,
          u.name AS username,
          u.email,
          a.balance,
          a.level AS account_level,
          cr.court_id,
          cr.reserve_date,
          cr.reserve_time
        FROM User u
        JOIN Account a ON u.id = a.id
        LEFT JOIN CourtReservation cr ON u.id = cr.subscriber
      """

      conditions = []
      params = []

      if username is not None:
        conditions.append("u.name = %s")
        params.append(username)

      if user_id is not None:
        conditions.append("u.id = %s")
        params.append(user_id)

      if conditions:
        sql += " WHERE " + " AND ".join(conditions)

      sql += " ORDER BY cr.reserve_date, cr.reserve_time"

      self.cursor.execute(sql, tuple(params))
      rows = self.cursor.fetchall()

      if not rows:
        return None

      first = rows[0]
      user_info = {
        "user_id": first[0],
        "username": first[1],
        "email": first[2],
        "balance": first[3],
        "level": first[4],
        "reservations": []
      }

      for row in rows:
        court_id = row[5]
        reserve_date = row[6]
        reserve_time = row[7]

        if court_id is not None:
          user_info["reservations"].append({
            "court_id": court_id,
            "reserve_date": reserve_date,
            "reserve_time": reserve_time
          })

      return user_info

    except mysql.connector.Error as err:
      print(f"mysql went wrong at find_user: {format(err)}")
      return None

    except Exception as e:
      print(f"find_user failed: {e}")
      return None

#TODO: 修改为id匹配
  def find_account(self, username) :
    try: 
      if not self.check_user_exist(username):
        raise(Exception(f"User not exists: {username}"))
      else:
        sql_select_account = "SELECT * FROM Account WHERE name = %s"
        self.cursor.execute(sql_select_account, (username,))
        result = self.cursor.fetchone()
        if result is None:
          return None
        else:
          return Account(result[0], result[1], result[2], result[3])
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at find_account: {format(err)}")
      return None
    
    except Exception as e:
      if "User not exists" in str(e):
        print(e)
  
  def find_court(self, court_id) :
    try: 
      if not self.check_court_exist(court_id):
        raise(Exception(f"Court not exists: {court_id}"))
      else:
        sql_select_court = "SELECT * FROM Courts WHERE court_id = %s"
        self.cursor.execute(sql_select_court, (court_id,))
        result = self.cursor.fetchone()
        if result is None:
          return None
        else:
          return Court(result[0], result[1], result[2])
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at find_court: {format(err)}")
      return None
    
    except Exception as e:
      if "Court not exists" in str(e):
        print(e)
  
  def find_court_reservation(self, court_id, reserve_date, reserve_time) :
    try: 
      if not self.check_court_reservation_exist(court_id, reserve_date, reserve_time):
        raise(Exception(f"Court reservation not exists: {court_id}, {reserve_date}, {reserve_time}"))
      else:
        sql_select_court_reservation = "SELECT * FROM CourtReservations \
                                        WHERE court_id = %s and reserve_date = %s and reserve_time = %s"
        self.cursor.execute(sql_select_court_reservation, (court_id, reserve_date, reserve_time))
        result = self.cursor.fetchone()
        if result is None:
          return None
        else:
          return CourtReservation(result[0], result[1], result[2], result[3])
    
    except mysql.connector.Error as err:
      print(f"mysql went wrong at find_court_reservation: {format(err)}")
      return None
    
    except Exception as e:
      if "Court reservation not exists" in str(e):
        print(e)
  
if __name__ == "__main__" :
  system = BadmintonSystem()
    