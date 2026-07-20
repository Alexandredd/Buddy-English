import requests
import json

# Test the dictionary API directly
print("Testing Free Dictionary API...")
try:
    r = requests.get('https://api.dictionaryapi.dev/api/v2/entries/en/car', timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Found word: {data[0].get('word')}")
        print(f"Meanings: {len(data[0].get('meanings', []))}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

# Test the vocabulary module
print("\nTesting vocabulary module...")
import vocabulary as vocab

# Try to search for words in our vocabulary
results = vocab.search_vocabulary("hello")
print(f"Local search results for 'hello': {len(results)}")
if results:
    print(f"  Found: {results[0]['word']} - {results[0]['translation']}")

results2 = vocab.search_vocabulary("restaurante")
print(f"Local search results for 'restaurante': {len(results2)}")
if results2:
    print(f"  Found: {results2[0]['word']} - {results2[0]['translation']}")

# Check if file exists
from pathlib import Path
vocab_file = Path(__file__).with_name("vocabulary_data.json")
print(f"Vocab file exists: {vocab_file.exists()}")
if vocab_file.exists():
    with vocab_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"Vocab items: {len(data)}")
        if data:
            print(f"First item: {data[0]}")