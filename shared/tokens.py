from __future__ import annotations

import io
from pathlib import Path
import tiktoken

try:
    _ENC = tiktoken.get_encoding("cl100k_base")
except Exception:
    _vscode_bpe = list(
        Path(r"C:\Users\Shiva\AppData\Local\Programs\Microsoft VS Code").glob(
            "**/cl100k_base.tiktoken"
        )
    )
    if _vscode_bpe:
        with open(_vscode_bpe[0], "rb") as f:
            data = f.read()
        buf = io.BytesIO(data)
        ranks = {}
        idx = 0
        while True:
            len_b = buf.read(1)
            if not len_b:
                break
            ranks[buf.read(len_b[0])] = idx
            idx += 1
        _ENC = tiktoken.Encoding(
            name="cl100k_base",
            pat_str=r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}++|\p{N}{1,3}+| ?[^\s\p{L}\p{N}]++[\r\n]*+|\s++$|\s*[\r\n]|\s+(?!\S)|\s""",
            mergeable_ranks=ranks,
            special_tokens={
                "<|endoftext|>": 100257,
                "<|fim_prefix|>": 100258,
                "<|fim_middle|>": 100259,
                "<|fim_suffix|>": 100260,
                "<|endofprompt|>": 100276,
            },
        )
    else:
        raise


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(_ENC.encode(text))
