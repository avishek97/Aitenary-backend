from pydantic import BaseModel 

class UserDTO(BaseModel):
    name: str
    username: str
    password: str
    email: str 
    mobile: int

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: str 
    mobile_number: int

class loginDTO(BaseModel):
    email: str
    password: str