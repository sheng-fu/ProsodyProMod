#!/usr/bin/env python
# coding: utf-8

# Python implementation by Sheng-Fu Wang (shengfu.wang@nyu.edu) 
# Last update: 1 November, 2024

# _ProsodyPro (previously: _TimeNormalizeF0.praat)
# Version 5.7.8.7
# Last update: 3 November, 2021
# Written by:   Yi Xu; all rights reserved.
# Report any bugs to Yi Xu (yi.xu@ucl.ac.uk)

# Find more information at http://www.homepages.ucl.ac.uk/~uclyyix/ProsodyPro/



import parselmouth as pm
import os
import copy
import math
import numpy as np

import argparse

parser = argparse.ArgumentParser(description='')

parser.add_argument('-directory', action="store", dest="directory", default = './', type=str)


parser.add_argument('-target_tier', action="store", dest="target_tier", default = 1, type=int)
parser.add_argument('-min_f0', action="store", dest="min_f0", default = 75, type=int)
parser.add_argument('-max_f0', action="store", dest="max_f0", default = 600, type=int)

parser.add_argument('-TextGrid_extension', action="store", dest="TextGrid_extension", default = ".TextGrid", type=str)
parser.add_argument('-Sound_file_extension', action="store", dest="Sound_file_extension", default = ".wav", type=str)

parser.add_argument('-npoints', action="store", dest="npoints", default = 10, type=int)
parser.add_argument('-f0_sample_rate', action="store", dest="f0_sample_rate", default = 100, type=int)

parser.add_argument('-get_BID_measures', action="store", dest="get_BID_measures", default = 0, type=int)

parser.add_argument('-energy_band_size', action="store", dest="energy_band_size", default = 500, type=int)
parser.add_argument('-energy_band_step_size', action="store", dest="energy_band_step_size", default = 250, type=int)
parser.add_argument('-max_number_of_formants', action="store", dest="max_number_of_formants", default = 5, type=int)
parser.add_argument('-maximum_formant', action="store", dest="maximum_formant", default = 5000, type=int)

parser.add_argument('-silence_marker', action="store", dest="silence_marker", default = "", type=str)

parser.add_argument('-perturbation_length', action="store", dest="perturbation_length", default = 0.0, type=float)
parser.add_argument('-final_offset', action="store", dest="final_offset", default = -0.03, type=float)
parser.add_argument('-smoothing_window_width', action="store", dest="smoothing_window_width", default = 0.07, type=float)

parser.add_argument('-set_initial_normalized_time_to_0', action="store", dest="set_initial_normalized_time_to_0", default = 1, type=int)

parser.add_argument('-capture_consonant_perturbation', action="store", dest="capture_consonant_perturbation", default = 0, type=int)

parser.add_argument('-other_tiers', action="store", dest="other_tiers", default = "", type=str)

args = parser.parse_args()

save_output_files = 1


directory = args.directory

target_tier = args.target_tier

TextGrid_extension = args.TextGrid_extension
Sound_file_extension = args.Sound_file_extension


min_f0 = args.min_f0
max_f0 = args.max_f0

npoints = args.npoints  
f0_sample_rate = args.f0_sample_rate  

get_BID_measures = args.get_BID_measures  
energy_band_size = args.energy_band_size  
energy_band_step_size = args.energy_band_step_size  
max_number_of_formants = args.max_number_of_formants  
maximum_formant = args.maximum_formant  

silence_marker = args.silence_marker  
perturbation_length = args.perturbation_length  
final_offset = args.final_offset 
smoothing_window_width = args.smoothing_window_width  
set_initial_normalized_time_to_0 = args.set_initial_normalized_time_to_0 
capture_consonant_perturbation = args.capture_consonant_perturbation  

other_tiers = args.other_tiers

other_tiers = [int(x) for x in other_tiers.split(",") if x != ""]
empty_intevals = ["", " ", "\n", "\t"]




soundfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and Sound_file_extension in f]
soundfiles
textgridfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and TextGrid_extension in f]
textgridfiles


# In[7]:


set_initial_normalized_time_to_0 = 1
hasmeanstitle = 0
hasnormf0 = 0
hasnormtime_semitonef0 = 0
hasmean_normf0 = 0
found_interval = 0
last_means_nrows = 0
hasnormactutime = 0
hassamplef0 = 0
hasf0velocity = 0
hasnormtime_f0velocity = 0
hasf0acceleration = 0
hasnormtime_f0acceleration = 0
hasnormIntensity = 0
hasmean_normf0_cross_speaker = 0
hasBID = 0
hasVoice = 0
number = 1
repetition = 1
has_number_of_repetitions = 0


# In[8]:


def Get_point(PraatObject, index):
    if index % 1 == 0.0:
        sample_time = pm.praat.call(PraatObject, "Get time from index...", i)
    else:
        small_index = index // 1
        large_index = (index+1) // 1
        sample_time_small = pm.praat.call(PraatObject, "Get time from index...", small_index)
        sample_time_large = pm.praat.call(PraatObject, "Get time from index...", large_index)
        sample_time = (sample_time_large - sample_time_small) * (index-small_index)/(large_index-small_index) + sample_time_small
    return sample_time
        


# In[9]:


def Labeling(directory, soundname):
    filename = soundname.replace(Sound_file_extension, "")
    Sound_name = pm.read(os.path.join(directory, filename + Sound_file_extension))
    TextGrid_name = pm.read(os.path.join(directory, filename + TextGrid_extension))
    PointProcess_name = pm.praat.call(Sound_name, "To PointProcess (periodic, cc)", min_f0, max_f0)
    
    return filename, Sound_name, TextGrid_name, PointProcess_name

#filename, Sound_name, TextGrid_name, PointProcess_name = Labeling(soundfiles[0])


# In[48]:


def Create_other_tier_columns(TableOfReal, TextGrid):
    if len(other_tiers) > 0:
        for other_tier in other_tiers:
            tier_label = pm.praat.call(TextGrid, "Get tier name", other_tier)
            ncol = pm.praat.call(TableOfReal, "Get number of columns")
            pm.praat.call(TableOfReal, "Insert column", ncol + 1, tier_label)     
            #pm.praat.call(TableOfReal, "Set column label (index)", ncol + 1, tier_label)    
    return TableOfReal

def Fill_other_tier_columns(TableOfReal, TextGrid, start1, target_row, colnames):
    if len(other_tiers) > 0:
        for i in range(len(other_tiers)):
            interval_int = pm.praat.call(TextGrid_name, "Get interval at time", other_tiers[i], start1 - perturbation_length)
            interval_label = pm.praat.call(TextGrid_name, "Get label of interval", other_tiers[i], interval_int)
            ncol = pm.praat.call(TableOfReal, "Get number of columns")
            target_col = ncol - len(other_tiers) + 1 + i
            pm.praat.call(TableOfReal, "Set string value", target_row, colnames[target_col], interval_label)
    return TableOfReal


# In[88]:


