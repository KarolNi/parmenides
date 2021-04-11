import uuid
import segno
from functools import lru_cache
from typing import List
import sourcerandom
import os
import hashlib
import svgutils.transform


def pt2mm(pt: float) -> float:
    return 0.35277777777778*pt

def mm2px(mm: float) -> float:
    return 96 / 25.4 * mm

def px2mm(mm: float) -> float:
    return 25.4 / 96 * mm

A4 = [mm2px(297), mm2px(210)]

config = {
#"dpi":100,
"margins":mm2px(10),
"error":"H",
#"spacing":0.5,
"font_size":5,
#"orientation":"L",
#"format":"A4",
}

@lru_cache
def size_of_cell() -> [float, float]:
    qrcode = segno.make(int(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF), error=config["error"])  # 128 bit number
    qr_svg = svgutils.transform.fromstring(qrcode.svg_inline())
    w, h = qr_svg.get_size()
    wqr = float(w)
    hqr = float(h)
    w = wqr
    h = hqr + config["font_size"]
    return [w, h]

@lru_cache
def size_of_printable() -> [float, float]:
    w, h = A4
    return [w - 2 * config["margins"], h - 2 * config["margins"]]

def number_of_cells() -> [int, int]:
    w = size_of_printable()[0] // size_of_cell()[0]
    h = size_of_printable()[1] // size_of_cell()[1]
    return [int(w), int (h)]

# table of uuids

def ndim_iterate(data, func):
    try:
        for item in data:
            ndim_iterate(item,func)
    except TypeError:
        func(data)

def better_uuid4():
    qrng = sourcerandom.SourceRandom(source=sourcerandom.OnlineRandomnessSource.QRNG_ANU)  # TODO static it somehow
    tumbler = hashlib.blake2b(digest_size=16)
    tumbler.update(os.urandom(16))
    tumbler.update(qrng.randint(0,0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF).to_bytes(16,'big'))
    ret = uuid.UUID(bytes=tumbler.digest(),version=4)
    return ret


def array_of_uuids(dimensions: List[int]):
    ret = list()
    for i in range(dimensions[0]):
        ret.append(list())
        for j in range(dimensions[1]):
            ret[i].append(uuid.uuid4())  # better_uuid4()
    return ret

def draw_cell(data):
    qrcode = segno.make(data.int, error=config["error"])
    qr_svg = svgutils.transform.fromstring(qrcode.svg_inline())
    w, h = qr_svg.get_size()
    wqr = float(w)
    hqr = float(h)
    w = wqr
    h = hqr + config["font_size"]
    qr_element = qr_svg.getroot()
    text_element = svgutils.transform.TextElement(wqr/2., hqr + config["font_size"] - 1, data.hex[0:8], size=config["font_size"], anchor="middle", font="OCR A Extended")
    line_element = svgutils.transform.LineElement([[0, 0], [w, 0], [w, h], [0, h], [0, 0]])
    line_element.root.attrib["style"] = "fill:none"
    return svgutils.transform.GroupElement([qr_element, text_element, line_element])

def main():
    fig = svgutils.transform.SVGFigure()
    size = [str(A4[0]),str(A4[1])]
    fig.set_size(size)

    uuids = array_of_uuids(number_of_cells())
    for i, row in enumerate(uuids):
        for j, cell in enumerate(row):
            cell_element = draw_cell(cell)
            w, h = size_of_cell()
            cell_element.moveto(w * i + config["margins"], h * j + config["margins"])
            fig.append([cell_element])
    fig.save("test_qr.svg")

if __name__ == "__main__":
    main()
