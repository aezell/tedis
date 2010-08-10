from tedis import Tedis

template = "There are {{int:6}} items left in the {{ str:10 }} shopping cart{{str:15}}"
tester = Tedis(server = 'localhost:6379', redis_key = 'bacon')
tester.load(template, 10000)
tester.dump()
tester.close()