def Normalize(Pitchtier_1, TableOfReal_1, TableOfReal_2, end, start1, interval, label, firstime, TextGrid_name):
    duration = end - start1


    ncols = pm.praat.call(TableOfReal_1, "Get number of columns")
    colnames1 = {i+1:pm.praat.call(TableOfReal_1, "Get column label", i+1) for i in range(ncols)}            
    ncols = pm.praat.call(TableOfReal_2, "Get number of columns")   
    colnames2 = {i+1:pm.praat.call(TableOfReal_2, "Get column label", i+1) for i in range(ncols)}                

    

    for x in range(0,npoints):
        normtime = start1 + duration * x / npoints
        if smoothing_window_width > 0:
            PitchTier = Pitchtier_1
        else:
            PitchTier = Pitchtier_name
        f0 = pm.praat.call(PitchTier, "Get value at time", normtime)
        nrows = pm.praat.call(TableOfReal_1, "Get number of rows")
        pm.praat.call(TableOfReal_1, "Set numeric value", nrows, colnames1[2], 1+x+interval*npoints)
        pm.praat.call(TableOfReal_1, "Set numeric value", nrows, colnames1[3], f0)
        new_label = label.replace(" ", "_")
        pm.praat.call(TableOfReal_1, "Set string value", nrows, 'rowLabel', new_label)
        pm.praat.call(TableOfReal_1, "Insert row", nrows + 1)        

        nrows = pm.praat.call(TableOfReal_2, "Get number of rows")
        pm.praat.call(TableOfReal_2, "Set numeric value", nrows, colnames2[2], normtime)
        if set_initial_normalized_time_to_0:
            pm.praat.call(TableOfReal_2, "Set numeric value", nrows, colnames2[2], normtime-firstime)
        pm.praat.call(TableOfReal_2, "Set numeric value", nrows, colnames2[3], f0)
        new_label = label.replace(" ", "_")
        pm.praat.call(TableOfReal_2, "Set string value", nrows, 'rowLabel', new_label)
        pm.praat.call(TableOfReal_2, "Insert row", nrows + 1)    


        TableOfReal_1 = Fill_other_tier_columns(TableOfReal_1, TextGrid_name, start1, nrows, colnames1)
        TableOfReal_2 = Fill_other_tier_columns(TableOfReal_2, TextGrid_name, start1, nrows, colnames2)
            
    return PitchTier, TableOfReal_1, TableOfReal_2


def Normalization(Pitchtier_1, TextGrid_name, name1 = "name1", name2 = "name2"):
    if smoothing_window_width > 0:
        PitchTier = Pitchtier_1
    else:
        PitchTier = Pitchtier_name
    lasttime = pm.praat.call(PitchTier, "Get finishing time")

    TableOfReal_name1 = pm.praat.call("Create TableOfReal", name1, 1, 2)

    TableOfReal_name1 = pm.praat.call(TableOfReal_name1, "To Table", "rowLabel")
    pm.praat.call(TableOfReal_name1, "Set column label (index)", 2, "NormalizedTime")
    pm.praat.call(TableOfReal_name1, "Set column label (index)", 3, "F0")


    
    TableOfReal_name2 = pm.praat.call("Create TableOfReal", name2, 1, 2)

    TableOfReal_name2 = pm.praat.call(TableOfReal_name2, "To Table", "rowLabel")
    pm.praat.call(TableOfReal_name2, "Set column label (index)", 2, "ActualTime")
    pm.praat.call(TableOfReal_name2, "Set column label (index)", 3, "F0") 


    

    TableOfReal_name1 = Create_other_tier_columns(TableOfReal_name1, TextGrid_name)
    TableOfReal_name2 = Create_other_tier_columns(TableOfReal_name2, TextGrid_name)

    
    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    interval = 0
    found_interval = 0
    nrows = 0
    for m in range(1,nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)

        if label not in empty_intevals or n_intervals == 1:
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)

            if smoothing_window_width > 0:
                PitchTier = Pitchtier_1
            else:
                PitchTier = TextGrid_name
            index1 = pm.praat.call(PitchTier, "Get high index from time", start1)
            index2 = pm.praat.call(PitchTier, "Get low index from time", end)
            if found_interval == 0:
                found_interval = 1
            if smoothing_window_width > 0:
                PitchTier = Pitchtier_1
            else:
                PitchTier = Pitchtier_name       
            firstime = start1
            PitchTier, TableOfReal_name1, TableOfReal_name2 = Normalize(PitchTier, TableOfReal_name1, TableOfReal_name2, end, start1, interval, label, firstime, TextGrid_name)
            interval = interval + 1

    nrows = pm.praat.call(TableOfReal_name1, "Get number of rows")

    pm.praat.call(TableOfReal_name1, "Remove row", nrows) 
    nrows = pm.praat.call(TableOfReal_name1, "Get number of rows")

    nrows = pm.praat.call(TableOfReal_name2, "Get number of rows")
    pm.praat.call(TableOfReal_name2, "Remove row", nrows) 
    return PitchTier, TableOfReal_name1, TableOfReal_name2


def Trim(PitchTier_name, n, maxbump, maxedge, maxgap):

    for i in range(2,n):

        tleft = pm.praat.call(PitchTier_name, "Get time from index", i-1)
        tmid = pm.praat.call(PitchTier_name, "Get time from index", i)
        tright = pm.praat.call(PitchTier_name, "Get time from index", i+1)
        gap1 = tmid - tleft
        gap2 = tright - tmid
        left = pm.praat.call(PitchTier_name, "Get value at index", i-1)

        mid = pm.praat.call(PitchTier_name, "Get value at index", i)
        right = pm.praat.call(PitchTier_name, "Get value at index", i+1)

        diff1 = mid - left
        diff2 = mid - right

        if (diff1 > maxbump and diff2 > maxedge and gap1 < maxgap and gap2 < maxgap) or (diff2 > maxbump and diff1 > maxedge and gap1 < maxgap and gap2 < maxgap):
            pm.praat.call(PitchTier_name, "Remove point", i)
            pm.praat.call(PitchTier_name, "Add point", tmid, left+(tmid-tleft)/(tright-tleft)*(right-left))

        if not capture_consonant_perturbation:
            if diff1 > maxbump and gap2 >= maxgap:
                pm.praat.call(PitchTier_name, "Remove point", i)
                pm.praat.call(PitchTier_name, "Add point", tmid, left + maxbump)        


            if diff2 > maxbump and gap1 >= maxgap:
                pm.praat.call(PitchTier_name, "Remove point", i)
                pm.praat.call(PitchTier_name, "Add point", tmid, right + maxbump)


        diff1 = left - mid
        diff2 = right - mid
        if (diff1 > maxbump and diff2 > maxedge and gap1 < maxgap and gap2 < maxgap) or (diff2 > maxbump and diff1 > maxedge and gap1 < maxgap and gap2 < maxgap):
            pm.praat.call(PitchTier_name, "Remove point", i)
            pm.praat.call(PitchTier_name, "Add point", tmid, left+(tmid-tleft)/(tright-tleft)*(right-left))    



        if not capture_consonant_perturbation:
            if diff1 > maxbump and gap2 >= maxgap:
                pm.praat.call(PitchTier_name, "Remove point", i)
                pm.praat.call(PitchTier_name, "Add point", tmid, left - maxbump)  

                
            if diff2 > maxbump and gap1 >= maxgap:
                pm.praat.call(PitchTier_name, "Remove point", i)
                pm.praat.call(PitchTier_name, "Add point", tmid, right - maxbump)

    return PitchTier_name



