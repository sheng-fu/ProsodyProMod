# ProsodyProMod

Modifications to ProsodyPro

**Find the original script and descriptions at** 
http://www.homepages.ucl.ac.uk/~uclyyix/ProsodyPro/

**To cite the tool**:
Xu, Y. (2013). ProsodyPro — A Tool for Large-scale Systematic Prosody Analysis. In Proceedings of Tools and Resources for the Analysis of Speech Prosody (TRASP 2013), Aix-en-Provence, France. 7-10.

------

## Python version (ProsodyProMod.py)

Implementation of the "Process all sounds without pause" option in the original script <br>

+ Required libraries
  + praat-parselmouth ([link](https://parselmouth.readthedocs.io/en/stable/))
  + numpy

### Example Usage
```
python ProsodyProMod.py -directory DIRECTORY -target_tier 1 -get_BID_measures 1 -set_initial_normalized_time_to_0 0
```

### Modifications 
+ Added an option to extract annotations from other tiers to the following (series) of files (e.g., ```-other_tiers 2,3```)
  + .actutimeX 
  + .normtimeX
  + .means (as .meansMoreTiers)
  + .BID
+ Added raw formant measurements (F1, F2, F3) to .normtimeVoice
+ Added an option to adjust threshold for trimming F0 and formants (```-trim_if_bump_above_Hz```); defaults to 0.01 as the variable 'maxbump' in the original script
+ Means of voice measurements are calculated by ignoring undefined values

### Notes

+ CPP measurements might differ from running the .Praat version (in .means, .meansMoreTiers, .normtimeVoice)
  + Issue with "Get peak prominence" on PowerCepstrum objects returning different results with Interpolation other than "none"



## Praat script version (_ProsodyProMod.praat)

### Modifications 

+ Added raw formant measurements (F1, F2, F3) to .normtimeVoice
+ Added an option to adjust threshold for trimming F0 and formants, i.e., the "maxbump" parameter in the original script (in "trim_if_bump_above_Hz" in extra_options); defaults to 0.01 as the variable 'maxbump' in the original script
+ .BID and “Get ensemble files” outputs are saved to the selected folder when ```Choose_working_folder = 1```
+ Outputs of “Average across speakers” are saved to specified folders 




