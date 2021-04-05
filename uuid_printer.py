import uuid
import segno
import fpdf

config = {"dpi":72}

pdf = fpdf.FPDF(orientation="P", unit="mm", format="A4")
pdf.add_page()
pdf.set_font('courier', '', 5)

x = 10
y = 10
for i in range(1,10):

    uuid1 = uuid.uuid4()

    s = segno.make(uuid1.int)
    sp = s.to_pil()
    w = sp.width/(i*20)*25.4

    pdf.image(sp, x=x, y = y, w = w)
    pdf.text(x=x, y = y+w+2, txt = uuid1.hex[0:8]+"\t"+str(i*20))

    y = y+w+10

pdf.output("test_segno.pdf")