def Trimf0(PitchTier_name, npulses):
    maxbump = 0.01 
    maxedge = 0.0
    maxgap = 0.033
    n = pm.praat.call(PitchTier_name, "Get number of points")
    first = pm.praat.call(PitchTier_name, "Get value at index", 1)
    second = pm.praat.call(PitchTier_name, "Get value at index", 2)
    penult = pm.praat.call(PitchTier_name, "Get value at index", n-1) 
    last =  pm.praat.call(PitchTier_name, "Get value at index", n) 
    tfirst = pm.praat.call(PitchTier_name, "Get time from index", 1) 

    if npulses < 3:
        print("file needs to have more than three pulse marks")    
    tlast = pm.praat.call(PitchTier_name, "Get time from index", n)
    for k in range(0,3):
        PitchTier_name = Trim(PitchTier_name, n, maxbump, maxedge, maxgap)
    pm.praat.call(PitchTier_name, "Remove point", 1)
    pm.praat.call(PitchTier_name, "Add point", tfirst, second + (first-second) / 1000)
    pm.praat.call(PitchTier_name, "Remove point", n)
    pm.praat.call(PitchTier_name, "Add point", tlast, penult + (last-penult) / 1000)
    return PitchTier_name


def Smooth(PitchTier_curve_in, width, sampleStart, sampleEnd):
    PitchTier_curve_out = pm.praat.call("Create PitchTier", "curve_out", sampleStart, sampleEnd)  
    
    j = 1
    weight = {}
    
    for j in range(1, int(width + 1)):
        if j < width / 2 + 0.5:
            weight[j] = j
        else:
            weight[j] = width - j + 1

    smooth_end = pm.praat.call(PitchTier_curve_in, "Get number of points") 
    smooth_end += 1
   
    i = 1 
    while i < width / 2:  
        n = 0.0
        smoothsample = 0.0
        sample_time = pm.praat.call(PitchTier_curve_in, "Get time from index", i)

        j = 1 
        while j < width/2 + i:
            rawsample = pm.praat.call(PitchTier_curve_in, "Get value at index", j)
            index = width / 2 + j - i
            index = round(index)
            smoothsample += weight[index] * rawsample
            n += weight[index] 
            j += 1
        smoothsample = smoothsample / n
        if not math.isnan(smoothsample):
            pm.praat.call(PitchTier_curve_out, "Add point", sample_time, smoothsample)
        i += 1

    i = width/2
    while i < smooth_end - width/2:
        n = 0
        smoothsample = 0.0
        sample_time = pm.praat.call(PitchTier_curve_in, "Get time from index", round(i+0.01))
        j = 1
        while j < width:
            rawsample = pm.praat.call(PitchTier_curve_in, "Get value at index", int((i-width/2+j) // 1))
            smoothsample += weight[j] * rawsample
            n += weight[j]
            j += 1
        smoothsample /= n
        if not math.isnan(smoothsample):
            pm.praat.call(PitchTier_curve_out, "Add point", sample_time, smoothsample) 
        i += 1

    i = width/2
    while i > 0:
        n = 0.0
        smoothsample = 0.0
        i = round(i+0.01)
        sample_time = pm.praat.call(PitchTier_curve_in, "Get time from index", smooth_end-i)
        j = width/2 + i
        j = round(j+0.01)
        while j > 1:
            rawsample = pm.praat.call(PitchTier_curve_in, "Get value at index", smooth_end - j)
            index = width/2+i-j + 1
            index = round(index + 0.001)
            smoothsample += weight[index] * rawsample
            n += weight[index]
            j -= 1
        smoothsample /= n
        if not math.isnan(smoothsample):
            pm.praat.call(PitchTier_curve_out, "Add point", sample_time, smoothsample) 
        i -= 1

    return PitchTier_curve_out
    


def Sampling(PitchTier_name, TextGrid_name):
    TableOfReal_samplef0 = pm.praat.call(PitchTier_name, "Create TableOfReal", "samplef0", 1, 2)

    TableOfReal_samplef0 = pm.praat.call(TableOfReal_samplef0, "To Table", "rowLabel")
    pm.praat.call(TableOfReal_samplef0, "Set column label (index)", 2, "SampleTime")
    pm.praat.call(TableOfReal_samplef0, "Set column label (index)", 3, "F0")   

    last_sample_time = 0
    
    
    TableOfReal_samplef0 = Create_other_tier_columns(TableOfReal_samplef0, TextGrid_name)

    ncols = pm.praat.call(TableOfReal_samplef0, "Get number of columns")
    colnames = {i+1:pm.praat.call(TableOfReal_samplef0, "Get column label", i+1) for i in range(ncols)}      
    
    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    found_interval = 0
    nrows = 0
    hassampleStart = 0
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)
        if label not in empty_intevals or nintrevals == 1:
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length
            if start1-last_sample_time < 1/f0_sample_rate:
                start1 = last_sample_time + 1/f0_sample_rate
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)
            duration = end - start1
            if not hassampleStart:
                sampleStart = start1
                sampleEnd = pm.praat.call(TextGrid_name, "Get end point", target_tier, nintervals)
                PitchTier_samplef0 = pm.praat.call("Create PitchTier", "samplef0", sampleStart, sampleEnd)
                hassampleStart = 1
                found_interval = 1

            nsamples = duration * f0_sample_rate + 1
            nsamples = nsamples 
            x = 0
            while x < nsamples // 1:
                sample_time = start1 + x/f0_sample_rate
                f0 = pm.praat.call(PitchTier_name, "Get value at time", sample_time)

                pm.praat.call(PitchTier_samplef0, "Add point", sample_time, f0)
                nrows = pm.praat.call(TableOfReal_samplef0, "Get number of rows")
                pm.praat.call(TableOfReal_samplef0, "Set numeric value", nrows, colnames[2], sample_time)
                pm.praat.call(TableOfReal_samplef0, "Set numeric value", nrows, colnames[3], f0)            
                new_label = label.replace(" ", "_")
                pm.praat.call(TableOfReal_samplef0, "Set string value", nrows, 'rowLabel', new_label)
                pm.praat.call(TableOfReal_samplef0, "Insert row", nrows + 1) 
                TableOfReal_samplef0 = Fill_other_tier_columns(TableOfReal_samplef0, TextGrid_name, start1, nrows, colnames)
                x += 1
       

            
            sampleStart_time = sample_time + 1/f0_sample_rate
    if nrows > 1:
        pm.praat.call(TableOfReal_samplef0, "Remove row", nrows + 1) 
    if smoothing_window_width > 0:
        PitchTier_smoothf0 = Smooth(PitchTier_samplef0, smoothing_window_width * f0_sample_rate, sampleStart, sampleEnd)
        TableOfReal_smoothf0 = pm.praat.call(PitchTier_smoothf0, "Down to TableOfReal", "Hertz")
    else:
        TableOfReal_smoothf0 = copy.copy(TableOfReal_samplef0)

    return PitchTier_samplef0, PitchTier_smoothf0, TableOfReal_smoothf0, sampleStart, sampleEnd

