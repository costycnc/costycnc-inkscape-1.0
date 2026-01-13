import inkex
from inkex import bezier
import math
import os
import sys
from datetime import datetime
import serial


class CostyCNC(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--feedrate", type=int, default=500)
        pars.add_argument("--temperature", type=int, default=1000)
        pars.add_argument("--port", type=str, default="COM4")
        pars.add_argument("--dpi", type=float, default=96)  # richiesto da Inkscape
        pars.add_argument("--subdivision", type=float, default=0.1, help="Precisione contorno (linee corte=più dettagli)")

    def effect(self):

        if len(self.svg.selected) == 0:
            self.msg("Seleziona almeno un path")
            return

        # =========================================================
        # 1) ESTRAZIONE DI TUTTI I PATH (con trasformazioni)
        # =========================================================
        all_paths = []

        for el in self.svg.selected:
            path = el.path.transform(el.composed_transform())
            csp = path.to_superpath()
            bezier.cspsubdiv(csp, self.options.subdivision)  # <-- parametro dinamico

            for sub in csp:
                pts = [(seg[0][0], seg[0][1]) for seg in sub]
                if len(pts) > 1:
                    all_paths.append(pts)

        if not all_paths:
            self.msg("Nessun punto valido trovato")
            return

        # =========================================================
        # 2) SCELTA DEL MIGLIOR INGRESSO (più vicino a 0,0)
        # =========================================================
        origin = (0, 0)
        minDist = sys.maxsize

        for pi, p in enumerate(all_paths):
            for ni, pt in enumerate(p):
                d = math.dist(origin, pt)
                if d < minDist:
                    minDist = d
                    start_path_idx = pi
                    start_node_idx = ni

        first_path = all_paths.pop(start_path_idx)
        first_path = first_path[start_node_idx:] + first_path[:start_node_idx]

        if first_path[0] != first_path[-1]:
            first_path.append(first_path[0])

        pathx = first_path[:]
        paths = all_paths[:]

        # =========================================================
        # 3) UNIONE DI TUTTI I PATH (nearest-neighbor)
        # =========================================================
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

        # =========================================================
        # 4) BOUNDING BOX E TRASLAZIONE A (0,0)
        # =========================================================
        xs = [p[0] for p in pathx]
        ys = [p[1] for p in pathx]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width_mm  = self.svg.uutounit(max_x - min_x, 'mm')
        height_mm = self.svg.uutounit(max_y - min_y, 'mm')

        self.msg(f"(Dimension X={width_mm:.2f}mm Y={height_mm:.2f}mm)")

        # =========================================================
        # 5) GENERAZIONE GCODE
        # =========================================================
        gcode = []
        gcode.append("G21")                      # mm
        gcode.append("G90")                      # assoluto
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

        # =========================================================
        # 6) SALVATAGGIO FILE
        # =========================================================
        outdir = os.path.expanduser("~/documents/costycnc/")
        os.makedirs(outdir, exist_ok=True)

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".nc"
        filepath = os.path.join(outdir, filename)

        with open(filepath, "w") as f:
            f.write(gcode_str)

        self.msg(f"(Salvato: {filepath})")
        self.msg(gcode_str)

        # =========================================================
        # 7) INVIO A GRBL (opzionale)
        # =========================================================
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
