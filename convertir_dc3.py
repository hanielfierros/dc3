# -*- coding: utf-8 -*-
"""convertir_dc3.py — Convierte modelos AC3D (.ac) del Douglas DC-3 a glTF 2.0.
Genera dos salidas: exterior (dc3-exterior.gltf) y cabina (dc3-cockpit.gltf)."""
import os, re, json, struct, shutil

RAIZ = os.path.dirname(os.path.abspath(__file__))
TMP = r"C:\Users\hanie\AppData\Local\Temp\opencode\dc3_analysis\Douglas-Dc3-master"
LOG = os.path.join(RAIZ, "convertir_dc3.log")

def log(m):
    with open(LOG, "a", encoding="utf-8") as f: f.write(m + "\n")

# ---------------- tokenizador / parser AC3D ----------------
def tokenizar(texto):
    toks, i, n = [], 0, len(texto)
    while i < n:
        c = texto[i]
        if c.isspace(): i += 1; continue
        if c == '"':
            j = texto.find('"', i + 1); j = n if j < 0 else j
            toks.append(texto[i + 1:j]); i = j + 1; continue
        j = i
        while j < n and not texto[j].isspace(): j += 1
        toks.append(texto[i:j]); i = j
    return toks

class P:
    def __init__(self, t): self.t, self.i = t, 0
    def peek(self): return self.t[self.i] if self.i < len(self.t) else None
    def next(self): v = self.t[self.i]; self.i += 1; return v
    def f(self): return float(self.next())

def parse_surface(p):
    p.next(); flags = p.next()
    p.next(); mat = int(p.next())
    p.next(); n = int(p.next())
    refs = []
    for _ in range(n):
        vi = int(p.next()); u = float(p.next()); v = float(p.next())
        refs.append((vi, u, v))
    try: f = int(flags, 16)
    except ValueError: f = 0
    return {"mat": mat, "refs": refs, "twosided": bool(f & 0x02)}

def parse_object(p, tipo):
    o = {"tipo": tipo, "name": None, "loc": (0.0, 0.0, 0.0), "texture": None,
         "verts": [], "surfs": [], "kids": []}
    while p.peek() is not None:
        tok = p.next()
        if tok == "name": o["name"] = p.next()
        elif tok == "loc": o["loc"] = (p.f(), p.f(), p.f())
        elif tok == "texture": o["texture"] = p.next()
        elif tok == "texrep": p.f(); p.f()
        elif tok == "crease": p.next()
        elif tok == "rot": p.f(); p.f(); p.f(); p.f()
        elif tok == "numvert":
            n = int(p.next())
            o["verts"] = [[p.f(), p.f(), p.f()] for _ in range(n)]
        elif tok == "numsurf":
            n = int(p.next())
            o["surfs"] = [parse_surface(p) for _ in range(n)]
        elif tok == "kids":
            n = int(p.next())
            for _ in range(n):
                p.next(); t2 = p.next()
                o["kids"].append(parse_object(p, t2))
            return o
    return o

def parse_ac(content):
    p = P(tokenizar(content))
    if p.next() != "AC3Db": raise ValueError("no AC3D")
    materiales, raiz = [], None
    while p.peek() is not None:
        tok = p.next()
        if tok == "MATERIAL":
            p.next()  # nombre (quoted)
            p.next(); rgb = [p.f(), p.f(), p.f()]          # rgb
            p.next(); p.f(); p.f(); p.f()                   # amb
            p.next(); p.f(); p.f(); p.f()                   # emis
            p.next(); p.f(); p.f(); p.f()                   # spec
            p.next(); p.f()                                 # shi
            p.next(); trans = p.f()                         # trans
            materiales.append({"rgb": rgb, "trans": trans})
        elif tok == "OBJECT":
            raiz = parse_object(p, p.next())
    return materiales, raiz

# ---------------- geometría ----------------
def _k(v): return tuple(round(x, 5) for x in v)

