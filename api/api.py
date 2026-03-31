from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from badminton_sys.badminton_sys import BadmintonSystem
from typing import List
import os
import requests
from datetime import datetime

app = FastAPI()
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

system = BadmintonSystem()
class CourtReservation(BaseModel):
  court_id : int
  subscriber : int
  reserve_time : str
  reserve_date : str

class UserCreate(BaseModel):
  username : str
  email    : str
  password : str
  
class UserLogin(BaseModel):
  username : str
  password : str
  
class UserInfo(BaseModel):
  user_id  : int
  username : str
  email    : str
  level    : float
  balance  : float
  
class CourtInfo (BaseModel) :
  courts   : List [int]

class CourtReservations (BaseModel) :
  reservations : List[CourtReservation]

class Password(BaseModel):
  password : str
  
class LoginResponse(BaseModel):
  username : str
  password : str
  
class AdminLogin(BaseModel) :
  username : str
  password : str

class RechargeRequest(BaseModel):
  amount: float

class UpdateProfileRequest(BaseModel):
  email: str

class UpdatePasswordRequest(BaseModel):
  old_password: str
  new_password: str

class UpdateCourtLevelRequest(BaseModel):
  level: int

class AIRequest(BaseModel):
  prompt: str

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Admin@123"
ADMIN_TOKEN = "admin-token-2025"

