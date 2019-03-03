import cProfile
#pr = cProfile.Profile()
# pr.enable()
import blng.Voodoo
# pr.disable()
# pr.print_stats()


#pr = cProfile.Profile()
# pr.enable()
session = blng.Voodoo.DataAccess('crux-example.xml')
# pr.disable()
# pr.print_stats()

#pr = cProfile.Profile()
# pr.enable()
root = session.get_root()
# pr.disable()
# pr.print_stats()


"""

#pr = cProfile.Profile()
# pr.enable()
root.simpleleaf = 'Hello World!'
# pr.disable()
# pr.print_stats()

pr = cProfile.Profile()
pr.enable()
print(session.dumps())
pr.disable()
pr.print_stats()

root.morecomplex.leaf2 = "a"

import time
n = 10000
start_time = time.time()
for x in range(n):
    root.simpleleaf = str(x)
end_time = time.time()

print((end_time-start_time), 'for', n)
print((end_time-start_time)/n)
a = end_time-start_time

xmldoc = session._xmldoc

#start_time = time.time()
# for x in range(n):
#    e = xmldoc.xpath('//simpleleaf')[0] = str(x)
#end_time = time.time()

#print((end_time-start_time), 'for', n)
# print((end_time-start_time)/n)
#b = end_time-start_time


#e = xmldoc.xpath('//simpleleaf')[0]
#start_time = time.time()
# for x in range(n):
#    e = str(x)
#end_time = time.time()

#print((end_time-start_time), 'for', n)
# print((end_time-start_time)/n)
#c = end_time-start_time

# print((a/b)*100)

"""


l = root.simplelist.create('sdf')
print('-'*80)
l.nonleafkey = 'sdf'
print('='*80)
print(session.dumps())
