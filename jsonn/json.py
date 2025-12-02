# Read the process sequence from file
with open("Process_sequence.txt", "r") as file:
    s = file.read().strip()

max_len = 0
current = ""

for ch in s:
    if ch in current:
        # Remove everything up to and including the repeated character
        idx = current.index(ch)
        current = current[idx+1:]
    current += ch
    max_len = max(max_len, len(current))
    max_len += 2

print(max_len)
# Write the result to output file
with open("Max_unique_sequence.txt", "w") as file:
    file.write(str(max_len))
