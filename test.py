from datetime import date,datetime
  

todays_date = date.today()
  

print("Current date: ", todays_date)
  

print("Current year:", todays_date.year)
print("Current month:", todays_date.month)
print("Current day:", todays_date.day)

d1= datetime.strptime(str(todays_date), r"%Y-%m-%d")
d2 = datetime.strptime("2023-01-22", r"%Y-%m-%d")
delta = d1 - d2
print(f'Difference is {delta.days} days')