def Differentiation(PitchTier_in_contour, TableOfReal_in_contour, npulses, TableOfReal_smoothf0, sampleStart, sampleEnd, TextGrid_name):

    PitchTier_out_contour = pm.praat.call("Create PitchTier", "out_contour", sampleStart, sampleEnd)

    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    labeled_intervals = []
    interval_lengths = []

    n_labeled_intervals = 0

    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)

        if label not in empty_intevals or nintrevals == 1:
            start1 = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)

            index_first = pm.praat.call(PitchTier_in_contour, "Get nearest index from time", start1)
            index_last = pm.praat.call(PitchTier_in_contour, "Get nearest index from time", end)

            interval_length = 0
            for x in range(index_first, index_last):
                x2 = x + 2
                x2a = x + 1
                f01 = pm.praat.call(PitchTier_in_contour, "Get value at index", x)
                f02 = pm.praat.call(PitchTier_in_contour, "Get value at index", x2)        
                sampletime1 = pm.praat.call(PitchTier_in_contour, "Get time from index", x)
                sampletime2 = pm.praat.call(PitchTier_in_contour, "Get time from index", x2) 

                if math.isnan(f02) or math.isnan(sampletime2):
                    f02 = pm.praat.call(PitchTier_in_contour, "Get value at index", x2a)    
                    sampletime2 = pm.praat.call(PitchTier_in_contour, "Get time from index", x2a)    
                derivative = (f02 - f01) / (sampletime2 - sampletime1)
                derivative_time = sampletime1
                pm.praat.call(PitchTier_out_contour, "Add point", derivative_time, derivative)
                points = pm.praat.call(PitchTier_out_contour, "Get number of points")
                interval_length += 1
            labeled_intervals.append(label)
            interval_lengths.append(interval_length)
    
    PitchTier_out_contour = Trimf0(PitchTier_out_contour, npulses)
   
    TableOfReal_out_contour = pm.praat.call(PitchTier_out_contour, "Down to TableOfReal", "Hertz")
    row = 0
    for m in range(0, len(labeled_intervals)):
        for x in range(interval_lengths[m]):
            row += 1
            new_label = labeled_intervals[m].replace(" ", "_")

            pm.praat.call(TableOfReal_out_contour, "Set row label (index)", row, new_label)
            pm.praat.call(TableOfReal_in_contour, "Set row label (index)", row, new_label)
            pm.praat.call(TableOfReal_smoothf0, "Set row label (index)", row, new_label)

    return PitchTier_out_contour, TableOfReal_out_contour, TableOfReal_in_contour, TableOfReal_smoothf0
    


def Intensity_normalization(TextGrid_name, Sound_name):
    TableOfReal_normtimeIntensity = pm.praat.call("Create TableOfReal", "normtimeIntensity", 1, 2)
    #pm.praat.call(TableOfReal_normtimeIntensity, "Set row label (index)", 1, 'test')

    TableOfReal_normtimeIntensity = pm.praat.call(TableOfReal_normtimeIntensity, "To Table", "rowLabel")

    pm.praat.call(TableOfReal_normtimeIntensity, "Set column label (index)", 2, "ActualTime")
    pm.praat.call(TableOfReal_normtimeIntensity, "Set column label (index)", 3, "Intensity")   

    Intensity_name = pm.praat.call(Sound_name, "To Intensity", 100, 0, "yes")

    TableOfReal_normtimeIntensity = Create_other_tier_columns(TableOfReal_normtimeIntensity, TextGrid_name)

    ncols = pm.praat.call(TableOfReal_normtimeIntensity, "Get number of columns")
    colnames = {i+1:pm.praat.call(TableOfReal_normtimeIntensity, "Get column label", i+1) for i in range(ncols)}      

    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    nrows = 0
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)
        if label not in empty_intevals or n_intervals == 1:
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length         
            firstime = start1
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)
            duration = end - start
            for x in range(0, npoints):
                normtime = start1 + duration * x / npoints
                intensity = pm.praat.call(Intensity_name, "Get value at time", normtime, "Cubic")
                nrows = pm.praat.call(TableOfReal_normtimeIntensity, "Get number of rows")
                pm.praat.call(TableOfReal_normtimeIntensity, "Set numeric value", nrows, colnames[2], normtime)
                if set_initial_normalized_time_to_0:
                    pm.praat.call(TableOfReal_normtimeIntensity, "Set numeric value", nrows, colnames[2], normtime-firstime)
                pm.praat.call(TableOfReal_normtimeIntensity, "Set numeric value", nrows, colnames[3], intensity)
                new_label = label.replace(" ", "_")
                pm.praat.call(TableOfReal_normtimeIntensity, "Set string value", nrows, "rowLabel", new_label)                
                pm.praat.call(TableOfReal_normtimeIntensity, "Insert row", nrows + 1)
                TableOfReal_normtimeIntensity = Fill_other_tier_columns(TableOfReal_normtimeIntensity, TextGrid_name, start1, nrows, colnames)


    if nrows > 1:
        pm.praat.call(TableOfReal_normtimeIntensity, "Remove row", nrows + 1)

    return TableOfReal_normtimeIntensity, normtime
                
                    
def Energy_bands(Sound_name_part, energyline, median_pitch):
    center = energy_band_step_size
    energies = {}
    for band in range(1,16):
        floor = center - 0.5*energy_band_size
        ceiling = center + 0.5*energy_band_size
        Sound_name_part_band = pm.praat.call(Sound_name_part, "Filter (pass Hann band)", floor, ceiling, 100)
        energy = pm.praat.call(Sound_name_part_band, "Get power", 0, 0)
        energy = 10 * math.log(50000*energy, 10)
        energies[band] = energy

        energyline = energyline + '\t' + str(energy)
        center += 0.5*energy_band_size

    center = median_pitch
    bandwidth = 2 * median_pitch

    for band in range(1, 3):
        floor = center = 0.5*bandwidth
        ceiling = center + 0.5*bandwidth
        Sound_name_part_band = pm.praat.call(Sound_name_part, "Filter (pass Hann band)", floor, ceiling, 100)
        energy = pm.praat.call(Sound_name_part_band, "Get power", 0, 0)
        energy = 10 * math.log(50000*energy, 10)
        energies[band] = energy
        center += median_pitch

    return energyline

def Formant_dispersion(FormantTier_name, starttime, endtime):
    dispersion1_3 = -1
    dispersion1_5 = -1
    midpoint = 0.5*(starttime + endtime)
    f = {}
    for i in range(1,6):
        f[i] = pm.praat.call(FormantTier_name, "Get value at time", i, midpoint)

    if not math.isnan(f[1]) and not math.isnan(f[2]) and not math.isnan(f[3]):
        dispersion = (f[3]-f[1]) / 2
        if f[3] < f[2]:
            dispersion1_3 = f[2]-f[1]
    else:
        dispersion1_3 = -1

    if not math.isnan(f[1]) and not math.isnan(f[3]) and not math.isnan(f[4]) and not math.isnan(f[5]):
        dispersion1_5 = (f[5] - f[1]) / 4
        if math.isnan(f[5]) or f[5] < f[4]:
            dispersion1_5 = (f[4]-f[1])/3
        if f[4] < f[3]:
            dispersion1_5 = dispersion1_3
    else:
        dispersion1_5 = -1

    
    return dispersion1_3, dispersion1_5

def Voice_quality(PointProcess_name, Sound_name, Harmonicity_name, starttime, endtime):
    jitter = pm.praat.call(PointProcess_name, "Get jitter (ddp)", starttime, endtime, 0.0001, 0.02, 1.3)
    shimmer = pm.praat.call([Sound_name, PointProcess_name], "Get shimmer (dda)", starttime, endtime, 0.0001, 0.02, 1.3, 1.6)
    harmonicity = pm.praat.call(Harmonicity_name, "Get mean", starttime, endtime)
    return jitter, shimmer, harmonicity

