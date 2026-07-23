from typing import Dict, Any, List, Tuple, Optional
from abc import ABC, abstractmethod
from PIL import Image

class VideoGameBenchInterface(ABC):
    """Base interface class for video game emulation benchmarks."""
    
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def load_game(self, *args, **kwargs) -> bool:
        """Load a game from the specified path."""
        pass

    @abstractmethod
    async def step(self, *args, **kwargs) -> Tuple[str, List[bytes]]:
        """Execute an action and return the observation."""
        pass

    @abstractmethod
    async def close(self, *args, **kwargs) -> None:
        """Clean up resources."""
        pass

    @abstractmethod
    async def get_observation(self, *args, **kwargs) -> Optional[Dict[str, Any]]:
        """Get current game state observation."""
        pass
