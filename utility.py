#%%
import re
from pathlib import Path

import pandas as pd

OUT_FOLDER = Path("fdf_posts")


def fix_multilevel(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


def write_to_file(file, name, value):
    pattern_tag = rf"\[//\]: # \({name}\)"

    pattern_full = rf"({pattern_tag})([\s\S]*)({pattern_tag})"
    file_content = file.read_text()

    # print("===================")
    # print(re.findall(pattern_tag, file_content))
    # print(re.findall(pattern_full, file_content))
    # print("===================")
    repl = re.sub(pattern_full, rf"\1\n\n{value.strip()}\n\n\3", file_content)
    file.write_text(repl)


def write_img_to_file(file, name, path: Path, alt_text=None, caption=None):
    path = path.relative_to(OUT_FOLDER)
    x = str(path).replace("\\", "/")
    # print(x)
    c = f"{caption}\n" if caption else ""
    alt_text = alt_text or ""
    img_tag = f"{c}![{alt_text}]({x})"
    write_to_file(file, name, img_tag)
