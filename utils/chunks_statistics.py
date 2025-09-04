import json
import statistics

with open("data/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

char_lengths = [len(chunk["text"]) for chunk in chunks]
word_counts = [len(chunk["text"].split()) for chunk in chunks]


def print_stats(name, values):
    print(f"{name} stats:")
    print(f"\tMin: {min(values)}")
    print(f"\tMedian: {int(statistics.median(values))}")
    print(f"\tAverage: {sum(values)/len(values):.2f}")
    print(f"\tMax: {max(values)}")


print("Total Chunks: ", len(chunks))
print_stats("\nCharacters per chunk", char_lengths)
print_stats("\nWords per chunk", word_counts)

large_chunks = [chunk
                for chunk in chunks if len(chunk["text"].split()) > 300]
small_chunks = [chunk
                for chunk in chunks if len(chunk["text"].split()) < 25]

print("\nChunks with more than 300 words: ", len(large_chunks))
print("\nChunks with less than 25 words: ", len(small_chunks))
