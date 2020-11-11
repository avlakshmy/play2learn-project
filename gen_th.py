# Reference for web html: https://stackoverflow.com/questions/8238407/how-to-parse-excel-xls-file-in-javascript-html5
# Reference for style: https://speckyboy.com/code-snippet-form-ui/

from fpdf import FPDF
import pandas as pd
import sys
import random
import json
import numpy as np

class PDF(FPDF):
    def lines(self):
        self.set_line_width(0.0)
        self.line(5.0,5.0,292.0,5.0) # top one
        self.line(5.0,205.0,292.0,205.0) # bottom one
        self.line(5.0,5.0,5.0,205.0) # left one
        self.line(292.0,5.0,292.0,205.0) # right one

    def draw_rectangle(self, r, g, b):
        self.set_fill_color(r, g, b)
        self.rect(10, 10, 120, 190, 'F')

    def add_image(self, img_path):
        self.set_xy(20, 70)
        self.image(img_path,  link='', type='', w=100)

    def add_cryptogram(self, cryptogram, cryptocode, code):
        self.add_page()
        self.lines()
        self.set_text_color(0, 0, 0)

        self.set_font('Helvetica', 'B', 24)

        self.set_xy(35, 40)
        self.cell(w=225, h=20.0, align='C', txt="Solve the cryptogram!",border=0)

        if len(cryptogram) <= 18:
            w = (260 - 15*len(cryptogram)) // 2
            self.set_xy(w+15,75.0)
            for i in range(len(cryptogram)):
                self.cell(w=15, h=10.0, align='C', txt=cryptogram[i], border=1)
            self.set_xy(w+15,90.0)
            for i in range(len(cryptogram)):
                self.cell(w=15, h=10.0, align='C', txt=cryptocode[i], border=1)
        else:
            w = (260 - 10*len(cryptogram)) // 2
            self.set_font('Helvetica', 'B', 20)
            self.set_xy(w+15,75.0)
            for i in range(len(cryptogram)):
                self.cell(w=10, h=10.0, align='C', txt=cryptogram[i], border=1)
            self.set_xy(w+15,90.0)
            for i in range(len(cryptogram)):
                self.cell(w=10, h=10.0, align='C', txt=cryptocode[i], border=1)

        self.set_font('Helvetica', 'B', 24)

        self.set_xy(50,115)
        for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']:
            self.cell(w=15, h=10.0, align='C', txt=letter, border=1)

        self.set_xy(50,125)
        for codenum in [str(x) for x in code[:13]]:
            self.cell(w=15, h=10.0, align='C', txt=codenum, border=1)

        self.set_xy(50,145)
        for letter in ['N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
            self.cell(w=15, h=10.0, align='C', txt=letter, border=1)

        self.set_xy(50,155)
        for codenum in [str(x) for x in code[13:]]:
            self.cell(w=15, h=10.0, align='C', txt=codenum, border=1)

    def add_title_page(self, quiz_name, author_name, date):
        self.add_page()
        self.lines()

        self.set_xy(50,50.0)
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=200, h=20.0, align='C', txt=quiz_name, border=0)

        self.set_xy(75,110.0)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=150, h=20.0, align='C', txt=author_name, border=0)

        self.set_xy(75,140.0)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 0, 0)
        self.multi_cell(w=150, h=20.0, align='C', txt=date, border=0)

    def add_qn(self, i, text, pic):
        self.add_page()
        self.lines()
        self.draw_rectangle(255, 204, 204)
        if not (pd.isnull(pic)):
            self.add_image('tempfiles/'+pic)
            # self.add_image('../ma2040/'+pic)
        self.set_xy(150.0,70.0)
        self.set_font('Helvetica', '', 24)
        self.set_text_color(102, 0, 51)
        self.cell(w=130, h=15, align='C', txt="Qn {}:".format(i), border=0)
        self.set_xy(150.0,90.0)
        self.multi_cell(w=130, h=15, align='C', txt=text, border=0)

    def add_ans(self, i, text, url):
        self.add_page()
        self.lines()
        self.draw_rectangle(204, 255, 229)
        self.set_xy(150.0,80.0)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(0, 102, 51)
        self.cell(w=130, h=20, align='C', txt="Ans {}:".format(i), border=0)
        self.set_xy(150, 100)
        if not (pd.isnull(url)):
            self.set_text_color(0, 0, 204)
            self.cell(w=130, h=20.0, align='C', txt=text, border=0, link=url)
        else:
            self.cell(w=130, h=20.0, align='C', txt=text, border=0, link="")

    def add_hint(self, i, hint):
        hint_text = '{} ={}'.format(hint[0], hint[1])
        self.add_page()
        self.lines()
        self.draw_rectangle(204, 204, 255)
        self.set_xy(150.0,80.0)
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(51, 0, 102)
        self.cell(w=130, h=20, align='C', txt="Hint {}:".format(i), border=0)
        self.set_xy(150, 100)
        self.cell(w=130, h=20.0, align='C', txt=hint_text, border=0, link="")

