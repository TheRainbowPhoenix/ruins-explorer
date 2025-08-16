import struct
import gc
import io

HDR_FMT = "<4sHHII"
HDR_SIZE = struct.calcsize(HDR_FMT)

def read_header(path):
    with io.open(path, 'rb') as f:
        print("BEFORE READ")
        b = f.read(HDR_SIZE)
        print("AFTER READ")
        if not isinstance(b, (bytes, bytearray)) or len(b) != HDR_SIZE:
            raise OSError("short read or not bytes")
        print("IS OK ???")
    magic, version, count, index_off, _ = struct.unpack(HDR_FMT, b)
    return magic, version, count, index_off

magic, version, count, index_off = read_header('gm/backgrounds.pak')
print(magic, version, count, index_off)
gc.collect()