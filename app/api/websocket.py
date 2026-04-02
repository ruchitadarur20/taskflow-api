from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import JWTError, jwt

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.connection_manager import manager

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/projects/{project_id}")
async def project_websocket(
    websocket: WebSocket,
    project_id: int,
    token: str = Query(...),
):
    """
    Connect to receive real-time updates for a project.

    Pass your JWT access token as a query parameter:
        ws://host/ws/projects/1?token=<access_token>

    Events pushed:
      - task_created
      - task_status_changed
      - comment_added
      - member_added
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") is None:
            await websocket.close(code=4001)
            return
    except JWTError:
        await websocket.close(code=4001)
        return

    await manager.connect(project_id, websocket)
    try:
        while True:
            # Keep the connection alive; server pushes events
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