def require_admin(x_admin_token: str = Header(None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="无管理员权限")

@app.post("/users/signup", summary="创建用户")
def create_user(user: UserCreate):
  success = system.create_user(user.username, user.email, user.password)
  if not success:
    raise HTTPException(status_code=400, detail="User creation failed")
  return {"message": "User created successfully"}

@app.get("/users/{username}", summary="根据用户名获取用户信息")
def get_user(username: str):
  print(username)
  user_data = system.find_user(username)
  if user_data is None:
    raise HTTPException(status_code=404, detail="User data not found")
  return user_data

@app.post("/users/delete/{username}", summary="删除用户")
def delete_user(username: str, user_password: Password):
  success = system.delete_user(username, user_password.password)
  if not success:
    raise HTTPException(status_code=400, detail="User deletion failed")
  return {"message": "User deleted successfully"}

@app.post("/users/login", summary = "用户登录")
def login_user(user: UserLogin) :
  success = system.check_user_exist(user.username)
  if not success:
    raise HTTPException(status_code=400, detail="User not found")
  
  success = system.check_password(user.username, user.password)
  if not success:
    raise HTTPException(status_code=400, detail="Incorrect password")

  user_data = system.find_user(username = user.username)

  return {
    "message" : "登录成功",
    "user"    : user_data
  }

@app.get("/courts/info", summary="获取场地信息") 
def get_court_info(level: int | None = None) :
  court_data = system.find_court_info(level)
  if len(court_data["courts"]) == 0:
    raise HTTPException(status_code=404, detail="No court data found")
  return court_data

@app.get("/courts/reservations/info", summary="获取场地预约信息")
def get_court_reservations_info() :
  reservations = system.find_reservation_info()
  if len(reservations) == 0:
    raise HTTPException(status_code=404, detail="No reservation data found")
  return reservations

@app.post("/courts/reservations/create", summary="创建场地预约")
def create_court_reservation(reservation: CourtReservation) :
  success = system.create_reservation(
    court_id     = reservation.court_id,
    subscriber   = int(reservation.subscriber),
    reserve_date = reservation.reserve_date,
    reserve_time = reservation.reserve_time
  )
  if not success:
    raise HTTPException(status_code=400, detail="Reservation creation failed")
  return {"message": "Reservation created successfully"}

@app.post("/courts/reservations/delete", summary="删除场地预约")
def delete_court_reservation(reservation: CourtReservation) :
  success = system.delete_court_reservation(
    court_id     = reservation.court_id,
    reserve_date = reservation.reserve_date,
    reserve_time = reservation.reserve_time
  )
  if not success:
    raise HTTPException(status_code=400, detail="Reservation deletion failed")
  return {"message": "Reservation deleted successfully"}

@app.post("/users/{username}/recharge", summary="用户充值")
def recharge_user(username: str, req: RechargeRequest):
  if req.amount <= 0:
    raise HTTPException(status_code=400, detail="amount must be positive")
  new_balance = system.recharge_balance(username, req.amount)
  if new_balance is None:
    raise HTTPException(status_code=400, detail="充值失败")
  return {"message": "recharge success", "new_balance": new_balance}

@app.post("/users/{username}/profile", summary="更新用户资料")
def update_user_profile(username: str, req: UpdateProfileRequest):
  ok = system.update_user_email(username, req.email)
  if not ok:
    raise HTTPException(status_code=400, detail="更新失败")
  return {"message": "update success"}

@app.post("/users/{username}/password", summary="修改用户密码")
def update_user_password(username: str, req: UpdatePasswordRequest):
  if len(req.new_password) < 6:
    raise HTTPException(status_code=400, detail="新密码长度至少6位")
  ok = system.update_user_password(username, req.old_password, req.new_password)
  if not ok:
    raise HTTPException(status_code=400, detail="旧密码错误或更新失败")
  return {"message": "password updated"}

# 管理页面需要的api
@app.post("/admin/login")
def admin_login(req: AdminLogin):
    if req.username == ADMIN_USERNAME and req.password == ADMIN_PASSWORD:
        return {"role": "admin", "token": ADMIN_TOKEN}
    raise HTTPException(status_code=401, detail="管理员账号或密码错误")

# -------- 经营统计（概览）--------
@app.get("/admin/stats/overview")
def admin_stats_overview(_=Depends(require_admin)):
    return {
        "user_count": system.admin_count_users(),
        "court_count": system.admin_count_courts(),
        "reservation_count": system.admin_count_reservations(),
    }

# -------- 用户管理：列表/删除--------
@app.get("/admin/users")
def admin_list_users(_=Depends(require_admin)):
    return system.admin_list_users()

@app.delete("/admin/users/{username}")
def admin_delete_user(username: str, _=Depends(require_admin)):
    ok = system.admin_delete_user_by_name(username)
    if not ok:
        raise HTTPException(status_code=400, detail="删除失败：用户不存在或数据库删除异常")
    return {"ok": True}

# -------- 场地管理：列表/新增/删除--------
class CreateCourtReq(BaseModel):
    court_id: int
    level: int = 1

@app.get("/admin/courts")
def admin_list_courts(_=Depends(require_admin)):
    return system.admin_list_courts()

@app.post("/admin/courts")
def admin_create_court(req: CreateCourtReq, _=Depends(require_admin)):
    system.admin_create_court(req.court_id, req.level)
    return {"ok": True}

@app.delete("/admin/courts/{court_id}")
def admin_delete_court(court_id: int, _=Depends(require_admin)):
    system.admin_delete_court(court_id)
    return {"ok": True}

@app.put("/admin/courts/{court_id}")
def admin_update_court(court_id: int, req: UpdateCourtLevelRequest, _=Depends(require_admin)):
    ok = system.admin_update_court_level(court_id, req.level)
    if not ok:
        raise HTTPException(status_code=400, detail="更新失败")
    return {"ok": True}

# -------- 预约管理：列表/删除--------
@app.get("/admin/reservations")
def admin_list_reservations(_=Depends(require_admin)):
    return system.admin_list_reservations()

class DeleteReservationReq(BaseModel):
    court_id: int
    subscriber: int
    reserve_date: str
    reserve_time: str  # "08:00:00"

@app.post("/admin/reservations/delete")
def admin_delete_reservation(req: DeleteReservationReq, _=Depends(require_admin)):
    system.admin_delete_reservation(
        req.court_id, req.subscriber, req.reserve_date, req.reserve_time
    )
    return {"ok": True}

def _extract_ai_text(payload: dict) -> str:
  if isinstance(payload.get("output_text"), str) and payload.get("output_text"):
    return payload["output_text"].strip()
  outputs = payload.get("output", [])
  texts = []
  for item in outputs:
    if item.get("type") == "message":
      for c in item.get("content", []):
        if c.get("type") == "output_text" and "text" in c:
          texts.append(c["text"])
    elif item.get("type") == "output_text" and "text" in item:
      texts.append(item["text"])
  return "\n".join([t for t in texts if t]).strip()

@app.post("/ai/suggest", summary="AI 训练建议")
def ai_suggest(req: AIRequest):
  api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
  if not api_key:
    raise HTTPException(status_code=400, detail="DEEPSEEK_API_KEY 未配置")

  model = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
  prompt = (req.prompt or "").strip()
  if not prompt:
    raise HTTPException(status_code=400, detail="请输入问题")

  try:
    response = requests.post(
      "https://api.deepseek.com/chat/completions",
      headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
      },
      json={
        "model": model,
        "messages": [
          {"role": "system", "content": "你是羽毛球训练助理，给出清晰、可执行的训练建议，要求简短最好就三条"},
          {"role": "user", "content": prompt}
        ],
        "stream": False
      },
      timeout=30
    )
    if not response.ok:
      raise HTTPException(status_code=502, detail=f"DeepSeek API 调用失败: {response.text}")
    data = response.json()
    text = ""
    if isinstance(data, dict) and data.get("choices"):
      msg = data["choices"][0].get("message", {})
      text = (msg.get("content") or "").strip()
    return {"answer": text or "未生成有效内容"}
  except HTTPException:
    raise
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"AI 调用异常: {str(e)}")

@app.get("/server/time", summary="获取服务器时间")
def get_server_time():
  now = datetime.now()
  return {
    "iso": now.isoformat(),
    "date": now.strftime("%Y-%m-%d"),
    "time": now.strftime("%H:%M:%S")
  }
