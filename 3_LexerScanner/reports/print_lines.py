import pathlib
path=pathlib.Path(r"d:\uni\year2\dsllab\3_LexerScanner\reports\report.tex")
for i, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
    if 110 <= i <= 120:
        print(f"{i:4}: {line}")
