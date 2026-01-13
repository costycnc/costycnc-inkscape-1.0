import inkex
from inkex import bezier
import math
import os
from datetime import datetime
import serial
import sys


class CostyCNC(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--feedrate", type=int, default=500)
        pars.add_argument("--temperature", type=int, default=1000)
        pars.add_argument("--port", type=str, default="COM4")
        pars.add_argument("--dpi", type=float, default=96)  # richiesto da Inkscape


    def effect(self):

        if len(self.svg.selected) < 1:
            self.msg("Seleziona almeno un path")
            return

        # ====== ESTRAZIONE PERCORSI ======
        all_paths = []

        for el in self.svg.selected:

            path = el.path.transform(el.composed_transform())
            csp = path.to_superpath()
            bezier.cspsubdiv(csp, 0.5)

            for sub in csp:
                pts = [(seg[0][0], seg[0][1]) for seg in sub]
                if len(pts) > 1:
                    all_paths.append(pts)

        if not all_paths:
            self.msg("Nessun punto trovato")
            return

        # ====== UNIONE PATH (NEAREST NEIGHBOR) ======
        pathx = [all_paths[0][0]]
        paths = all_paths.copy()

        while paths:
            minDist = sys.maxsize

            for i, d in enumerate(pathx):
                for pi, p in enumerate(paths):
                    for ni, pt in enumerate(p):
                        dist = math.dist(d, pt)
                        if dist < minDist:
                            minDist = dist
                            insert_pos = i
                            path_idx = pi
                            node_idx = ni

            p = paths.pop(path_idx)
            p = p[node_idx:] + p[:node_idx]

            if p[0] != p[-1]:
                p.append(p[0])

            pathx = pathx[:insert_pos] + [pathx[insert_pos]] + p + pathx[insert_pos:]

        # ====== BOUNDING BOX ======
        xs = [p[0] for p in pathx]
        ys = [p[1] for p in pathx]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width_mm  = self.svg.uutounit(max_x - min_x, 'mm')
        height_mm = self.svg.uutounit(max_y - min_y, 'mm')

        self.msg(f"(Dimension X={width_mm:.2f}mm Y={height_mm:.2f}mm)")

        # ====== GCODE ======
        gcode = []
        gcode.append("G21")
        gcode.append("G90")
        gcode.append(f"F{self.options.feedrate}")
        gcode.append("G92 X0 Y0")
        gcode.append(f"M03 S{self.options.temperature}")

        first = True
        for x, y in pathx:
            x_mm = self.svg.uutounit(x - min_x, 'mm')
            y_mm = self.svg.uutounit(y - min_y, 'mm')

            if first:
                gcode.append(f"G00 X{x_mm:.3f} Y{y_mm:.3f}")
                first = False
            else:
                gcode.append(f"G01 X{x_mm:.3f} Y{y_mm:.3f}")

        gcode.append("G01 X0 Y0")
        gcode.append("M05")

        gcode_str = "\n".join(gcode)

        # ====== SALVATAGGIO ======
        outdir = os.path.expanduser("~/documents/costycnc/")
        os.makedirs(outdir, exist_ok=True)

        fname = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".nc"
        fpath = os.path.join(outdir, fname)

        with open(fpath, "w") as f:
            f.write(gcode_str)

        self.msg(f"(Salvato: {fpath})")
        self.msg(gcode_str)

        # ====== INVIO A GRBL ======
        try:
            ser = serial.Serial(self.options.port, 115200, timeout=1)
            ser.readline()
            ser.readline()

            for line in gcode:
                ser.write((line + "\n").encode())
                ser.readline()

            ser.close()

        except Exception as e:
            self.msg(f"Errore seriale: {e}")


if __name__ == '__main__':
    CostyCNC().run()

