import re

s = "Programming is fun"


new_s = s.split(" ")

for i in range(len(new_s)):
    if re.search(new_s[i], ".*[aeiou].*"):
        new_s[i] = "asterisks"
s = ""
for i in new_s:
    s += i
print(s)
