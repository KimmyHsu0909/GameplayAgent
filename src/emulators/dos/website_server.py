import http.server
import socketserver
import os
import logging
import threading
import urllib.parse
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import platform

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DOSGameServer:
    """
    Simple HTTP server for hosting js-dos games.
    """
    def __init__(self, port: int = 8000, lite: bool = False):
        """
        Initialize the DOS game server.
        
        Args:
            port: The port to run the server on
        """
        self.port = port
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.lite_mode = lite

    def start(self, game_url: str, custom_html: str = None) -> str:
        """
        Start the server with the specified game.
        
        Args:
            game_url: URL to the js-dos game bundle
            
        Returns:
            The URL to access the game
        """
        if self.is_running:
            logger.warning("Server is already running")
            return f"http://localhost:{self.port}"
            
        # Create a custom request handler with the game URL
        handler = self._create_request_handler(game_url, custom_html, self.lite_mode)
        
        # Create and start the server
        self.server = socketserver.TCPServer(("", self.port), handler)
        self.is_running = True
        
        # Run the server in a separate thread
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info(f"Server started at http://localhost:{self.port}")
        return f"http://localhost:{self.port}"
        
    def stop(self) -> None:
        """
        Stop the server.
        """
        if not self.is_running:
            logger.warning("Server is not running")
            return
            
        # Close browser if open
        if self.browser:
            asyncio.create_task(self._close_browser())
        
        # Stop server    
        self.server.shutdown()
        self.server.server_close()
        self.is_running = False
        logger.info("Server stopped")
    
    async def open_in_chromium(self, headless: bool = False) -> None:
        """
        Open the server page in Chromium using Playwright.
        
        Args:
            headless: Whether to run the browser in headless mode
        """
        if not self.is_running:
            logger.error("Server is not running, cannot open browser")
            return
        
        logger.info("Opening server in Chromium browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser without viewport parameter
        self.browser = await self.playwright.chromium.launch(headless=headless, args=["--disable-web-security"])
        
        # Create context with dimensions based on OS
        # Measured in viewport pixels
        viewport_dimensions = {"width": 640, "height": 400} if platform.system() == "Darwin" else {"width": 700, "height": 475}
        
        self.context = await self.browser.new_context(
            viewport=viewport_dimensions,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # Navigate to the server
        await self.page.goto(f"http://localhost:{self.port}")
        
        # Adjust the window size precisely to fit the game
        await self.page.evaluate("""
        () => {
            // Make sure the page contains only the game with minimal margins
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            document.body.style.overflow = 'hidden';
        }
        """)
        
        logger.info("Browser opened successfully")
    
    async def _close_browser(self) -> None:
        """
        Close the browser if it's open.
        """
        if self.browser:
            await self.browser.close()
            self.browser = None
        
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        logger.info("Browser closed successfully")
        
    def _create_request_handler(self, 
                                game_url: str, 
                                custom_html: str = None, 
                                lite_mode: bool = False):
        """
        Create a custom request handler with the game URL.
        
        Args:
            game_url: URL to the js-dos game bundle
            
        Returns:
            A request handler class
        """
        class DOSGameHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                # Serve the index.html page for the root path
                if self.path == "/" or self.path == "/index.html":
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    
                    # Create the HTML content with the specified game URL
                    from src.consts import DOS_GAME_HTML_TEMPLATE, DOS_GAME_LITE_HTML_TEMPLATE

                    if custom_html:
                        html_content = custom_html
                    elif lite_mode:
                        html_content = DOS_GAME_LITE_HTML_TEMPLATE.format(game_url=game_url)
                    else:
                        html_content = DOS_GAME_HTML_TEMPLATE.format(game_url=game_url)
                    
                    self.wfile.write(html_content.encode())
                # Add handler for dosbox.conf
                elif self.path == "/dosbox.conf":
                    # Get the path to the dosbox.conf file
                    dosbox_conf_path = Path("src/dos/dosbox.conf")
                    
                    if dosbox_conf_path.exists():
                        self.send_response(200)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        
                        # Read and serve the dosbox.conf file
                        with open(dosbox_conf_path, 'rb') as f:
                            self.wfile.write(f.read())
                    else:
                        # If the file doesn't exist, return 404
                        self.send_response(404)
                        self.send_header("Content-type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"dosbox.conf file not found")
                        logger.error(f"dosbox.conf file not found at {dosbox_conf_path.absolute()}")
                else:
                    # For other paths, use the default behavior
                    super().do_GET()
                    
            def log_message(self, format, *args):
                # Customize logging to use our logger
                logger.debug(format % args)
                
        return DOSGameHandler 