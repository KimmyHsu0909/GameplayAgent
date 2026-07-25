import asyncio
import base64
import logging
import math
import random
import time
from typing import List, Optional, Tuple, Union
import platform

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserController:
    """
    Controller for browser interactions using Playwright.
    Implements human-like mouse movements and interactions.
    """
    def __init__(self, headless: bool = False):
        """
        Initialize the browser controller.
        
        Args:
            headless: Whether to run the browser in headless mode
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_mouse_position = (0, 0)
        self.paused = False
        self.pause_task = None  # Add this to track the pause task
    
    async def pre_load(self, game: str) -> None:
        """
        Read and execute preload actions from a config file for the specified game.
        
        Args:
            game: Name of the game to preload
        """
        config_path = f"configs/{game}/preload.txt"

        # Get around locking
        try:
            with open(config_path, 'r') as f:
                actions = f.readlines()
            
            for action in actions:
                action = action.strip()
                if not action or action.startswith('#'):
                    continue
                    
                parts = action.split()
                command = parts[0].lower()
                
                if command == "sleep":
                    seconds = float(parts[1])
                    await asyncio.sleep(seconds)
                    print(f"Waited for {seconds} seconds")
                    
                elif command == "move_mouse":
                    x, y = float(parts[1]), float(parts[2])
                    await self.move_mouse(x, y)
                    print(f"Moved mouse to ({x}, {y})")
                    
                elif command == "click":
                    x, y = float(parts[1]), float(parts[2])
                    await self.click(x, y)
                    print(f"Clicked at ({x}, {y})")
                    
                elif command == "press_key":
                    key = parts[1]
                    await self.press_key(key)
                    print(f"Pressed key: {key}")
                    
                else:
                    print(f"Unknown command: {command}")
                    
        except FileNotFoundError:
            print(f"Warning: No preload configuration found at {config_path}")
        except Exception as e:
            print(f"Error executing preload actions: {e}")

    async def start(self, viewport_width: Optional[int] = None, viewport_height: Optional[int] = None) -> None:
        """
        Start the browser.
        """
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless, args=["--disable-web-security"])

        if viewport_width and viewport_height:
            viewport_dimensions = {"width": viewport_width, "height": viewport_height}
        else:
            viewport_dimensions = {"width": 640, "height": 400} if platform.system() == "Darwin" else {"width": 700, "height": 475}
        self.context = await self.browser.new_context(
            viewport=viewport_dimensions,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # Set initial mouse position
        self.current_mouse_position = (0, 0)
        
        logger.info("Browser started successfully")
        
    async def close(self) -> None:
        """
        Close the browser.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed successfully")
        
    async def navigate(self, url: str) -> None:
        """
        Navigate to a URL.
        
        Args:
            url: The URL to navigate to
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        await self.page.goto(url)
        logger.info(f"Navigated to {url}")
        
    async def get_screenshot(self) -> bytes:
        """
        Get a screenshot of the current page.
        
        Returns:
            The screenshot as bytes
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        viewport = self.page.viewport_size or {"width": 640, "height": 400}
        screenshot = await self.page.screenshot(
            type="jpeg",
            quality=100,
            clip={
                "x": 0,
                "y": 0,
                "width": viewport["width"],
                "height": viewport["height"],
            },
        )
        logger.info("Screenshot captured")
        return screenshot
        
    async def move_mouse(self, x: float, y: float) -> None:
        """
        Move the mouse to the specified coordinates with human-like movement.
        
        Args:
            x: The x coordinate
            y: The y coordinate
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        # Get current mouse position
        start_x, start_y = self.current_mouse_position
        
        # Generate a human-like path for the mouse movement
        path = self._generate_human_like_path(start_x, start_y, x, y)
        
        # Move the mouse along the path
        for point_x, point_y in path:
            await self.page.mouse.move(point_x, point_y)
            # Add a small delay to simulate human movement speed
            await asyncio.sleep(random.uniform(0.001, 0.005))
        
        # Update current mouse position
        self.current_mouse_position = (x, y)
        logger.info(f"Mouse moved to ({x}, {y})")

    async def move_mouse_right(self) -> None:
        """Move the mouse 10 pixels to the right."""
        x, y = self.current_mouse_position
        await self.move_mouse(x + 10, y)

    async def move_mouse_left(self) -> None:
        """Move the mouse 10 pixels to the left."""
        x, y = self.current_mouse_position
        await self.move_mouse(x - 10, y)

    async def move_mouse_up(self) -> None:
        """Move the mouse 10 pixels up."""
        x, y = self.current_mouse_position
        await self.move_mouse(x, y - 10)

    async def move_mouse_down(self) -> None:
        """Move the mouse 10 pixels down."""
        x, y = self.current_mouse_position
        await self.move_mouse(x, y + 10)
        
    async def click(self, x: float, y: float, options: dict = None) -> None:
        """
        Click at the specified coordinates with human-like movement.
        
        Args:
            x: The x coordinate
            y: The y coordinate
            options: Dictionary of click options including:
                - button: 'left' (default) or 'right'
                - modifiers: list of modifiers ('Shift', 'Control', 'Alt')
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        # First move the mouse to the target position
        await self.move_mouse(x, y)
        
        # Add a small delay before clicking (like a human would)
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Apply click options
        if options:
            await self.page.mouse.click(x, y, **options)
        else:
            await self.page.mouse.click(x, y)
        
        logger.info(f"Clicked at ({x}, {y}) with options: {options}")
        
    async def drag(self, x: float, y: float) -> None:
        """
        Drag from current position to the specified coordinates.
        
        Args:
            x: The x coordinate to drag to
            y: The y coordinate to drag to
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        # Get current mouse position
        start_x, start_y = self.current_mouse_position
        
        # Press mouse button down at current position
        await self.page.mouse.down()
        
        # Generate a human-like path for the drag movement
        path = self._generate_straight_path(start_x, start_y, x, y)
        
        # Move the mouse along the path
        for point_x, point_y in path:
            await self.page.mouse.move(point_x, point_y)
            # Add a small delay to simulate human movement speed
            await asyncio.sleep(random.uniform(0.005, 0.01))
        
        # Release mouse button at target position
        await self.page.mouse.up()
        
        # Update current mouse position
        self.current_mouse_position = (x, y)
        logger.info(f"Dragged from ({start_x}, {start_y}) to ({x}, {y})")
        
    async def scroll_down(self, amount: int) -> None:
        """
        Scroll down by the specified amount.
        
        Args:
            amount: The amount to scroll down in pixels
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        await self.page.mouse.wheel(0, amount)
        logger.info(f"Scrolled down {amount} pixels")
        
    async def scroll_up(self, amount: int) -> None:
        """
        Scroll up by the specified amount.
        
        Args:
            amount: The amount to scroll up in pixels
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        await self.page.mouse.wheel(0, -amount)
        logger.info(f"Scrolled up {amount} pixels")
        
    async def type_text(self, text: str) -> None:
        """
        Type text with human-like timing.
        
        Args:
            text: The text to type
        """
        if not self.page:
            raise ValueError("Browser not started")
        
        # Type with human-like delays between keystrokes
        for char in text:
            await self.page.keyboard.press(char)
            # Add a random delay between keystrokes
            await asyncio.sleep(random.uniform(0.05, 0.15))

        logger.info(f"Typed: {text}")
    
    async def _pause_loop(self) -> None:
        """
        Internal method to run the pause loop.
        """
        while self.paused:
            await self.page.keyboard.press("Alt+Pause")
            await asyncio.sleep(0.01)  # Wait 0.01ms between presses

    async def pause_dos(self) -> None:
        """
        Pause the DOS game by continuously pressing Alt+Pause in a non-blocking way.
        """
        if self.pause_task is not None:
            return  # Already paused
            
        self.paused = True
        self.pause_task = asyncio.create_task(self._pause_loop())
        logger.info("DOS game paused")

    async def unpause_dos(self) -> None:
        """
        Unpause the DOS game by stopping the pause loop.
        """
        self.paused = False
        if self.pause_task:
            await self.pause_task  # Wait for the task to complete
            self.pause_task = None
        # Press Alt+Pause one final time to ensure unpaused state
        logger.info("DOS game unpaused")

    async def press_key(self, key: str, 
                        lite_mode: bool = False, 
                        delay_ms: float = 100) -> None:
        """
        Press a specific key or key combination.
        
        Args:
            key: The key to press (e.g., "KeyA", "ArrowLeft", "Shift+KeyA")
            lite_mode: Whether to use lite mode
            delay_ms: The delay in milliseconds when pressing key.
        """
        if not self.page:
            raise ValueError("Browser not started")

        # Handle key combinations like "Shift+KeyA"
        if "," in key:
            logger.info(f"Pressing key: {key}")
            keys = key.split("+")
            
            # Press down all modifier keys first
            for modifier in keys[:-1]:
                await self.page.keyboard.down(modifier)
            
            # Press the final key
            await self.page.keyboard.press(keys[-1], delay=delay_ms)
            
            # Release all modifier keys in reverse order
            for modifier in reversed(keys[:-1]):
                await self.page.keyboard.up(modifier)
        
        # Handle single key press
        else:
            await self.page.keyboard.press(key, delay=delay_ms)
        
        logger.info(f"Pressed key: {key}")

    def _generate_straight_path(
        self, 
        start_x: float, 
        start_y: float, 
        end_x: float, 
        end_y: float,
    ) -> List[Tuple[float, float]]:
        """
        Generate a straight line path between two points.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            end_x: Ending x coordinate
            end_y: Ending y coordinate
            control_points: Unused, kept for compatibility
            
        Returns:
            A list of (x, y) coordinates representing the straight path
        """
        # Calculate distance between start and end points
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        # Determine number of steps based on distance
        steps = max(10, int(distance / 10))
        
        path = []
        for i in range(steps + 1):
            t = i / steps
            # Linear interpolation between start and end points
            x = start_x + t * (end_x - start_x)
            y = start_y + t * (end_y - start_y)
            path.append((x, y))
            
        return path

    def _generate_human_like_path(
        self, 
        start_x: float, 
        start_y: float, 
        end_x: float, 
        end_y: float, 
        control_points: int = 3
    ) -> List[Tuple[float, float]]:
        """
        Generate a human-like path for mouse movement using Bezier curves.
        
        Args:
            start_x: Starting x coordinate
            start_y: Starting y coordinate
            end_x: Ending x coordinate
            end_y: Ending y coordinate
            control_points: Number of control points for the Bezier curve
            
        Returns:
            A list of (x, y) coordinates representing the path
        """
        # Calculate distance between start and end points
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        # Determine number of steps based on distance
        steps = max(10, int(distance / 10))
        
        # Generate control points for the Bezier curve
        control_xs = [start_x]
        control_ys = [start_y]
        
        # Add random control points
        for i in range(control_points):
            # Add some randomness to the control points
            # The control points should be closer to the straight line for longer distances
            max_offset = min(100, distance * 0.2)
            
            # Calculate a point along the straight line
            t = (i + 1) / (control_points + 1)
            line_x = start_x + t * (end_x - start_x)
            line_y = start_y + t * (end_y - start_y)
            
            # Add random offset
            control_x = line_x + random.uniform(-max_offset, max_offset)
            control_y = line_y + random.uniform(-max_offset, max_offset)
            
            control_xs.append(control_x)
            control_ys.append(control_y)
        
        # Add end point
        control_xs.append(end_x)
        control_ys.append(end_y)
        
        # Generate points along the Bezier curve
        path = []
        for i in range(steps + 1):
            t = i / steps
            
            # Calculate point on the Bezier curve
            x = self._bezier_point(t, control_xs)
            y = self._bezier_point(t, control_ys)
            
            path.append((x, y))
        
        return path
    
    def _bezier_point(self, t: float, control_points: List[float]) -> float:
        """
        Calculate a point on a Bezier curve.
        
        Args:
            t: Parameter between 0 and 1
            control_points: List of control point coordinates
            
        Returns:
            The coordinate of the point on the Bezier curve
        """
        n = len(control_points) - 1
        point = 0
        
        for i in range(n + 1):
            # Calculate binomial coefficient
            binomial = math.comb(n, i)
            
            # Calculate Bernstein polynomial
            bernstein = binomial * (t ** i) * ((1 - t) ** (n - i))
            
            # Add contribution of this control point
            point += control_points[i] * bernstein
        
        return point
