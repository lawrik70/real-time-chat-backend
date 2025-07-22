from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str  # In a real app, this would be hashed

class Message(BaseModel):
    sender: str
    content: str
    timestamp: int
    room: str

class Room(BaseModel):
    name: str
    users: List[str] = []
    messages: List[Message] = []

# In-memory storage
users_db: Dict[str, User] = {}
rooms_db: Dict[str, Room] = {}
active_connections = {}