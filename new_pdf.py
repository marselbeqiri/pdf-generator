from io import StringIO, BytesIO

from reportlab.graphics.shapes import Line, Drawing
from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import LETTER, inch, A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


class Canvas(canvas.Canvas):
    TOP_IMAGE_LEFT = None
    TOP_IMAGE_RIGHT = None

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = LETTER

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if self._pageNumber > 1:
                self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page = "Page %s of %s" % (self._pageNumber, page_count)
        x = 128
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.drawImage(self.TOP_IMAGE_RIGHT, self.width - inch * 8 - 5, self.height - 50, width=100, height=20,
                       preserveAspectRatio=True)
        self.drawImage(self.TOP_IMAGE_LEFT, self.width - inch * 2, self.height - 50, width=100, height=30,
                       preserveAspectRatio=True, mask='auto')
        self.line(30, 740, LETTER[0] - 50, 740)
        self.line(66, 78, LETTER[0] - 66, 78)
        self.setFont('Times-Roman', 10)
        self.drawString(LETTER[0] - x, 65, page)
        self.restoreState()


class PdfGenerator:
    PAGE_SIZE = A5
    APP_NAME = 'App name'
    TABLE_TITLE = 'Report'
    TABLE_HEADER_TITLES = ["No.", "Col.1", "Col.2", "Col.3", "Col.4"]
    DATA_COLUMNS_NAMES = ['id', 'name', 'email', 'phone', 'address']
    # Required: Specify for each column table have
    TABLE_ALIGN_STYLE = [
        ParagraphStyle(name="01", alignment=TA_CENTER),
        ParagraphStyle(name="02", alignment=TA_LEFT),
        ParagraphStyle(name="03", alignment=TA_CENTER),
        ParagraphStyle(name="04", alignment=TA_CENTER),
        ParagraphStyle(name="05", alignment=TA_CENTER)
    ]
    # Specify for each column table have or None
    COLUMN_WIDTHS = [50, 200, 80, 80, 80]
    # Need to have as many items as table have columns
    TOTAL_ROW_CONTENT = ["Total", "", "", "", "Your total results"]

    TOP_IMAGE_LEFT = 'static/sample-1.png'
    TOP_IMAGE_RIGHT = 'static/sample-2.jfif'

    def __init__(self, path, data_records):
        custom_canvas = Canvas
        custom_canvas.TOP_IMAGE_LEFT = self.TOP_IMAGE_LEFT
        custom_canvas.TOP_IMAGE_RIGHT = self.TOP_IMAGE_RIGHT
        # Same length
        has_same_length = len(self.TABLE_HEADER_TITLES) == len(self.TABLE_ALIGN_STYLE) == \
                          len(self.TOTAL_ROW_CONTENT) == len(self.DATA_COLUMNS_NAMES)
        assert has_same_length, 'You forgot to set the same element length in TABLE_HEADER_TITLES, TABLE_ALIGN_STYLE, ' \
                                'COLUMN_WIDTHS, TOTAL_ROW_CONTENT '

        self.path = path
        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        # colors
        self.colorGreen0 = Color((45.0 / 255), (166.0 / 255), (153.0 / 255), 1)
        self.colorGreen1 = Color((182.0 / 255), (227.0 / 255), (166.0 / 255), 1)
        self.colorGreen2 = Color((140.0 / 255), (222.0 / 255), (192.0 / 255), 1)

        self.colorBlue0 = Color((54.0 / 255), (122.0 / 255), (179.0 / 255), 1)
        self.colorBlue1 = Color((122.0 / 255), (180.0 / 255), (225.0 / 255), 1)
        self.colorGreenLines = Color((50.0 / 255), (140.0 / 255), (140.0 / 255), 1)

        self.page_title()
        self.set_table(data_records)
        # Build
        self.doc = SimpleDocTemplate(path, pagesize=LETTER)
        self.doc.multiBuild(self.elements, canvasmaker=custom_canvas)

    def page_title(self):
        psHeaderText = ParagraphStyle('Hed0', fontSize=16, alignment=TA_LEFT, borderWidth=3,
                                      textColor=self.colorGreen0)
        text = self.APP_NAME
        paragraphReportHeader = Paragraph(text, psHeaderText)
        self.elements.append(paragraphReportHeader)

        spacer = Spacer(10, 10)
        self.elements.append(spacer)

        d = Drawing(500, 1)
        line = Line(-15, 0, 483, 0)
        line.strokeColor = self.colorGreenLines
        line.strokeWidth = 2
        d.add(line)
        self.elements.append(d)

        spacer = Spacer(10, 1)
        self.elements.append(spacer)

        d = Drawing(500, 1)
        line = Line(-15, 0, 483, 0)
        line.strokeColor = self.colorGreenLines
        line.strokeWidth = 0.5
        d.add(line)
        self.elements.append(d)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)

    def set_table(self, table_data):
        header_paragraph_style = ParagraphStyle('Hed0', fontSize=12, alignment=TA_LEFT, borderWidth=3,
                                                textColor=self.colorBlue0)
        text = self.TABLE_TITLE
        header_paragraph = Paragraph(text, header_paragraph_style)
        self.elements.append(header_paragraph)

        spacer = Spacer(10, 22)
        self.elements.append(spacer)

        table_head = []
        table_header_titles = self.TABLE_HEADER_TITLES

        font_size = 8
        centered_style = ParagraphStyle(name="centered", alignment=TA_CENTER)
        for text in table_header_titles:
            paragraph_text = "<font size='%s'><b>%s</b></font>" % (font_size, text)
            title = Paragraph(paragraph_text, centered_style)
            table_head.append(title)

        table = [table_head]

        row_no = 1
        formatted_row_data = []

        table_align_style = self.TABLE_ALIGN_STYLE

        # Table body content

        for row in table_data:
            row_data = [getattr(row, field) for field in self.DATA_COLUMNS_NAMES]
            column_number = 0

            for item in row_data:
                paragraph_text = "<font size='%s'>%s</font>" % (font_size - 1, item)
                paragraph = Paragraph(paragraph_text, table_align_style[column_number])

                formatted_row_data.append(paragraph)
                column_number = column_number + 1

            table.append(formatted_row_data)
            formatted_row_data = []

        # Row for total
        total_row = self.TOTAL_ROW_CONTENT
        for item in total_row:
            paragraph_text = "<font size='%s'>%s</font>" % (font_size - 1, item)
            p = Paragraph(paragraph_text, table_align_style[1])
            formatted_row_data.append(p)
        table.append(formatted_row_data)

        full_table = Table(table, colWidths=self.COLUMN_WIDTHS) if self.COLUMN_WIDTHS else Table(table)

        table_style = TableStyle(
            [  # ('GRID',(0, 0), (-1, -1), 0.5, grey),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                # ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ("ALIGN", (1, 0), (1, -1), 'RIGHT'),
                ('LINEABOVE', (0, 0), (-1, -1), 1, self.colorBlue1),
                ('BACKGROUND', (0, 0), (-1, 0), self.colorGreenLines),
                ('BACKGROUND', (0, -1), (-1, -1), self.colorBlue1),
                ('SPAN', (0, -1), (-2, -1))
            ])
        full_table.setStyle(table_style)
        self.elements.append(full_table)


class Sample:

    def __init__(self):
        self.id = 0
        self.name = 0
        self.email = 0
        self.phone = 0
        self.address = 0


if __name__ == '__main__':
    data_records = [Sample() for x in range(100)]
    report = PdfGenerator('pdf_report.pdf', data_records)

    """ Below code can be integrated to work with Django """
    # buffer = BytesIO()
    # doc = PdfGenerator(buffer, data_records)
    # pdf = buffer.getvalue()
    # buffer.close()

    # email = EmailMessage('Hello', 'Body', 'from@from.com', ['to@to.com'])
    # email.attach('invoicex.pdf', pdf, 'application/pdf')
    # email.send()

    # return Response({'data': base64.b64encode(pdf).decode(), 'title': report.code}, status=status.HTTP_200_OK)
