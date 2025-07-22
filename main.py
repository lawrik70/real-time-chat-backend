from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from models import User, Message, Room, users_db, rooms_db, active_connections
from datetime import datetime
import secrets

app = FastAPI()
security = HTTPBasic()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:4200"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# For production: mount Angular build files
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Helper functions
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    print(users_db)
    print(credentials.username)
    if credentials.username not in users_db:
        raise HTTPException(status_code=401, detail="Username not found")
    user = users_db[credentials.username]
    if not secrets.compare_digest(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return credentials.username


# REST endpoints
@app.post("/register")
async def register(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = user
    return {"message": "User created successfully"}


@app.get("/rooms")
async def get_rooms():
    return {"rooms": list(rooms_db.keys())}


@app.post("/rooms")
async def create_room(room: Room):
    print ("entered post")
    if room.name in rooms_db:
        raise HTTPException(status_code=400, detail="Room already exists")
    rooms_db[room.name] = Room(name=room.name)
    return {"message": f"Room '{room.name}' created successfully"}


# WebSocket endpoint
@app.websocket("/ws/{room_name}/{username}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, username: str):
    if room_name not in rooms_db:
        await websocket.close(code=1008, reason="Room does not exist")
        return

    room = rooms_db[room_name]

    # Add user to room and active connections
    if username not in room.users:
        room.users.append(username)
    active_connections[(room_name, username)] = websocket

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            message = Message(
                sender=username,
                content=data,
                timestamp=int(datetime.now().timestamp()),
                room=room_name
            )

            # Add message to room history
            room.messages.append(message)
            print(room.messages)
            # Broadcast message to all users in the room
            print(room.users)
            print(active_connections)
            for user in room.users:
                print(user)
                if (room_name, user) in active_connections:
                    conn = active_connections[(room_name, user)]
                    print("sending message")
                    print(message)
                    await conn.send_json(message.dict())
    except WebSocketDisconnect:
        # Remove connection when user disconnects
        del active_connections[(room_name, username)]
        await broadcast_user_list(room_name)


async def broadcast_user_list(room_name: str):
    print(room_name)
    if room_name in rooms_db:
        room = rooms_db[room_name]
        user_list = {"type": "user_list", "users": room.users}
        for user in room.users:
            if (room_name, user) in active_connections:
                conn = active_connections[(room_name, user)]
                await conn.send_json(user_list)