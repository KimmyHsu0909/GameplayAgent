from typing import Dict, Any, List, Tuple, Optional
from PIL import Image
import os
import time
import asyncio
import logging
from src.emulators.dos.browser_controller import BrowserController
from src.emulators.interface_base import VideoGameBenchInterface

class DOSGameInterface(VideoGameBenchInterface):
    """DOS Game Interface using Playwright and JSDOS (DOSBOX)"""
    
    def __init__(self, 
                 headless: bool = False,
                 game: str = None,
                 lite: bool = False,
                 key_press_delay: float = 0.1,
                 lite_key_press_delay: float = 0.1,
                 num_screenshots_per_action: int = 0,
                 viewport_width: int = None,
                 viewport_height: int = None,
                 pause_key: str = None,
                 minimum_input_duration: float = 0.0,
                 minimum_mouse_duration: float = None,
                 minimum_space_duration: float = None,
                 mouse_only: bool = False,
                 ):
        super().__init__()
        self.headless = headless
        self.game = game
        self.lite = lite
        self.key_press_delay_ms = key_press_delay * 1000
        self.browser = BrowserController(headless=headless)
        self.num_screenshots_per_action = num_screenshots_per_action
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.pause_key = pause_key or "Alt+Pause"
        legacy_minimum = max(0.0, minimum_input_duration)
        self.minimum_mouse_duration = max(
            0.0,
            legacy_minimum if minimum_mouse_duration is None else minimum_mouse_duration,
        )
        self.minimum_space_duration = max(
            0.0,
            legacy_minimum if minimum_space_duration is None else minimum_space_duration,
        )
        self.mouse_only = mouse_only

        # Lite condition, can change
        if lite:
            self.key_press_delay_ms = lite_key_press_delay * 1000
            self.num_screenshots_per_action = 3

    async def load_game(self, initial_url: str) -> bool:
        """
        Load a DOS game from a URL.
        """
        pass
        """
        Start the agent by initializing the browser.
        """
        await self.browser.start(viewport_width=self.viewport_width, viewport_height=self.viewport_height)
        
        # Navigate to the initial URL
        await self.browser.navigate(initial_url)

        # Pre-loaded actions based on game
        await self.browser.pre_load(self.game)

        if self.lite:
            await self.browser.press_key(self.pause_key, delay_ms=0)
    
    
    async def click(self, action_input: str, press_key_delay: float = 0.5) -> str:
        x, y = self.browser.current_mouse_position
        option_input = action_input or ""

        parts = [part.strip() for part in option_input.split(",")]
        if len(parts) >= 2:
            try:
                x, y = float(parts[0]), float(parts[1])
                option_input = ",".join(parts[2:])
            except ValueError:
                pass

        if not action_input and (x, y) == (0, 0):
            return "Click ignored at (0, 0): provide visible target coordinates as x,y."

        click_options = {}
        if option_input:
            if "right" in option_input.lower():
                click_options["button"] = "right"
            
            modifiers = []
            if "shift" in option_input.lower():
                modifiers.append("Shift")
            if "ctrl" in option_input.lower():
                modifiers.append("Control")
            if "alt" in option_input.lower():
                modifiers.append("Alt")
            if modifiers:
                click_options["modifiers"] = modifiers
        else:
            click_options = None
        
        if self.minimum_mouse_duration > 0:
            button = click_options.get("button", "left") if click_options else "left"
            await self.browser.hold_mouse(
                x,
                y,
                self.minimum_mouse_duration,
                button=button,
                modifiers=click_options.get("modifiers", []) if click_options else [],
            )
            result = (
                f"Mouse held at ({x}, {y}) for "
                f"{self.minimum_mouse_duration} seconds"
            )
        else:
            await self.browser.click(x, y, click_options)
            result = f"Mouse clicked at ({x}, {y}) with options: {click_options}"
        return result

    async def hold_mouse(self, action_input: str, delay_ms: float = 100) -> str:
        parts = [part.strip() for part in action_input.split(",")]
        if len(parts) < 2:
            raise ValueError("hold_mouse requires x,y[,duration]")

        x, y = float(parts[0]), float(parts[1])
        requested_duration = float(parts[2]) if len(parts) > 2 else 1.0
        duration = max(requested_duration, self.minimum_mouse_duration)
        await self.browser.hold_mouse(x, y, duration)
        return f"Held mouse at ({x}, {y}) for {duration} seconds"

    async def move(self, action_input: str, press_key_delay_ms: float = 0.5) -> str:
        x, y = map(float, action_input.split(","))
        await self.browser.move_mouse(x, y)
        result = f"Mouse moved to ({x}, {y})"
        return result

    async def drag(self, action_input: str, press_key_delay_ms: float = 0.5) -> str:
        x, y = map(float, action_input.split(","))
        await self.browser.drag(x, y)
        result = f"Mouse dragged to ({x}, {y})"
        return result

    async def scroll_down(self, action_input: str, press_key_delay_ms: float = 100) -> str:
        amount = int(action_input)
        await self.browser.scroll_down(amount)
        result = f"Scrolled down {amount} pixels."
        return result

    async def scroll_up(self, action_input: str, press_key_delay_ms: float = 100) -> str:
        amount = int(action_input)
        await self.browser.scroll_up(amount)
        result = f"Scrolled up {amount} pixels."
        return result

    async def write(self, action_input: str, press_key_delay_ms: float = 100) -> str:
        await self.browser.type_text(action_input)
        result = f"Typed: {action_input}"
        return result

    async def press_key(self, action_input: str, press_key_delay_ms: float = 100) -> Tuple[str, List[bytes]]:
        screenshots = []
        if "," in action_input:
            keys = action_input.split(",")
            for key in keys:
                key = key.strip()
                key_delay_ms = press_key_delay_ms
                if key.lower() == "space":
                    key_delay_ms = max(
                        key_delay_ms,
                        self.minimum_space_duration * 1000,
                    )
                await self.browser.press_key(key, lite_mode=self.lite, delay_ms=key_delay_ms)
                screenshot = await self.browser.get_screenshot()
                screenshots.append(screenshot)
                await asyncio.sleep(key_delay_ms / 1000)
            result = f"Pressed keys: {action_input}"
        else:
            key_delay_ms = press_key_delay_ms
            if action_input.strip().lower() == "space":
                key_delay_ms = max(
                    key_delay_ms,
                    self.minimum_space_duration * 1000,
                )
            await self.browser.press_key(action_input, lite_mode=self.lite, delay_ms=key_delay_ms)
            result = f"Pressed key: {action_input}"
        return result, screenshots

    async def hold_key(self, action_input: str, delay_ms: float = 100) -> str:
        parts = action_input.split(",")
        key = parts[0].strip()
        duration = float(parts[1]) if len(parts) > 1 else 0.5
        if key.lower() == "space":
            duration = max(duration, self.minimum_space_duration)
        await self.browser.press_key(
            key,
            lite_mode=self.lite,
            delay_ms=duration * 1000,
        )
        result = f"Held key {key} for {duration} seconds"
        return result


    async def step(self, 
                    action: str, 
                    action_input: str,
                    key_press_delay_ms: Optional[float] = None,
                    ) -> str:
        """Execute an action and return the observation."""
        key_press_delay_ms = self.key_press_delay_ms if key_press_delay_ms is None else key_press_delay_ms

        try:
            # Execute the action
            result = None
            frames = []

            if self.lite:
                await self.browser.press_key(self.pause_key, delay_ms=0)
                await asyncio.sleep(0.01)

            action_map = {
                'click': self.click,
                'hold_mouse': self.hold_mouse,
                'move': self.move,
                'move_mouse': self.move, # Add alias for move_mouse
                'move_mouse_left': lambda *args: self.move("left", *args),
                'move_mouse_right': lambda *args: self.move("right", *args), 
                'move_mouse_up': lambda *args: self.move("up", *args),
                'move_mouse_down': lambda *args: self.move("down", *args),
                'drag': self.drag,
                'scroll_down': self.scroll_down,
                'scroll_up': self.scroll_up,
                'write': self.write,
                'press_key': self.press_key,
                'hold_key': self.hold_key,
            }

            if action is None:
                result = "No action provided."
            else:
                action = action.lower().strip()
                if self.mouse_only and action in {"write", "press_key", "hold_key"}:
                    result = (
                        f"Action {action} is disabled: this game must be played "
                        "using mouse actions only."
                    )
                    action = None
                if action in action_map.keys():
                    result = await action_map[action](action_input, key_press_delay_ms)
                    if isinstance(result, tuple):
                        result, frames = result
                elif action is not None:
                    result = f"Unknown action: {action}"

            # Take screenshots for approximately 0.5 seconds
            for _ in range(self.num_screenshots_per_action):
                frame = await self.browser.get_screenshot()
                frames.append(frame)
                await asyncio.sleep(key_press_delay_ms / 1000) 

            # Pause game
            if self.lite:
                await self.browser.press_key(self.pause_key, delay_ms=0)
            
            # Under real benchmark (not lite), take screenshot here
            if not frames or len(frames) == 0:
                screenshot = await self.browser.get_screenshot()
                frames = [screenshot]
                
            return result if result else f"Unknown action: {action}", frames

        except Exception as e:
            error_msg = f"Error executing action: {str(e)}"
            
            if self.lite:
                try:
                    await self.browser.press_key(self.pause_key, delay_ms=0)
                except Exception as pause_error:
                    error_msg += f"; pause recovery failed: {pause_error}"

            try:
                screenshot = await self.browser.get_screenshot()
                return error_msg, [screenshot]
            except Exception as screenshot_error:
                return f"{error_msg}; screenshot recovery failed: {screenshot_error}", []
        
    async def close(self) -> None:
        """Clean up resource[screen]."""
        await self.browser.close()

    async def get_observation(self) -> Optional[Dict[str, Any]]:
        """
        Get current screenshot from Playwright.
        """
        screenshot = await self.browser.get_screenshot()
        return screenshot
