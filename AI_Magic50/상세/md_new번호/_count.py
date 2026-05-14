import re, sys
text = open(sys.argv[1], encoding='utf-8').read()
body = re.sub(r'^---.*?---\n', '', text, count=1, flags=re.DOTALL)
plain = re.sub(r'[#*_`\\]', '', body)
plain = re.sub(r'\s+', '', plain)
print(f'plain: {len(plain)}, full: {len(body)}')