def BID_measures(starttime, endtime, m, name, label, Sound_name, Pitch_name, FormantTier_name, Harmonicity_name, voice_dict):

    Sound_name_part = pm.praat.call(Sound_name, "Extract part", starttime, endtime, "Rectangular", 1, "no")

    median_pitch = pm.praat.call(Pitch_name, "Get quantile", starttime, endtime, 0.5, "Hertz")
    if math.isnan(median_pitch):
        median_pitch = 100

    energyline = ""
    energyline = Energy_bands(Sound_name_part, energyline, median_pitch)
    dispersion1_3, dispersion1_5 = Formant_dispersion(FormantTier_name, starttime, endtime)
    jitter, shimmer, harmonicity = Voice_quality(PointProcess_name, Sound_name, Harmonicity_name, starttime, endtime)

    Spectrum_name_part = pm.praat.call(Sound_name_part, "To Spectrum", "yes")
    center_gravity = pm.praat.call(Spectrum_name_part, "Get centre of gravity", 2)
    max_frequency = pm.praat.call(Spectrum_name_part, "Get highest frequency")
    hammarberg_index = pm.praat.call(Spectrum_name_part, "Get band energy difference", 2000, 5000, 0, 2000)
    energy500Hz = pm.praat.call(Spectrum_name_part, "Get band energy", 0, 500)
    energy1000Hz = pm.praat.call(Spectrum_name_part, "Get band energy", 0, 1000)
    total_energy = pm.praat.call(Spectrum_name_part, "Get band energy", 0, max_frequency)
    energy500Hz = energy500Hz / total_energy
    energy1000Hz = energy1000Hz / total_energy

    mean_h1_h2 = np.nanmean(voice_dict['mean_h1_h2_'][m])
    mean_h1_H2 = np.nanmean(voice_dict['mean_h1_H2_'][m])
    mean_h1_A1 = np.nanmean(voice_dict['mean_h1_A1_'][m])
    mean_h1_A3 = np.nanmean(voice_dict['mean_h1_A3_'][m])
    mean_cpp = np.nanmean(voice_dict['mean_cpp_'][m])

    bidline = label + '\t' + str(mean_h1_h2) + '\t' + str(mean_h1_H2) + '\t' + str(mean_h1_A1) + '\t' + str(mean_h1_A3) + '\t' + str(mean_cpp) 
    bidline = bidline + str(center_gravity) + '\t' + str(hammarberg_index) + '\t' + str(energy500Hz) + '\t' + str(energy1000Hz) + '\t' 
    bidline = bidline + str(dispersion1_3) + '\t' + str(dispersion1_5) + '\t' + str(median_pitch) + '\t' + str(jitter) + '\t' + str(shimmer) + '\t' 
    bidline = bidline + str(harmonicity) + '\t' + energyline 

    return bidline



def FormantCorrection(Formant_name, f0, time_point, sf, h):
# Based on Iseli, M., Shue, Y.-L. and Alwan, A. (2007). Age, sex, and vowel dependencies of acoustic measures related to the voice source. Journal of the Acoustical Society of America 121: 2283-2295.
    pi = 3.141592653589793
    for w in range(1, 2+1):
        w0 = 2 * pi * f0 * w
        delta = 0
        for i in range(1, 2+1):
            fii = pm.praat.call(Formant_name, "Get value at time", i, time_point, "Hertz", "Linear")
            bi = 80 + 120 * fii / 5000                            #following Iseli et al. 2007
            wi = 2 * pi * fii / sf
            ri = math.exp(-pi * bi / sf)

            delta += 10 * math.log(math.pow((1-2*ri*math.cos(wi)+math.pow(ri,2)),2) / ((1-2*ri*math.cos(w0+wi)+math.pow(ri, 2))*(1-2*ri*math.cos(w0-wi)+math.pow(ri, 2))), 10)
        h[w] -= delta        
    return h


