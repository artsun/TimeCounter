# -*- coding: utf-8 -*-
import datetime
import calendar

def sliece_month(alldays: list) -> list:
    temp = []
    while len(alldays) > 0:
        temp.append(alldays[:7])
        del alldays[:7]
    return temp


if __name__ == '__main__':
    cal = calendar.Calendar()
    for x in range(1,13):
        alldays = [day.day for day in cal.itermonthdates(2020, x)]
        print(sliece_month(alldays))


    #print()
    #print(datetime.date(2020, 7, 8).day)
