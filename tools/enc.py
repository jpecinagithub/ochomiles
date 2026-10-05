"""Codificadores binarios para datos-base.js / datos-picos.js. Ver SCHEMA.md."""
import base64


def _leb128_encode(n: int) -> bytes:
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break
    return bytes(out)


def _zigzag(d: int) -> int:
    return ((d << 1) ^ (d >> 31)) & 0xFFFFFFFF


def enc_ints(vals) -> str:
    """Lista de enteros con signo -> base64 (delta + zigzag + LEB128)."""
    vals = list(vals)
    out = bytearray()
    prev = 0
    for i, v in enumerate(vals):
        d = v if i == 0 else v - prev
        out += _leb128_encode(_zigzag(d))
        prev = v
    return base64.b64encode(bytes(out)).decode("ascii")


def enc_u8(data: bytes) -> str:
    return base64.b64encode(bytes(data)).decode("ascii")


def enc_lines(lines) -> str:
    """Lista de polilíneas [[(lon,lat),...],...] -> base64.
    Unidades internas: microgrados enteros."""
    ints = []
    px = py = 0
    for line in lines:
        ints.append(len(line))
        for lon, lat in line:
            x = int(round(lon * 1e6))
            y = int(round(lat * 1e6))
            ints.append(x - px)
            ints.append(y - py)
            px, py = x, y
    return enc_ints(ints)


# ---------- decodificadores (solo para verificación) ----------

def _leb128_decode(buf: bytes):
    vals = []
    i = 0
    n = len(buf)
    while i < n:
        shift = 0
        res = 0
        while True:
            b = buf[i]
            i += 1
            res |= (b & 0x7F) << shift
            shift += 7
            if not (b & 0x80):
                break
        vals.append(res)
    return vals


def dec_ints(s: str):
    raw = _leb128_decode(base64.b64decode(s))
    out = []
    acc = 0
    for z in raw:
        d = (z >> 1) ^ -(z & 1)
        acc += d
        out.append(acc)
    return out


def dec_lines(s: str):
    ints = dec_ints(s)
    lines = []
    k = 0
    x = y = 0
    while k < len(ints):
        n = ints[k]
        k += 1
        line = []
        for _ in range(n):
            x += ints[k]
            y += ints[k + 1]
            k += 2
            line.append((x / 1e6, y / 1e6))
        lines.append(line)
    return lines
