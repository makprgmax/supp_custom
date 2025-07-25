from openai import OpenAI

client = OpenAI(
  api_key=''
)


import csv
from PyPDF2 import PdfReader

def extract_text_from_pdf(file_path):
    # pdf_reader = PyPDF2.PdfReader(open(file_path, 'rb'))
    pdf_reader = PdfReader(open(file_path, 'rb'))
    text = ""
    
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


def create_qa_from_text(text):


    response = client.completions.create(
        model='gpt-3.5-turbo-instruct',
        prompt=f"Extract questions and answers from the following text:\n\n{text}",
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.1
    )
    return response.choices[0].text.strip()


pdf_file_path = './pdf/UG_MTK_L_EN/UG_MTK_L_EN-22.pdf'
pdf_file_path = './pdf/Basic_Touch-624/_User_Guide_pb_624_EN-14.pdf'

pdf_text = extract_text_from_pdf(pdf_file_path)

qa_text = create_qa_from_text(pdf_text)

qa_pairs = qa_text.split('\n\n')
output_csv_path = 'output.csv'


with open(output_csv_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(["question", "context", "answers"])
    for pair in qa_pairs:
        question, answer = pair.split('\n', 1)
        print(f'q:\n{question}\n a:{answer} \n')
        writer.writerow([question, pdf_text, answer])
        

print(f"Data successfully written to {output_csv_path}")