def recoger(obj, mats, primitivas, con_texturas):
    if obj["verts"] and obj["surfs"]:
        verts = obj["verts"]
        vindex = {}; posiciones = []; uvs = []; nacc = {}; tris = []
        def add(pos, uv):
            pk = _k(pos); key = (pk, round(uv[0], 5), round(uv[1], 5))
            if key not in vindex:
                vindex[key] = len(posiciones)
                posiciones.append(pos); uvs.append(uv)
                nacc.setdefault(pk, [0.0, 0.0, 0.0])
            return vindex[key]
        for s in obj["surfs"]:
            refs = s["refs"]
            for a in range(1, len(refs) - 1):
                tri = (refs[0], refs[a], refs[a + 1])
                iv = [add(verts[vi], (u, 1.0 - v)) for (vi, u, v) in tri]
                p0, p1, p2 = posiciones[iv[0]], posiciones[iv[1]], posiciones[iv[2]]
                ux = p1[0]-p0[0]; uy = p1[1]-p0[1]; uz = p1[2]-p0[2]
                vx = p2[0]-p0[0]; vy = p2[1]-p0[1]; vz = p2[2]-p0[2]
                nx = uy*vz-uz*vy; ny = uz*vx-ux*vz; nz = ux*vy-uy*vx
                l = (nx*nx+ny*ny+nz*nz)**0.5 or 1.0
                nx, ny, nz = nx/l, ny/l, nz/l
                for vi in iv:
                    a2 = nacc[_k(posiciones[vi])]; a2[0]+=nx; a2[1]+=ny; a2[2]+=nz
                tris.append((iv[0], iv[1], iv[2], s["mat"], s["twosided"]))
        normales = []
        for pos in posiciones:
            a2 = nacc[_k(pos)]; l = (a2[0]**2+a2[1]**2+a2[2]**2)**0.5
            if l < 1e-9: normales.append([0.0, 1.0, 0.0])
            else: normales.append([a2[0]/l, a2[1]/l, a2[2]/l])
        grupos = {}
        for (a, b, c, mat, twos) in tris:
            grupos.setdefault((mat, obj["texture"], twos), []).append((a, b, c))
        for (mat, tex, twos), grp in grupos.items():
            idx = []
            for (a, b, c) in grp: idx += [a, b, c]
            color = mats[mat]["rgb"] if mat < len(mats) else [1, 1, 1]
            alpha = mats[mat]["trans"] if mat < len(mats) else 1.0
            primitivas.append({
                "nombre": obj["name"], "loc": obj["loc"], "pos": posiciones,
                "nor": normales, "uv": uvs, "idx": idx, "color": color,
                "alpha": alpha, "tex": tex if con_texturas else None, "twos": twos,
            })
    for k in obj["kids"]:
        recoger(k, mats, primitivas, con_texturas)

