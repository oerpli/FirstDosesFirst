#%%
import re
from pathlib import Path



def write_to_file(file, name, value):
    pattern_tag = rf"\[//\]: # \({name}\)"

    pattern_full = rf"({pattern_tag})([\s\S]*)({pattern_tag})"
    file_content = file.read_text()

    # print("===================")
    # print(re.findall(pattern_tag, file_content))
    # print(re.findall(pattern_full, file_content))
    # print("===================")
    repl =  re.sub(pattern_full, rf"\1\n\n{value.strip()}\n\n\3", file_content)
    file.write_text(repl)


# %%