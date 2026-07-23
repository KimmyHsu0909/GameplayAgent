import tkinter as tk
from tkinter import ttk
import sv_ttk
from typing import List, Optional
from datetime import datetime
from PIL import ImageGrab

ascii_art = """
██╗   ██╗ ██████╗        █████╗  ██████╗ ███████╗███╗   ██╗████████╗
██║   ██║██╔════╝       ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝
██║   ██║██║  ███╗█████╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   
╚██╗ ██╔╝██║   ██║╚════╝██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   
 ╚████╔╝ ╚██████╔╝      ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   
  ╚═══╝   ╚═════╝       ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   """

class AgentMonitorUI:
    def __init__(self, title: str = "LLM Agent Thoughts", screen_recorder=None):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x950")  # Made taller to accommodate checkpoints
        
        # Configure dark theme colors
        self.colors = {
            'bg': '#1e1e1e',        # Dark background
            'text': '#ffffff',       # White text
            'frame': '#2d2d2d',      # Slightly lighter background for frames
            'highlight': '#3d3d3d',  # Highlight color for active elements
            'accent': '#007acc'      # Blue accent color
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['bg'])
        
        # Add ASCII art at the top
        
        ascii_label = tk.Label(
            self.root,
            text=ascii_art,
            font=('Courier', 8),  # Monospace font for ASCII art
            bg=self.colors['bg'],
            fg=self.colors['accent'],
            justify=tk.LEFT
        )
        ascii_label.pack(pady=(5, 0))
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('default')  # Reset theme to ensure consistent styling
        
        # Configure all frame elements to use dark theme
        self.style.configure('Dark.TFrame', background=self.colors['bg'])
        self.style.configure('Dark.TLabelframe', 
                           background=self.colors['frame'],
                           padding=10,
                           borderwidth=2)
        
        # Configure the label (title) part of the labelframe with larger font
        self.style.configure('Dark.TLabelframe.Label', 
                           background=self.colors['frame'],
                           foreground=self.colors['text'],
                           font=('Arial', 14, 'bold'))  # Increased from 12 to 14
        
        # Additional styling for nested elements
        self.style.map('Dark.TLabelframe', 
                      background=[('active', self.colors['frame'])])
        self.style.map('Dark.TLabelframe.Label', 
                      background=[('active', self.colors['frame'])])
        
        # Configure scrollbar style
        self.style.configure('Dark.Vertical.TScrollbar',
                           background=self.colors['frame'],
                           arrowcolor=self.colors['text'],
                           bordercolor=self.colors['frame'],
                           troughcolor=self.colors['bg'])
        
        self.style.configure('Dark.TButton', 
                           background=self.colors['accent'],
                           foreground=self.colors['text'],
                           padding=5)
        
        # Create main container
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Context History Section
        self.history_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Context History",
            style='Dark.TLabelframe'
        )
        self.history_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.history_text, self.history_frame_frame = self._create_text_widget(self.history_frame, height=15)
        
        # Last Action Section
        self.action_frame = ttk.LabelFrame(
            self.main_frame,
            text="Last Action",
            style='Dark.TLabelframe'
        )
        self.action_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.action_text, self.action_frame_frame = self._create_text_widget(self.action_frame, height=4)
        
        # Currently Executing Action Section
        self.executing_frame = ttk.LabelFrame(
            self.main_frame,
            text="Currently Executing Action",
            style='Dark.TLabelframe'
        )
        self.executing_frame.pack(fill=tk.X, pady=(0, 10))
        self.executing_text, self.executing_frame_frame = self._create_text_widget(self.executing_frame, height=2)
        
        # Steps Counter Section
        self.steps_frame = ttk.LabelFrame(
            self.main_frame,
            text="Steps Taken",
            style='Dark.TLabelframe'
        )
        self.steps_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.steps_text, self.steps_frame_frame = self._create_text_widget(self.steps_frame, height=1)
        
        # Add Cost Section (after Steps Counter section)
        self.cost_frame = ttk.LabelFrame(
            self.main_frame,
            text="Total Cost",
            style='Dark.TLabelframe'
        )
        self.cost_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.cost_text, self.cost_frame_frame = self._create_text_widget(self.cost_frame, height=1)
        
        # Initialize steps counter
        self.steps_count = 0
        self.update_steps_count(0)  # Initialize display with 0
        
        # Initialize cost display
        self.update_cost(0.0)  # Initialize display with $0.00
        
        # Reflection Memory Section
        self.reflection_frame = ttk.LabelFrame(
            self.main_frame,
            text="Reflection Memory",
            style='Dark.TLabelframe'
        )
        self.reflection_frame.pack(fill=tk.BOTH, expand=True)
        
        self.reflection_text, self.reflection_frame_frame = self._create_text_widget(self.reflection_frame, height=10)
        
        # Add Checkpoints Section (after Reflection Memory section)
        self.checkpoints_frame = ttk.LabelFrame(
            self.main_frame,
            text="Checkpoints",
            style='Dark.TLabelframe'
        )
        self.checkpoints_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Container for checkpoint boxes
        self.checkpoint_container = ttk.Frame(self.checkpoints_frame, style='Dark.TFrame')
        self.checkpoint_container.pack(fill=tk.X, padx=5, pady=5)
        
        # Initialize empty checkpoint display
        self.checkpoint_boxes = []
        self.checkpoint_labels = []
        
        # Add screen recorder
        self.game_instance = None
        
        # Add recording controls
        self.recording_frame = tk.Frame(
            self.root,
            bg=self.colors['bg']
        )
        self.recording_frame.pack(fill=tk.X, padx=5, pady=5)
        
        sv_ttk.set_theme("dark")
        self.root.update_idletasks()
        self.root.update()

    def _create_text_widget(self, parent, height=10):
        """Create a styled text widget."""
        # Create a frame to hold both the text widget and scrollbar
        frame = ttk.Frame(parent, style='Dark.TFrame')
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbar first
        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            style='Dark.Vertical.TScrollbar'
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create text widget
        text_widget = tk.Text(
            frame,
            height=height,
            wrap=tk.WORD,
            bg=self.colors['bg'],
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['text'],
            font=('Consolas', 10),
            padx=5,
            pady=5,
            relief=tk.FLAT,
            borderwidth=0,
            yscrollcommand=scrollbar.set  # Connect to scrollbar
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbar to text widget
        scrollbar.config(command=text_widget.yview)
        
        return text_widget, frame

    def update_context_history(self, history: List[dict]) -> None:
        """Update the context history display."""
        try:
            self.history_text.delete(1.0, tk.END)
            for message in history:
                # Handle Message objects from context_history
                if hasattr(message, 'role') and hasattr(message, 'content'):
                    if isinstance(message.content, list):
                        content = ' '.join([item.get('text', '') for item in message.content 
                                         if item.get('type') == 'text'])
                    else:
                        content = str(message.content)
                    self._insert_formatted_message(self.history_text, message.role, content)
                # Handle dictionary format
                elif isinstance(message, dict):
                    content = message.get('content', '')
                    role = message.get('role', '')
                    self._insert_formatted_message(self.history_text, role, content)
            
            self.history_text.see(tk.END)
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating context history: {e}")

    def _insert_formatted_message(self, text_widget, role, content):
        """Insert a formatted message into the text widget."""
        text_widget.insert(tk.END, f"{role}: ", "role")
        text_widget.insert(tk.END, f"{content}\n", "content")
        # Configure tags for different text styles
        text_widget.tag_configure("role", foreground=self.colors['accent'])
        text_widget.tag_configure("content", foreground=self.colors['text'])

    def update_last_action(self, action: str) -> None:
        """Update the last action display."""
        try:
            self.action_text.delete(1.0, tk.END)
            self.action_text.insert(tk.END, action)
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating last action: {e}")

    def update_executing_action(self, action: str) -> None:
        """Update the currently executing action display."""
        try:
            self.executing_text.delete(1.0, tk.END)
            self.executing_text.insert(tk.END, action)
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating executing action: {e}")

    def update_steps_count(self, count: Optional[int] = None) -> None:
        """Update the steps counter display."""
        try:
            if count is not None:
                self.steps_count = count
            self.steps_text.delete(1.0, tk.END)
            self.steps_text.insert(tk.END, f"Total steps: {self.steps_count}")
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating steps count: {e}")

    def update_cost(self, cost: float) -> None:
        """Update the total cost display."""
        try:
            self.cost_text.delete(1.0, tk.END)
            self.cost_text.insert(tk.END, f"Total cost: ${cost:.2f}")
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating cost: {e}")

    def update_reflection_memory(self, memory: str) -> None:
        """Update the reflection memory display."""
        try:
            self.reflection_text.delete(1.0, tk.END)
            self.reflection_text.insert(tk.END, memory)
            self.root.update_idletasks()
            self.root.update()
        except Exception as e:
            print(f"Error updating reflection memory: {e}")

    def take_screenshot(self, path: str, name: str) -> None:
        """Take a screenshot of the UI window."""
        try:
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            screenshot.save(f"{path}/{name}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")

    def setup_checkpoints(self, num_checkpoints: int):
        """Set up the checkpoint display boxes."""
        # Clear existing checkpoints if any
        for box in self.checkpoint_boxes:
            box.destroy()
        for label in self.checkpoint_labels:
            label.destroy()
        self.checkpoint_boxes = []
        self.checkpoint_labels = []
        
        # Create new checkpoint boxes
        for i in range(num_checkpoints):
            frame = ttk.Frame(self.checkpoint_container, style='Dark.TFrame')
            frame.pack(side=tk.LEFT, padx=5)
            
            # Create number label first
            label = tk.Label(
                frame,
                text=str(i + 1),
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Consolas', 8)
            )
            label.pack(side=tk.BOTTOM)
            
            # Create checkbox (using Text widget for better styling control)
            box = tk.Text(
                frame,
                width=1,
                height=1,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                font=('Consolas', 12),
                relief=tk.SOLID,
                borderwidth=1,
                padx=2
            )
            box.pack(side=tk.BOTTOM, pady=(0, 2))
            box.tag_configure("center", justify='center')
            box.tag_configure("completed", foreground="#00ff00")  # Add green color tag
            box.insert('1.0', '□', "center")
            box.configure(state='disabled')
            
            self.checkpoint_boxes.append(box)
            self.checkpoint_labels.append(label)

    def update_checkpoint(self, index: int, completed: bool = True):
        """Update the status of a specific checkpoint (1-indexed)."""
        if 0 < index <= len(self.checkpoint_boxes):
            box = self.checkpoint_boxes[index-1]
            box.configure(state='normal')
            box.delete('1.0', tk.END)
            tags = ("center", "completed") if completed else ("center",)  # Apply both tags for completed checkmarks
            box.insert('1.0', 'X' if completed else '□', tags)
            box.configure(state='disabled')
            self.root.update_idletasks()
            self.root.update()