# ---------------- construir gltf ----------------
def construir(archivos, nombre, con_texturas, prefijo):
    primitivas = []
    texmap = {}
    for af in archivos:
        try:
            with open(af, encoding="utf-8", errors="replace") as fh:
                mats, raiz = parse_ac(fh.read())
        except Exception as e:
            log("ERROR parse %s: %s" % (af, e)); continue
        def reg(o):
            if o["texture"] and con_texturas:
                src = os.path.normpath(os.path.join(os.path.dirname(af), o["texture"]))
                if os.path.isfile(src) and o["texture"] not in texmap:
                    base = os.path.basename(src)
                    texmap[o["texture"]] = prefijo + re.sub(r"[^A-Za-z0-9_.-]+", "-", base)
            for k in o["kids"]: reg(k)
        reg(raiz)
        recoger(raiz, mats, primitivas, con_texturas)

    copiadas = set()
    for t, out in texmap.items():
        # encontrar el src real (recorrer de nuevo)
        for af in archivos:
            src = os.path.normpath(os.path.join(os.path.dirname(af), t))
            if os.path.isfile(src) and out not in copiadas:
                shutil.copyfile(src, os.path.join(RAIZ, out)); copiadas.add(out); break

    buf = bytearray()
    off = [[], [], [], []]
    for p in primitivas:
        off[0].append(len(buf)); buf += struct.pack("<%df" % (len(p["pos"])*3), *[c for v in p["pos"] for c in v])
        off[1].append(len(buf)); buf += struct.pack("<%df" % (len(p["nor"])*3), *[c for v in p["nor"] for c in v])
        off[2].append(len(buf)); buf += struct.pack("<%df" % (len(p["uv"])*2), *[c for v in p["uv"] for c in v])
        off[3].append(len(buf)); buf += struct.pack("<%dI" % len(p["idx"]), *p["idx"])
    while len(buf) % 4: buf += b"\x00"
    with open(os.path.join(RAIZ, nombre + ".bin"), "wb") as fh: fh.write(buf)

    bufferViews, accessors = [], []
    def add_bv(o, l, t):
        i = len(bufferViews); bufferViews.append({"buffer":0,"byteOffset":o,"byteLength":l,**({"target":t} if t else {})}); return i
    def add_acc(bvi, ct, cnt, comp, mn=None, mx=None):
        i = len(accessors); d = {"bufferView":bvi,"componentType":comp,"count":cnt,"type":ct}
        if mn is not None: d["min"]=mn; d["max"]=mx
        accessors.append(d); return i
    images, textures, materials = [], [], []
    samplers = [{"wrapS":10497,"wrapT":10497,"magFilter":9729,"minFilter":9987}]
    img_idx, tex_idx, mat_idx = {}, {}, {}
    meshes, nodes = [], []
    for i, p in enumerate(primitivas):
        np_ = len(p["pos"])
        bvP = add_bv(off[0][i], np_*12, 34962)
        bvN = add_bv(off[1][i], np_*12, 34962)
        bvU = add_bv(off[2][i], np_*8, 34962)
        bvI = add_bv(off[3][i], len(p["idx"])*4, 34963)
        mn = [min(v[0] for v in p["pos"]), min(v[1] for v in p["pos"]), min(v[2] for v in p["pos"])]
        mx = [max(v[0] for v in p["pos"]), max(v[1] for v in p["pos"]), max(v[2] for v in p["pos"])]
        aP = add_acc(bvP, "VEC3", np_, 5126, mn, mx)
        aN = add_acc(bvN, "VEC3", np_, 5126)
        aU = add_acc(bvU, "VEC2", np_, 5126)
        aI = add_acc(bvI, "SCALAR", len(p["idx"]), 5125)
        key = (tuple(round(c,4) for c in p["color"]), round(p["alpha"],4), p["tex"])
        if key not in mat_idx:
            d = {"doubleSided": True, "pbrMetallicRoughness":{"metallicFactor":0.0,"roughnessFactor":1.0}}
            if p["tex"] and p["tex"] in texmap:
                if p["tex"] not in img_idx:
                    img_idx[p["tex"]] = len(images); images.append({"uri": texmap[p["tex"]]})
                tk = img_idx[p["tex"]]
                if tk not in tex_idx:
                    tex_idx[tk] = len(textures); textures.append({"source":tk,"sampler":0})
                d["pbrMetallicRoughness"]["baseColorTexture"] = {"index": tex_idx[tk]}
            d["pbrMetallicRoughness"]["baseColorFactor"] = [p["color"][0], p["color"][1], p["color"][2], p["alpha"]]
            if p["alpha"] < 1.0: d["alphaMode"] = "BLEND"
            materials.append(d); mat_idx[key] = len(materials)-1
        meshes.append({"primitives":[{"attributes":{"POSITION":aP,"NORMAL":aN,"TEXCOORD_0":aU},"indices":aI,"material":mat_idx[key]}]})
        nd = {"mesh": i, "name": p["nombre"] or ("obj%d" % i)}
        if any(p["loc"]): nd["translation"] = list(p["loc"])
        nodes.append(nd)

    gltf = {
        "asset": {"version":"2.0","generator":"convertir_dc3.py"},
        "scene": 0, "scenes": [{"nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes, "accessors": accessors, "bufferViews": bufferViews,
        "buffers": [{"byteLength": len(buf), "uri": nombre + ".bin"}],
        "materials": materials,
    }
    if images: gltf["images"] = images
    if textures: gltf["textures"] = textures
    if samplers and textures: gltf["samplers"] = samplers
    with open(os.path.join(RAIZ, nombre + ".gltf"), "w", encoding="utf-8") as fh:
        json.dump(gltf, fh, ensure_ascii=False)
    log("%s: %d primitivas, %d vértices, %d triángulos, %d texturas, %.2f MB bin" % (
        nombre, len(primitivas), sum(len(p["pos"]) for p in primitivas),
        sum(len(p["idx"])//3 for p in primitivas), len(copiadas), len(buf)/1048576))

def main():
    if os.path.exists(LOG): os.remove(LOG)
    # Exterior (wireframe, sin texturas)
    ext = []
    for sub in ["dc-3.ac", "wheels.ac", "ailettes.ac", "floats.ac"]:
        ext.append(os.path.join(TMP, "Models", sub))
    for e in ["r1830.ac", "blocpiston.ac", "Propeller/propeller.ac"]:
        ext.append(os.path.join(TMP, "Models", "Engines", e))
    construir(ext, "dc3-exterior", con_texturas=False, prefijo="dc3x-")

    # Cabina (texturizada): Models/Interior completo
    int_files = []
    for dp, d, fs in os.walk(os.path.join(TMP, "Models", "Interior")):
        for f in fs:
            if f.lower().endswith(".ac"):
                int_files.append(os.path.join(dp, f))
    int_files.sort()
    construir(int_files, "dc3-cockpit", con_texturas=True, prefijo="dc3c-")

if __name__ == "__main__":
    main()
