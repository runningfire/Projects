from datetime import date , timedelta , datetime
dt_now = datetime.now()
del_yes = timedelta(days=1)
dt_yes = dt_now - del_yes 
del_month_ago = timedelta(days=30)
dt_month_ago = dt_now - del_month_ago
dt_str = '01/01/17 12:10:03.234567'
date_dt = datetime.strptime(dt_str, '%d/%m/%Y %H:%M:%S.n')
print(dt_now , ' ' , dt_yes, ' ' , dt_month_ago , ' ', date_dt)