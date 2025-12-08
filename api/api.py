from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from badminton_sys.badminton_sys import BadmintonSystem
from typing import List

app = FastAPI()

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

@app.post("/users", summary="创建用户")
def create_user(user: UserCreate):
  success = system.create_user(user.username, user.email, user.password)
  if not success:
    raise HTTPException(status_code=400, detail="User creation failed")
  return {"message": "User created successfully"}

@app.get("/users/{username}", summary="根据用户名获取用户信息")
def get_user(username: str):
  user_data = system.find_user(username)
  if user_data is None:
    raise HTTPException(status_code=404, detail="User not found")
  
  reservations = [
    CourtReservation(
      court_id     = r["court_id"],
      reserve_date = r["reserve_date"],
      reserve_time = r["reserve_time"]
    )
    for r in user_data["reservations"]
  ]

  user_info = UserInfo(
    user_id      = user_data["user_id"],
    username     = user_data["username"],
    email        = user_data["email"],
    level        = user_data["level"],
    balance      = user_data["balance"],
    reservations = reservations
  )
  return user_info

  