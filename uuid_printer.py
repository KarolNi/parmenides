import uuid
import segno
import fpdf
from functools import lru_cache


config = {"dpi":100,
"margins":10,
"error":"H",
"spacing":0.5,
"font_size":5,
"orientation":"L",
"format":"A4",
}

def pt2mm(pt: float) -> float:
    return 0.35277777777778*pt

# size of cell

@lru_cache
def size_of_qr() -> [float, float]:
    qrcode = segno.make(int(0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF), error="H")  # 128 bit number
    qrimage = qrcode.to_pil()
    wqr = qrimage.width/(config["dpi"])*25.4
    hqr = qrimage.height/(config["dpi"])*25.4
    return [wqr, hqr]

@lru_cache
def size_of_text() -> [float, float]:
    pdf = fpdf.FPDF()
    pdf.set_font('courier', '', config["font_size"])
    wt = pdf.get_string_width("12345678")  # 8 glyphs
    ht = pt2mm(config["font_size"])
    return [wt, ht]

def size_of_cell() -> [float, float]:
    w = max(size_of_qr()[0],size_of_text()[0]) + config["spacing"]
    h = size_of_qr()[1] + size_of_text()[1] + config["spacing"]
    return [w, h]

# number of cells

def size_of_page() -> [float, float]:
    pdf = fpdf.FPDF(orientation=config["orientation"], unit="mm", format=config["format"])
    pdf.add_page()
    return [pdf.w, pdf.h]

@lru_cache
def size_of_printable() -> [float, float]:
    [w, h] = size_of_page()
    return [w - 2 * config["margins"], h - 2 * config["margins"]]

def number_of_cells() -> [int, int]:
    w = size_of_printable()[0] // size_of_cell()[0]
    h = size_of_printable()[1] // size_of_cell()[1]
    return [int(w), int (h)]

# table of uuids

print (number_of_cells())


pdf = fpdf.FPDF(orientation="L", unit="mm", format="A4")
pdf.add_page()
pdf.set_font('courier', '', 5)

x = 10
y = 10

pdf.line(config["margins"], config["margins"], config["margins"], pdf.h - config["margins"])

for i in range(1,10):

    uuid1 = uuid.uuid4()

    s = segno.make(uuid1.int, error="H")
    sp = s.to_pil()
    w = sp.width/(i*20)*25.4

    pdf.image(sp, x=x, y = y, w = w)
    pdf.text(x=x, y = y+w+2, txt = uuid1.hex[0:8]+"\t"+str(i*20))

    y = y+w+10

pdf.output("test_segno.pdf")
