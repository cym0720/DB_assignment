from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from badminton_sys.badminton_sys import BadmintonSystem
from typing import List

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
  reservations : List[CourtReservation]
  
class Password(BaseModel):
  password : str
  
class LoginResponse(BaseModel):
  username : str
  password : str

@app.post("/users/signup", summary="创建用户")
def create_user(user: UserCreate):
  success = system.create_user(user.username, user.email, user.password)
  if not success:
    raise HTTPException(status_code=400, detail="User creation failed")
  return {"message": "User created successfully"}

@app.get("/users/{username}", summary="根据用户名获取用户信息")
def get_user(username: str):
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
    "message" : "登陆成功",
    "user"    : user_data
  }
