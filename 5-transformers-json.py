import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset
from transformers import AutoTokenizer, BertForQuestionAnswering, Trainer, TrainingArguments
import json

save_path = "save"

file_path = "./tmp/output.json"
with open(file_path, 'r',  encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data)
df = df[['question', 'context', 'answers']]
train_df, test_df = train_test_split(df, test_size=0.2)
train_dataset = Dataset.from_pandas(train_df)
test_dataset = Dataset.from_pandas(test_df)

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
model = BertForQuestionAnswering.from_pretrained("bert-base-cased")

def preprocess_function(examples):
    inputs = tokenizer(examples['question'], examples['context'], truncation=True, padding='max_length', max_length=512)
    start_positions = []
    end_positions = []

    for i in range(len(examples['answers'])):
        start_pos = examples['context'][i].find(examples['answers'][i])
        end_pos = start_pos + len(examples['answers'][i])
        start_positions.append(start_pos)
        end_positions.append(end_pos)
    
    inputs.update({'start_positions': start_positions, 'end_positions': end_positions})
    return inputs

train_dataset = train_dataset.map(preprocess_function, batched=True)
test_dataset = test_dataset.map(preprocess_function, batched=True)

train_dataset = train_dataset.remove_columns(['question', 'context', 'answers'])
test_dataset = test_dataset.remove_columns(['question', 'context', 'answers'])
train_dataset.set_format('torch')
test_dataset.set_format('torch')

training_args = TrainingArguments(
    output_dir='./results2',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
)

trainer.train()

trainer.evaluate()

model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)