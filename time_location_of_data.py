#!/usr/bin/env python

def relative_timestamp_hist(year,month):
    idx=-1-((2005-year)*12+(12-month))
    if idx<0:
        return idx
    else:
        exit

def relative_timestamp_fcst(year,month):
    idx=-1-((2100-year)*12+(12-month))
    if idx<0:
        return idx
    else:
        exit
