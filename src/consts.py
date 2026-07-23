# Hold constants for game-playing agent

DOS_GAME_LITE_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>JS-DOS Game Player</title>
    
    <!-- js-dos style sheet -->
    <link rel="stylesheet" href="https://v8.js-dos.com/8.xx/8.3.14/js-dos.css">
    
    <!-- js-dos -->
    <script src="https://v8.js-dos.com/8.xx/8.3.14/js-dos.js"></script>
</head>
<body>
    <div id="dos" style="width: 640px; height: 400px;"></div>
    <script>
        const props = Dos(document.getElementById("dos"), {{
            url: "{game_url}",
            autoStart: true,
        }});
        
        let isDown = false;
        let lastToggleTime = 0;
        
        function togglePause(event) {{
            // Only respond to Shift+PageUp combination
            if (event.key === 'PageUp' && event.shiftKey) {{
                console.log("Toggle pause");
                // Simulate Alt keydown
                document.dispatchEvent(new KeyboardEvent('keydown', {{
                    key: 'Alt',
                    code: 'AltLeft',
                    bubbles: true
                }}));
                
                // Simulate Pause keydown
                document.dispatchEvent(new KeyboardEvent('keydown', {{
                    key: 'Pause',
                    code: 'Pause',
                    altKey: true,
                    bubbles: true
                }}));
                
            }}
        }}

        document.addEventListener('keydown', togglePause);
    </script>
</body>
</html>"""

DOS_GAME_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>JS-DOS Game Player</title>
    
    <!-- js-dos style sheet -->
    <link rel="stylesheet" href="https://v8.js-dos.com/8.xx/8.3.14/js-dos.css">
    
    <!-- js-dos -->
    <script src="https://v8.js-dos.com/8.xx/8.3.14/js-dos.js"></script>
</head>
<body>
    <div id="dos" style="width: 640px; height: 400px;"></div>
    <script>
        const props = Dos(document.getElementById("dos"), {{
            url: "{game_url}",
            autoStart: true,
        }});
    </script>
</body>
</html>"""

### Mapping from game name to game URL
GAME_URL_MAP = {
    "doom": "https://cdn.dos.zone/custom/dos/doom.jsdos",
    "doom2": "https://cdn.dos.zone/custom/dos/doom2.jsdos",
    "quake": "https://br.cdn.dos.zone/quakev2.levp.jsdos",
    "civ": "https://br.cdn.dos.zone/published/br.jzcdse.Civilization.jsdos",
    "warcraft2": "https://cdn.dos.zone/custom/dos/war2.jsdos",
    "oregon_trail": "https://cdn.dos.zone/original/2X/5/53e616496b4da1d95136e235ad90c9cc3f3f760d.jsdos",
    "x-com": "https://cdn.dos.zone/original/2X/3/373503784811ac8505dc2fcc3e241fc60493171a.jsdos",
    "incredible-machine": "https://cdn.dos.zone/custom/dos/incredible-machine.jsdos",
    "prince": "https://cdn.dos.zone/custom/crafted/princeofpersiaorigin.jsdos",
    "need_for_speed": "https://cdn.dos.zone/custom/dos/nfs.jsdos",
    "age_of_empires": "https://cdn.dos.zone/custom/dos/aoe-nic.jsdos",

    # Other games not in benchmark, add more as needed
    "aladdin": "aladdin",
    "wolfenstein": "wolfenstein",
    "comanche2": "comanche",
    "sim_city": "sim_city",
    "calibration": "calibration", # Used to calibrate mouse
    "diablo": "diablo",
    "comanche2": "https://br.cdn.dos.zone/published/br.ofuxch.comanch2 (1).jsdos",
}

# Mapping from game name to ROM file
ROM_FILE_MAP = {
    "pokemon_red": "pokemon_red.gb",
    "pokemon_crystal": "pokemon_crystal.gbc",
    "zelda": "zelda_links_awakening.gbc",
    "super_mario_land": "super_mario_land.gb",
    "kirby": "kirby_dream_land.gb",
    "mega_man": "mega_man_dr_wilys_revenge.gb",
    "donkey_kong": "donkey_kong_land_2.gb",
    "castlevania": "castlevania_the_adventure.gb",
    "scooby_doo": "scooby_doo_classic_creep_capers.gbc",
    # Add more ROM mappings as needed
}

# GBA keys
GBA_KEYS = ["A", "B", "START", "SELECT", "UP", "DOWN", "LEFT", "RIGHT"]

# Keyboard key reference for DOS games
KEYBOARD_KEYS = {
    # Letters
    "A": "KeyA", "B": "KeyB", "C": "KeyC", "D": "KeyD", "E": "KeyE",
    "F": "KeyF", "G": "KeyG", "H": "KeyH", "I": "KeyI", "J": "KeyJ",
    "K": "KeyK", "L": "KeyL", "M": "KeyM", "N": "KeyN", "O": "KeyO",
    "P": "KeyP", "Q": "KeyQ", "R": "KeyR", "S": "KeyS", "T": "KeyT",
    "U": "KeyU", "V": "KeyV", "W": "KeyW", "X": "KeyX", "Y": "KeyY", "Z": "KeyZ",
    
    # Numbers
    "0": "Digit0", "1": "Digit1", "2": "Digit2", "3": "Digit3", "4": "Digit4",
    "5": "Digit5", "6": "Digit6", "7": "Digit7", "8": "Digit8", "9": "Digit9",
    
    # Function keys
    "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5",
    "F6": "F6", "F7": "F7", "F8": "F8", "F9": "F9", "F10": "F10",
    "F11": "F11", "F12": "F12",
    
    # Arrow keys
    "LEFT": "ArrowLeft", "RIGHT": "ArrowRight", "UP": "ArrowUp", "DOWN": "ArrowDown",
    
    # Special keys
    "ENTER": "Enter", "ESC": "Escape", "TAB": "Tab", "SPACE": "Space",
    "BACKSPACE": "Backspace", "DELETE": "Delete", "INSERT": "Insert",
    "HOME": "Home", "END": "End", "PAGEUP": "PageUp", "PAGEDOWN": "PageDown",
    
    # Modifier keys
    "CTRL": "Control", "ALT": "Alt", "SHIFT": "Shift", "META": "Meta",
    
    # Common combinations
    "CTRL+C": "Control+KeyC", "CTRL+V": "Control+KeyV", "CTRL+X": "Control+KeyX",
    "CTRL+A": "Control+KeyA", "CTRL+Z": "Control+KeyZ", "CTRL+S": "Control+KeyS",
    "ALT+F4": "Alt+F4", "CTRL+ALT+DEL": "Control+Alt+Delete"
}

NO_OP_SKIP_FRAMES = 120
