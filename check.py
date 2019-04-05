import ephem
from datetime import datetime
user_text = input()
today = str(datetime.now())
dt = today.split(' ')
if (user_text == 'Mercury'):
    local = ephem.Mercury()
    local.compute(dt[0])
    cons = ephem.constellation(local)
    print(cons)
elif (user_text == 'Venus'):
    local = ephem.Venus()
    local.compute(dt[0])
    cons = ephem.constellation(local)
    print(cons)
elif (user_text == 'Earth'):
    local = ephem.Earth()
    local.compute(dt[0])
    cons = ephem.constellation(local)
    print(cons)
elif (user_text == 'Mars'):
    local = ephem.Mars()
    local.compute(dt[0])
    cons = ephem.constellation(local)
    print(cons)   