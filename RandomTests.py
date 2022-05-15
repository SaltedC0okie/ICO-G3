import random

l = [1,2,3,4,5]

print(l[2:])

total = 6 * 32
print(f"total={total}")
perday = total / 6
print(f"perday={perday}")
a = 39
print(f"a={a}")
day_inc = int(a/32)
hour_inc = int(a % 32 / 2)
half_hour_inc = int(hour_inc - int(hour_inc) + 0.5)
print(day_inc)
print(hour_inc)
print(half_hour_inc)