def main(input_file_contents, output_file_path, quiz_name, mode, crypt, author_name, date):
    qa_df = pd.read_json(input_file_contents)
    # qa_df = pd.read_excel(input_file_contents)
    num_qs = len(qa_df)

    if not 'Question Image' in qa_df.columns:
        qa_df['Question Image'] = [np.nan for _ in range(num_qs)]

    if not 'Answer Link' in qa_df.columns:
        qa_df['Answer Link'] = [np.nan for _ in range(num_qs)]

    code = list(range(1, 27))
    random.shuffle(code)
    cryptogram = list(crypt.upper())
    cryptocode = []
    all_crypt = list(''.join(crypt.upper().split()))
    uniq = list(set(all_crypt))
    hide_num = int(len(uniq) * 0.75) # hide 75% of the letters
    hide = random.sample(uniq, hide_num)
    hints = set()

    for i in range(len(cryptogram)):
        if cryptogram[i] in hide:
            cryptocode.append(" {} ".format(code[ord(cryptogram[i]) - ord('A')]))
            hints.add((cryptogram[i],cryptocode[-1]))
            cryptogram[i] = "__"
        elif cryptogram[i] == " ":
            cryptogram[i] = "\t"
            cryptocode.append("\t")
        else:
            cryptocode.append(" {} ".format(code[ord(cryptogram[i]) - ord('A')]))

    hints = list(hints)

    for letter in hide:
        code[ord(letter) - ord('A')] = " "

    for i in range(len(code)):
        if (not code[i] == " "): # still not perfect, but can live with it...
            if random.randint(1, 26) % 26 < 13:
                code[i] = " "

    if not output_file_path[-4:] == '.pdf':
        output_file_path = output_file_path + ".pdf"

    pdf=PDF(orientation='L')

    pdf.add_title_page(quiz_name, author_name, date)

    if mode == "Classroom":
        for i in range(num_qs):
            pdf.add_qn(i+1, qa_df['Question'][i], qa_df['Question Image'][i])
            pdf.add_ans(i+1, qa_df['Answer'][i], qa_df['Answer Link'][i])
            if i < len(hints):
                pdf.add_hint(i+1, hints[i])

        pdf.add_cryptogram(cryptogram, cryptocode, code)
        pdf.add_ans("to Cryptogram", crypt.upper(), "")

    elif mode == "Test":
        for i in range(num_qs):
            pdf.add_qn(i+1, qa_df['Question'][i], qa_df['Question Image'][i])

        pdf.add_cryptogram(cryptogram, cryptocode, code)

        for i in range(num_qs):
            pdf.add_ans(i+1, qa_df['Answer'][i], qa_df['Answer Link'][i])

        pdf.add_ans("to Cryptogram", crypt.upper(), "")

    pdf.set_author(author_name)
    pdf.output(output_file_path,'F')

    return pdf

if __name__ == '__main__':
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    quiz_name = sys.argv[3]
    mode = sys.argv[4]
    crypt = sys.argv[5]
    author_name = sys.argv[6]
    date = sys.argv[7]

    main(input_file_path, output_file_path, quiz_name, mode, crypt, author_name, date)
