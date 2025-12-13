To run the game:

1. Install dependencies:
   pip install websockets pyglet numpy

2. Start the server (in one terminal):
   server.cmd

3. Start clients (in separate terminals, up to 4):
   client.cmd

Controls:
- Arrow Keys / WASD: Rotate and thrust
- SPACE: Shoot
- R: Respawn (when dead)

The server handles:
- Physics simulation (60Hz)
- Gravity from central sun
- Collision detection
- Broadcasting game state

Each client:
- Connects via WebSocket
- Sends inputs to server
- Receives game state updates
- Renders locally with Pyglet

Have fun!