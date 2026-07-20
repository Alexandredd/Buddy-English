import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import vocabulary as vocab

# Test searches
print("Testing vocabulary search...")
results = vocab.search_vocabulary("hello")
print(f"Search for 'hello': {len(results)} results")
if results:
    print(f"  Found: {results[0]['word']}")

results2 = vocab.search_vocabulary("restaurante")
print(f"Search for 'restaurante': {len(results2)} results")
if results2:
    print(f"  Found: {results2[0]['word']}")

results3 = vocab.search_vocabulary("reunião")
print(f"Search for 'reunião': {len(results3)} results")
if results3:
    print(f"  Found: {results3[0]['word']}")

results4 = vocab.search_vocabulary("car")
print(f"Search for 'car': {len(results4)} results")

# Test with context filter
results5 = vocab.search_vocabulary("restaurant", context="Restaurante")
print(f"Search for 'restaurant' in context 'Restaurante': {len(results5)} results")
if results5:
    print(f"  Found: {results5[0]['word']}")

print("\nAll tests completed!")