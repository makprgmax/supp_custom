import csv

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

file_path = './pdf/Basic_2-614/User_Guide_pb_614_EN-63-64'
file_path = './pdf/Basic_Touch-624/tmp/output_page_14'
file_path = './pdf/Basic_Touch-624/_User_Guide_PB_624_EN-14'

pdf_text = extract_text_from_pdf(file_path+'.pdf')


contextSentences = []

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text


def split_text_into_chunks(text, chunk_size=500):
    global contextSentences
    sentences = clean_text(text).split('. ')
    contextSentences = sentences

    chunks = []
    current_chunk = []

    for sentence in sentences:
        current_chunk.append(sentence)
        if len(' '.join(current_chunk)) >= chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

chunks = split_text_into_chunks(pdf_text)


import openai


ii=1
def extract_qa_context(chunk):
    global ii
    ii+=1
    prompt = (
        "Extract questions, answers, and context from the following text:"
        f"{chunk}"
        "Format the output as a JSON object with 'questions', 'answers', and 'context'."
    )

    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.1
    )

    return response.choices[0].text.strip()



qa_contexts = [extract_qa_context(chunk) for chunk in chunks]

print(qa_contexts)


import json

all_qa = {'questions': [], 'answers': [], 'context': []}
all_qa['context'].extend(contextSentences)


for qa_context in qa_contexts:
    try:

        qa_json = json.loads(qa_context)
        all_qa['questions'].extend(qa_json.get('questions', []))
        all_qa['answers'].extend(qa_json.get('answers', []))
        all_qa['context'].extend(qa_json.get('context', []))
    except json.JSONDecodeError:
        continue  



with open('qa_contexts.json', 'w') as f:
     json.dump(all_qa, f, indent=4)

exit()

default_value = "PB - best reader !!!"

def replace_empty(value):
    if value is None or value == '':
        return default_value
    return value


csv_file_path = file_path + '.csv'
with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';')
    csvwriter.writerow(['question', 'context', 'answers'])
    
    for question, context, answer in zip(all_qa['questions'],  all_qa['context'], all_qa['answers']):
        csvwriter.writerow([
            replace_empty(question), 
            replace_empty(context), 
            replace_empty(answer) 
        ])