def Voice_normalization(TextGrid_name, Sound_name, PitchTier_name, normtime, name):
    TableOfReal_normtimeVoice = pm.praat.call("Create TableOfReal", "normtimeIntensity", 1, 7)

    TableOfReal_normtimeVoice = pm.praat.call(TableOfReal_normtimeVoice, "To Table", "rowLabel")
    TableOfReal_normtimeVoice = Create_other_tier_columns(TableOfReal_normtimeVoice, TextGrid_name)

    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 2, "Time")
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 3, "H1-H2")   
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 4, "H1*-H2*")
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 5, "CPP")
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 6, "F1")
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 7, "F2")
    pm.praat.call(TableOfReal_normtimeVoice, "Set column label (index)", 8, "F3")
    #pm.praat.call(TableOfReal_normtimeVoice, "Set row label (index)", 1, 'test')

    ncols = pm.praat.call(TableOfReal_normtimeVoice, "Get number of columns")
    colnames = {i+1:pm.praat.call(TableOfReal_normtimeVoice, "Get column label", i+1) for i in range(ncols)}      

    
    sf = pm.praat.call(Sound_name, "Get sampling frequency")
    Formant_name = pm.praat.call(Sound_name, "To Formant (burg)", 0, 5, 5500, 0.025, 50)

    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)

    voice_dict = {'mean_h1_h2_':{},
                   'mean_h1_H2_':{},    
                   'mean_h1_A1_':{},
                   'mean_h1_A3_':{},
                   'mean_cpp_': {},
                 }
    
    intervals_found = 0
    nrows = 0
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)        
        if label not in empty_intevals or n_intervals == 1:
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length      
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)
            f0 = pm.praat.call(PitchTier_name, "Get value at time", normtime)

            duration = end - start
            time_step = duration / (npoints - 1)
            if not intervals_found:
                firstime = start1
                intervals_found = 1

            voice_dict['mean_h1_h2_'][m] = []
            voice_dict['mean_h1_H2_'][m] = []
            voice_dict['mean_h1_A1_'][m] = []
            voice_dict['mean_h1_A3_'][m] = []
            voice_dict['mean_cpp_'][m] = []
            

            for x in range(0, npoints):
                normtime = start1 + duration * x / npoints

                f1 = pm.praat.call(Formant_name, "Get value at time", 1, normtime, "Hertz", "Linear")      
                f2 = pm.praat.call(Formant_name, "Get value at time", 2, normtime, "Hertz", "Linear") 
                f3 = pm.praat.call(Formant_name, "Get value at time", 3, normtime, "Hertz", "Linear") 

                if end - normtime < 0.125:
                    window_start = end - 0.25
                else:
                    window_start = normtime - 0.125
                if normtime - start1 < 0.125:
                    window_end = start1 + 0.25
                else:
                    window_end = normtime + 0.125     
                Sound_name_part = pm.praat.call(Sound_name, "Extract part", window_start, window_end, "Rectangular", 1, "yes")
                Spectrum_name_part = pm.praat.call(Sound_name_part, "To Spectrum", "yes")
                PowerCepstrum_name_part = pm.praat.call(Spectrum_name_part, "To PowerCepstrum")
                cpp = pm.praat.call(PowerCepstrum_name_part, "Get peak prominence", 60, 333.3, "Parabolic", 0.001, 0.05, "Exponential decay", "Robust slow")
                SpectrumTier_name_part = pm.praat.call(Spectrum_name_part, "To SpectrumTier (peaks)")
                Table_name_part =  pm.praat.call(SpectrumTier_name_part, "Down to Table")
                nrows = pm.praat.call(Table_name_part, "Get number of rows")
                frequency_step = nrows / sf
                f = float(pm.praat.call(Table_name_part, "Get value", 1, "freq(Hz)"))
                row = 1
                while f < f0:
                    row += 1
                    f = float(pm.praat.call(Table_name_part, "Get value", row, "freq(Hz)"))
                h1 = -32767
                for r in range(row - 5, row + 6):
                    r1 = copy.copy(r)
                    if r < 1:
                        r1 = 1
                    a = float(pm.praat.call(Table_name_part, "Get value", r1, "pow(dB/Hz)"))

                    if a > h1:
                        h1 = a

                while f < f0 * 2:
                    row += 1
                    f = float(pm.praat.call(Table_name_part, "Get value", row, "freq(Hz)"))
                h2 = -32767
                for r in range(row-5, row+6):
                    r1 = copy.copy(r)
                    if r < 1:
                        r1 = 1
                    a = float(pm.praat.call(Table_name_part, "Get value", r1, "pow(dB/Hz)"))

                    if a > h2:
                        h2 = a
                        
                if not math.isnan(f1):
                    f = float(pm.praat.call(Table_name_part, "Get value", 1, "freq(Hz)"))
                    row = 1
                    while f < f1:
                        row += 1
                        if row > nrows:
                            print("f1 = ", f1)
                        f = float(pm.praat.call(Table_name_part, "Get value", row, "freq(Hz)"))
                    a1 = -32767
                    for r in range(row-5, row+6):
                        r1 = copy.copy(r)
                        if r < 1:
                            r1 = 1
                        a = float(pm.praat.call(Table_name_part, "Get value", r1, "pow(dB/Hz)"))
                        if a > a1:
                            a1 = a
                    h1_A1 = h1 - a1
                else:
                    h1_A1 = math.nan

                
                if not math.isnan(f3):
                    while f < f3:
                        row += 1
                        f = float(pm.praat.call(Table_name_part, "Get value", row, "freq(Hz)"))
                    a3 = -32767
                    for r in range(row-5, row+6):
                        r1 = copy.copy(r)
                        if r > 1:
                            r1 = 1
                        a = float(pm.praat.call(Table_name_part, "Get value", r1, "pow(dB/Hz)"))
                        if a > a3:
                            a3 = a
                    h1_A3 = h1 - a3
                else:
                    h1_A3 = math.nan  

                h1_h2 = h1 - h2
                h = {1:h1, 2:h2}
                h = FormantCorrection(Formant_name, f0, normtime, sf, h)
                h1_H2 = h[1] - h[2]

                nrows = pm.praat.call(TableOfReal_normtimeVoice, "Get number of rows")
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[2], normtime)
                if set_initial_normalized_time_to_0:
                    pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[2], normtime-firstime)
    
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[3], h1_h2)
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[4], h1_H2)
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[5], cpp)
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[6], f1)
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[7], f2)
                pm.praat.call(TableOfReal_normtimeVoice, "Set numeric value", nrows, colnames[8], f3)
                TableOfReal_normtimeIntensity = Fill_other_tier_columns(TableOfReal_normtimeVoice, TextGrid_name, start1, nrows, colnames)

                new_label = label.replace(" ", "_")
                pm.praat.call(TableOfReal_normtimeVoice, "Set string value", nrows, 'rowLabel', new_label)
                pm.praat.call(TableOfReal_normtimeVoice, "Insert row", nrows + 1)     

                voice_dict['mean_h1_h2_'][m].append(h1_h2)
                voice_dict['mean_h1_H2_'][m].append(h1_H2)
                voice_dict['mean_h1_A1_'][m].append(h1_A1)
                voice_dict['mean_h1_A3_'][m].append(h1_A3)
                voice_dict['mean_cpp_'][m].append(cpp)
            #voice_dict['mean_h1_h2_'][m] /= npoints
            #voice_dict['mean_h1_H2_'][m] /= npoints
            #voice_dict['mean_h1_A1_'][m] /= npoints
            #voice_dict['mean_h1_A3_'][m] /= npoints
            #voice_dict['mean_cpp_'][m] /= npoints
            
    if nrows > 1:
        pm.praat.call(TableOfReal_normtimeVoice, "Remove row", nrows + 1)                      
                        
    
    return TableOfReal_normtimeVoice, voice_dict

def Trimformants(FormantTier_name):
    maxbump = 0.01  
    maxedge = 0.0
    maxgap = 0.033
    n = pm.praat.call(FormantTier_name, "Get number of points")
    tfirst = pm.praat.call(FormantTier_name, "Get time from index", 1) 
    tlast = pm.praat.call(FormantTier_name, "Get time from index", n)
    for k in range(0,3):
        for m in range(1,6):
            FormantTier_name = Trimformant(FormantTier_name, n, maxbump, maxedge, maxgap, m)
    return FormantTier_name

def Trimformant(FormantTier_name, n, maxbump, maxedge, maxgap, m):

    for i in range(2,n):

        tleft = pm.praat.call(FormantTier_name, "Get time from index", i-1)
        tmid = pm.praat.call(FormantTier_name, "Get time from index", i)
        tright = pm.praat.call(FormantTier_name, "Get time from index", i+1)
        gap1 = tmid - tleft
        gap2 = tright - tmid
        left = pm.praat.call(FormantTier_name, "Get value at time", m, tleft)
        mid = pm.praat.call(FormantTier_name, "Get value at time", m, tmid)
        right = pm.praat.call(FormantTier_name, "Get value at time", m, tright)

        f = {}
        b = {}

        for fx in range(1,6):       
            f[fx] = pm.praat.call(FormantTier_name, "Get value at time", fx, tmid)
            b[fx] = pm.praat.call(FormantTier_name, "Get bandwidth at time", fx, tmid)

        
        diff1 = mid - left
        diff2 = mid - right

        if (diff1 > maxbump and diff2 > maxedge and gap1 < maxgap and gap2 < maxgap) or (diff2 > maxbump and diff1 > maxedge and gap1 < maxgap and gap2 < maxgap):
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))

        if diff1 > maxbump and gap2 >= maxgap:
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))


        if diff2 > maxbump and gap1 >= maxgap:
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))


        diff1 = left - mid
        diff2 = right - mid
        if (diff1 > maxbump and diff2 > maxedge and gap1 < maxgap and gap2 < maxgap) or (diff2 > maxbump and diff1 > maxedge and gap1 < maxgap and gap2 < maxgap):
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))

        if diff1 > maxbump and gap2 >= maxgap:
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))
            
        if diff2 > maxbump and gap1 >= maxgap:
            if not math.isnan(f[m]) and not math.isnan(b[m]):
                pm.praat.call(FormantTier_name, "Remove point", i)
                pm.praat.call(FormantTier_name, "Add point", tmid, ' '.join([str(f[1]), str(b[1]), str(f[2]), str(b[2]), str(f[3]), str(b[3]), 
                                                                       str(f[4]), str(b[4]), str(f[5]), str(b[5])]))

    return FormantTier_name

def hertzToSemitones(hz):
    return 12 * math.log(hz/100) / math.log(2)
    
