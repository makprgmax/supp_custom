import os
import csv
import json
import fitz  # PyMuPDF
import openai


default_value = "pb - of the best"
default_value_name = "Basic Touch-624"

directory_path = './pdf/Basic_Touch-624/'

def replace_empty(value):
    if not value:
        return [default_value] 
    return value

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def clean_text(text):
    text = text.replace('\n', ' ').replace('\t', ' ')
    text = text.encode('ascii', 'ignore').decode('ascii')
    return text

def split_text_into_chunks(text, chunk_size=500):
    sentences = clean_text(text).split('. ')
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

def extract_qa_context(chunk):

    prompt = (
        "Extract questions, answers, and context from the following text:"
        f"{chunk}"
        "Format the output as a JSON object with 'question', 'context', and 'answers'."
    )

    response = openai.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=570,
        n=1,
        stop=None,
        temperature=0
    )
    
    return response.choices[0].text.strip()

pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]

for pdf_file in pdf_files:
    file_path = os.path.join(directory_path, pdf_file)

    pdf_text = extract_text_from_pdf(file_path)

    chunks = split_text_into_chunks(pdf_text)

    qa_contexts = [extract_qa_context(chunk) for chunk in chunks]

    qa_contexts_out = []

    for i, item in enumerate(qa_contexts):
        try:
            print(f"item **** >>> {item}")
            json_object = json.loads(item)
            qa_contexts_out.append(json_object)
        except json.JSONDecodeError as e:
            print(f"Ошибка в элементе {i}: {e}")
            print(f"Содержание: {item}")


    for item in qa_contexts_out:
        item["context"] = f"{default_value}: {default_value_name}. {item['context']}"

        item["answers"] = "".join(item["answers"])


    json_file_path = os.path.join(directory_path, f'{pdf_file.replace(".pdf", "")}.json')


    with open(json_file_path, 'w', encoding='utf-8') as outfile:
        json.dump(qa_contexts_out, outfile, ensure_ascii=False, indent=4)