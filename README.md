# costycnc-inkscape-1.0

put folder gcode in C:\Program Files\Inkscape\share\inkscape\extensions

C:\Users\stefa\AppData\Roaming\inkscape\extensions\costycnc-inkscape-1.0-main\costycnc-inkscape-1.0-main\gcode

How install extension https://www.youtube.com/watch?v=h5VVwxQjCg4

# costycnc-inkscape-1.0: G-Code Generator (`gcode.py`)

This script is part of **costycnc-inkscape-1.0** and provides functionality to convert vector graphics (SVG paths) into G-Code commands, suitable for CNC machining/plotting. The script reads path data, processes it, and outputs G-Code movements with configurable parameters.

---

## 🔍 What `gcode.py` Does

- Parses SVG path data (as input) and converts commands (move, line, curve) into CNC friendly G-Code.  
- Supports scaling, coordinate transformations, feed rate settings.  
- Handles “pen up / pen down” style commands (lift vs draw moves) to avoid unwanted travel marks.  
- Generates G-Code that can be used on CNC/plotter machines with X, Y axes (and possibly Z for lifting/drawing).  

---

## ⚙️ Key Features

- **Path data parsing**: takes SVG path definitions, including curves, and approximates them in small segments for G-Code.  
- **Scaling & unit conversion**: you can configure how input units are mapped to CNC machine units.  
- **Feed rate control**: allows specifying the speed at which tool moves while “drawing” vs while “traveling.”  
- **Lift mechanism**: moves the Z-axis (or “pen up”) during non-drawing moves to prevent dragging or marking unwanted lines.  

---

## 🛠️ How to Use

1. Install dependencies (if any)  
2. Prepare your SVG files with clean path elements  
3. Call `gcode.py` from command line, passing required parameters (e.g. input SVG, output G-Code, scale, feed rates)  
4. Inspect the resulting `.gcode` file with a simulator or send to CNC/plotter machine  

---

## 🔧 Configuration Options

Typical configurable settings include:

- **Scale factor**: to map SVG units (e.g. pixels or mm) to machine space  
- **Feed rates**: different speeds for drawing vs travel moves  
- **Pen up/down Z-axis values**: how much to lift Z or retract tool during non-drawing moves  
- **Curve segment resolution**: how finely curves are approximated by line segments  

---

## 📂 Example

Example usage might look like:

```bash
python gcode.py --input myvector.svg --output output.gcode \
```

🧠 Skills Highlighted

SVG Path parsing & vector math

G-Code generation & CNC toolpath logic

Python scripting & file I/O

Curve approximation techniques

Embedded style precision (scaling, feed rates, Z-axis control)

📄 License & Contribution

This script is part of the costycnc-inkscape-1.0 project. Feel free to fork, adapt, or improve. Pull requests welcome!

  --scale 0.1 --feed_draw 1000 --feed_travel 3000 --pen_up 5 --pen_down 0