def Means(Sound_name, TextGrid_name, PitchTier_name, PitchTier_velocity, voice_dict):
    last_dispersion = 0
    Intensity_name = pm.praat.call(Sound_name, "To Intensity", 100, 0, "yes")

    if get_BID_measures:
        Formant_name = pm.praat.call(Sound_name, "To Formant (burg)", 0, 5, 5000, 0.025, 50)
        FormantTier_name = pm.praat.call(Formant_name, "Down to FormantTier")
        FormantTier_name = Trimformants(FormantTier_name)
        TableOfReal_trimmed_formant = pm.praat.call(FormantTier_name, "Down to TableOfReal", "yes", "no")
        Harmonicity_name = pm.praat.call(Sound_name, "To Harmonicity (cc)",  0.01, 75, 0.1, 1)
    

    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    TableOfReal_means = pm.praat.call("Create TableOfReal", "mean", 1, 11)

    pm.praat.call(TableOfReal_means, "Set column label (index)", 1, "maxf0")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 2, "minf0")   
    pm.praat.call(TableOfReal_means, "Set column label (index)", 3, "excursion_size")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 4, "meanf0")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 5, "finalf0")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 6, "mean_intensity")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 7, "duration")    
    pm.praat.call(TableOfReal_means, "Set column label (index)", 8, "max_velocity")
    pm.praat.call(TableOfReal_means, "Set column label (index)", 9, "final_velocity")    
    pm.praat.call(TableOfReal_means, "Set column label (index)", 10, "maxf0_loc_ms")    
    pm.praat.call(TableOfReal_means, "Set column label (index)", 11, "maxf0_loc_ratio")    

    if get_BID_measures:
        energytitle = "Energy_Profile__" + str(energy_band_step_size)+  "Hz"
        center = energy_band_step_size
        for band in range(1,16):
            energytitle = energytitle + '\t' + str(round(center))
            center += 0.5*energy_band_size
        titleline = name + '\th1-h2\th1*-h2*\tH1-A1\tH1-A3\tcpp\tcenter_of_gravity\tHammarberg_index\tenergy_below_500Hz\t'
        titleline = titleline + 'energy_below_1000Hz\tF_dispersion1_3\tF_dispersion1_5\tmedian_pitch\tjitter\tshimmer\tharmonicity\t' + energytitle
        if len(other_tiers) > 0:
            for other_tier in other_tiers:
                tier_label = pm.praat.call(TextGrid_name, "Get tier name", other_tier)
                titleline = titleline + '\t' + tier_label
            center += 0.5*energy_band_size
        
        BID_outfile = open(os.path.join(directory, name + '.BID'), 'w', encoding = 'utf-8')
        BID_outfile.write(titleline + '\n')

    
    interval = 0
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)
        if label not in empty_intevals or n_intervals == 1:
            interval = interval + 1
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length      
            end = pm.praat.call(TextGrid_name, "Get end point", target_tier, m)
            duration = 1000 * (end - start1)        
            new_label = label.replace(" ", "_")            
            pm.praat.call(TableOfReal_means, "Set row label (index)", interval, new_label)
            meanf0 = pm.praat.call(PitchTier_name, "Get mean (points)", start1, end)
            early_end = end + final_offset
            finalf0 = pm.praat.call(PitchTier_name, "Get value at time", early_end)
            Pitch_name = pm.praat.call(PitchTier_name, "To Pitch", 0.02, 30, 600)
            maxf0 = pm.praat.call(Pitch_name, "Get maximum", start1, end, "Hertz", "Parabolic")
            minf0 = pm.praat.call(Pitch_name, "Get minimum", start1, end, "Hertz", "Parabolic")
            peakTime = pm.praat.call(Pitch_name, "Get time of maximum", start1, end, "Hertz", "Parabolic")
            maxf0_loc_ms = 1000 * (peakTime - start1)
            maxf0_loc_ratio = maxf0_loc_ms / duration
            excursionsize = hertzToSemitones(maxf0) - hertzToSemitones(minf0)
            intensity = pm.praat.call(Intensity_name, "Get mean", start1, end, "energy")
            final_velocity = pm.praat.call(PitchTier_velocity, "Get value at time", early_end)
            index_first = pm.praat.call(PitchTier_velocity, "Get high index from time", start1)
            index_last = pm.praat.call(PitchTier_velocity, "Get low index from time", end)
            maxvelocity = 0
            for x in range(index_first, index_last + 1):
                v = pm.praat.call(PitchTier_velocity, "Get value at index", x)
                if abs(v) > abs(maxvelocity):
                    maxvelocity = v

            if get_BID_measures:
                bidline = BID_measures(start1, end, m, name, label, Sound_name, Pitch_name, FormantTier_name, Harmonicity_name, voice_dict)
                if len(other_tiers) > 0:
                    for i in range(len(other_tiers)):
                        interval_int = pm.praat.call(TextGrid_name, "Get interval at time", other_tiers[i], start1 - perturbation_length)
                        interval_label = pm.praat.call(TextGrid_name, "Get label of interval", other_tiers[i], interval_int)
                        bidline = bidline + '\t' + interval_label
                
                BID_outfile.write(bidline + '\n')


            
            pm.praat.call(TableOfReal_means, "Set value", interval, 1, maxf0)
            pm.praat.call(TableOfReal_means, "Set value", interval, 2, minf0)
            pm.praat.call(TableOfReal_means, "Set value", interval, 3, excursionsize)
            pm.praat.call(TableOfReal_means, "Set value", interval, 4, meanf0)
            pm.praat.call(TableOfReal_means, "Set value", interval, 5, finalf0)
            pm.praat.call(TableOfReal_means, "Set value", interval, 6, intensity)
            pm.praat.call(TableOfReal_means, "Set value", interval, 7, duration)
            pm.praat.call(TableOfReal_means, "Set value", interval, 8, maxvelocity)
            pm.praat.call(TableOfReal_means, "Set value", interval, 9, final_velocity)
            pm.praat.call(TableOfReal_means, "Set value", interval, 10, maxf0_loc_ms)
            pm.praat.call(TableOfReal_means, "Set value", interval, 11, maxf0_loc_ratio)
            pm.praat.call(TableOfReal_means, "Insert row (index)", interval + 1)

    nrows = pm.praat.call(TableOfReal_means, "Get number of rows")
    if nrows > 1:
        pm.praat.call(TableOfReal_means, "Remove row (index)", nrows)

    Table_means = pm.praat.call(TableOfReal_means, "To Table", "rowLabel")
    Table_means = Create_other_tier_columns(Table_means, TextGrid_name)

    ncols = pm.praat.call(Table_means, "Get number of columns")
    colnames = {i+1:pm.praat.call(Table_means, "Get column label", i+1) for i in range(ncols)}
    interval = 0
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)
        if label not in empty_intevals or n_intervals == 1:
            interval += 1
            start = pm.praat.call(TextGrid_name, "Get starting point", target_tier, m)
            start1 = start + perturbation_length      
            Table_means = Fill_other_tier_columns(Table_means, TextGrid_name, start1, interval, colnames)

    if get_BID_measures:
        BID_outfile.close()
    
    return TableOfReal_means, Table_means

