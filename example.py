from tedis import Tedis

template = "Integer: {{int:6}} -- Punc: {{ str:8:punc }} -- Alpha: {{ str:10:alpha }} -- Alphapunc: {{str:15:alphapunc}} -- Alphanumeric: {{str:6:alphanumeric}} -- Puncnumeric: {{ str:16:puncnumeric }}"
tester = Tedis(server = 'localhost:6379', redis_key = 'bacon')
tester.load(template, 10000)
tester.dump()
tester.close()