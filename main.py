################################################################################
# main.py - Main Client
################################################################################

import asyncio
import pyglet
from network import NetworkClient
from game_state import GameState
from input import InputHandler
from renderer import Renderer

class SpacewarClient:
    def __init__(self):
        self.game_state = GameState()
        self.input_handler = InputHandler()
        self.renderer = Renderer()
        self.network = NetworkClient(
            on_state_update=self.on_state_update,
            on_player_id=self.on_player_id
        )
        
        # Set up window event handlers
        self.renderer.window.push_handlers(
            on_key_press=self.input_handler.on_key_press,
            on_key_release=self.input_handler.on_key_release,
            on_draw=self.on_draw
        )
        
        self.input_send_interval = 1/30  # Send inputs 30 times per second
        self.running = True
        self.first_state_received = False
        
    def on_state_update(self, state_data):
        """Called when server sends game state"""
        self.game_state.update_from_server(state_data)
        if not self.first_state_received:
            print(f"First state received: {len(self.game_state.ships)} ships")
            self.first_state_received = True
    
    def on_player_id(self, player_id):
        """Called when server assigns player ID"""
        self.game_state.set_local_player(player_id)
        print(f"You are player {player_id}")
    
    def on_draw(self):
        """Pyglet draw handler"""
        self.renderer.draw(self.game_state)
    
    def update(self, dt):
        """Called by pyglet clock"""
        pass  # State updates come from network
    
    async def input_loop(self):
        """Send inputs to server periodically"""
        while self.running and self.network.connected:
            inputs = self.input_handler.get_inputs()
            await self.network.send_inputs(inputs)
            await asyncio.sleep(self.input_send_interval)
    
    async def run(self, server_uri="ws://localhost:8765"):
        """Run the client"""
        # Connect to server
        await self.network.connect(server_uri)
        
        if not self.network.connected:
            print("Failed to connect to server")
            return
        
        # Start network receive loop
        receive_task = asyncio.create_task(self.network.receive_loop())
        
        # Start input send loop
        input_task = asyncio.create_task(self.input_loop())
        
        # Schedule Pyglet update
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        
        # Run Pyglet event loop in async manner
        try:
            while self.running and not self.renderer.window.has_exit:
                # Process window events
                self.renderer.window.dispatch_events()
                
                # Trigger Pyglet's clock
                pyglet.clock.tick()
                
                # Draw
                self.renderer.window.dispatch_event('on_draw')
                self.renderer.window.flip()
                
                # Allow other async tasks to run
                await asyncio.sleep(0.001)
        finally:
            self.running = False
            await self.network.close()
            receive_task.cancel()
            input_task.cancel()

def main():
    client = SpacewarClient()
    asyncio.run(client.run())

if __name__ == "__main__":
    main()
