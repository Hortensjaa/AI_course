fin = open("ptwolnelektury.txt", "r")
fout = open("test.txt", "w")
import re

def normalize_line(text):
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)
    return text

def normalize_line_nospaces(text):
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"^[ \t]+", "", text, flags=re.MULTILINE)
    return "".join(text.split()) + '\n'

for l in fin.readlines():
    if l != "\n":
        fout.write(normalize_line_nospaces(l))