def save(directory, name, Sound_name, TextGrid_name, PointProcess_name):
   
    voice_dict = {}
   
    nintervals = pm.praat.call(TextGrid_name, "Get number of intervals", target_tier)
    for m in range(1, nintervals+1):
        label = pm.praat.call(TextGrid_name, "Get label of interval", target_tier, m)

        if label not in empty_intevals or n_intervals == 1:
            found_interval = True
    if save_output_files:
        npulses = pm.praat.call(PointProcess_name, "Get number of points")
        for n in range(2,npulses):
            time1 = pm.praat.call(PointProcess_name, "Get time from index", n-1)
            time2 = pm.praat.call(PointProcess_name, "Get time from index", n)
            if time2 - time1 < 0.001:
                pm.praat.call(PointProcess, "Remove point", n)
        pm.praat.call(PointProcess_name, "Write to short text file", os.path.join(directory, name + '.pulse'))

        maxperiod = 0.02
        PitchTier_name = pm.praat.call(PointProcess_name, "To PitchTier", 0.02)
        if npulses > 1:
            TableOfReal = pm.praat.call(PitchTier_name, "Down to TableOfReal", "Hertz")
            pm.praat.call(TableOfReal, "Write to headerless spreadsheet file", os.path.join(directory, name + '.rawf0'))
        else:
            print("file needs to have more than three pulse marks")   


        PitchTier_name = Trimf0(PitchTier_name, npulses)
        pm.praat.call(PitchTier_name, "Write to short text file", os.path.join(directory, name + '.PitchTier'))
        TableOfReal = pm.praat.call(PitchTier_name, "Down to TableOfReal", "Hertz")
        pm.praat.call(TableOfReal, "Write to headerless spreadsheet file", os.path.join(directory, name + '.f0'))    


        PitchTier_samplef0, PitchTier_smoothf0, TableOfReal_smoothf0, sampleStart, sampleEnd = Sampling(PitchTier_name, TextGrid_name)
        if nintervals == 1:
            print("\n\nNo labeled intervals. Generating entire f0 track instead!\n\n")
            print("\n\nNo Note that this is not very useful for most purposes.\n\n")
            
        if smoothing_window_width > 0:
            PitchTier_semitonef0 = copy.copy(PitchTier_smoothf0)
        else:
            PitchTier_semitonef0 = copy.copy(PitchTier_samplef0)
        TableOfReal_samplef0 = pm.praat.call(PitchTier_samplef0, "Down to TableOfReal", "Hertz")
        pm.praat.call(PitchTier_semitonef0, "Formula", "12 * ln (self) / ln(2)")
        TableOfReal_semitonef0 = pm.praat.call(PitchTier_semitonef0, "Down to TableOfReal", "Hertz")
        pm.praat.call(TableOfReal_semitonef0, "Set column label (index)", 1, "time")
        pm.praat.call(TableOfReal_semitonef0, "Set column label (index)", 2, "f0 (st)")

        PitchTier_velocity, TableOfReal_velocity, TableOfReal_semitonef0, TableOfReal_smoothf0 = Differentiation(PitchTier_semitonef0, 
                                                                                                                 TableOfReal_semitonef0,
                                                                                                                 npulses, TableOfReal_smoothf0,
                                                                                                                sampleStart, sampleEnd,
                                                                                                                TextGrid_name)
        if found_interval:
            pm.praat.call(TableOfReal_samplef0, "Write to headerless spreadsheet file", os.path.join(directory, name + '.samplef0'))
            pm.praat.call(TableOfReal_velocity, "Write to headerless spreadsheet file", os.path.join(directory, name + '.f0velocity'))

            PitchTier_acceleration, TableOfReal_acceleration, TableOfReal_velocity, TableOfReal_smoothf0 = Differentiation(PitchTier_velocity, 
                                                                                                                             TableOfReal_velocity,
                                                                                                                     npulses, TableOfReal_smoothf0,
                                                                                                                            sampleStart, sampleEnd,
                                                                                                                            TextGrid_name)
            
            pm.praat.call(TableOfReal_acceleration, "Write to headerless spreadsheet file", os.path.join(directory, name + '.accelerationf0'))
            pm.praat.call(TableOfReal_semitonef0, "Write to headerless spreadsheet file", os.path.join(directory, name + '.semitonef0'))
            if smoothing_window_width > 0:
                pm.praat.call(TableOfReal_smoothf0, "Write to headerless spreadsheet file", os.path.join(directory, name + '.smoothf0'))
          

        PitchTier_smoothf0, TableOfReal_normf0, TableOfReal_normactuf0 = Normalization(PitchTier_smoothf0, TextGrid_name)
        PitchTier_semitonef0, TableOfReal_normtime_semitonef0, TableOfReal_normactutime_semitonef0 = Normalization(PitchTier_semitonef0, TextGrid_name)
        PitchTier_velocity, TableOfReal_normtime_f0velocity, TableOfReal_normactutime_f0velocity = Normalization(PitchTier_velocity, TextGrid_name)
        PitchTier_acceleration, TableOfReal_normtime_f0acceleration, TableOfReal_normactutime_f0acceleration = Normalization(PitchTier_acceleration, TextGrid_name)

        TableOfReal_normtimeIntensity, normtime = Intensity_normalization(TextGrid_name, Sound_name)
        if get_BID_measures:
            TableOfReal_normtimeVoice, voice_dict = Voice_normalization(TextGrid_name, Sound_name, PitchTier_name, normtime, name)

        if found_interval:
            pm.praat.call(TableOfReal_normf0, "Save as tab-separated file", os.path.join(directory, name + '.normtimef0'))
            pm.praat.call(TableOfReal_normtime_semitonef0, "Save as tab-separated file", os.path.join(directory, name + '.normtime_semitonef0'))
            pm.praat.call(TableOfReal_normtime_f0velocity, "Save as tab-separated file", os.path.join(directory, name + '.normtime_f0velocity'))
            pm.praat.call(TableOfReal_normtime_f0acceleration, "Save as tab-separated file", os.path.join(directory, name + '.normtime_f0acceleration'))
            pm.praat.call(TableOfReal_normactuf0, "Save as tab-separated file", os.path.join(directory, name + '.actutimenormf0'))
            pm.praat.call(TableOfReal_normactutime_semitonef0, "Save as tab-separated file", os.path.join(directory, name + '.actutimesemitonef0'))
            pm.praat.call(TableOfReal_normtime_f0velocity, "Save as tab-separated file", os.path.join(directory, name + '.actutimef0velocity'))
            pm.praat.call(TableOfReal_normtime_f0acceleration, "Save as tab-separated file", os.path.join(directory, name + '.actutimef0acceleration'))
            pm.praat.call(TableOfReal_normtimeIntensity, "Save as tab-separated file", os.path.join(directory, name + '.normtimeIntensity'))
            if get_BID_measures:
                pm.praat.call(TableOfReal_normtimeVoice, "Save as tab-separated file", os.path.join(directory, name + '.normtimeVoice'))

        

        TableOfReal_means, Table_means = Means(Sound_name, TextGrid_name, PitchTier_name, PitchTier_velocity, voice_dict)
        pm.praat.call(TableOfReal_means, "Write to headerless spreadsheet file", os.path.join(directory, name + '.means'))
        pm.praat.call(Table_means, "Save as tab-separated file", os.path.join(directory, name + '.meansMoreTiers'))


        



for wav_file in soundfiles:
    name, Sound_name, TextGrid_name, PointProcess_name = Labeling(directory, wav_file)
    print("processing " + name + " now...")
    save(directory, name, Sound_name, TextGrid_name, PointProcess_name)
