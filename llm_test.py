from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline


model_name = "google/flan-t5-base"
token = "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"  

# HuggingFace token ile model yükle
tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name, token=token)

pipe = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200
)

# prompt Türkçe olursa anlamayabilir, bu model İngilizce için daha iyi
prompt = "What is the capital of France?"
result = pipe(prompt)
print(result[0]["generated_text"])
