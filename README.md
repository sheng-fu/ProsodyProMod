# ProsodyProMod

Modifications to ProsodyPro

**See original script and descriptions at** 
http://www.homepages.ucl.ac.uk/~uclyyix/ProsodyPro/

**To cite the tool**:
Xu, Y. (2013). ProsodyPro — A Tool for Large-scale Systematic Prosody Analysis. In Proceedings of Tools and Resources for the Analysis of Speech Prosody (TRASP 2013), Aix-en-Provence, France. 7-10.

------

## Python version (ProsodyProMod.py)

Implementation of the "Process all sounds without pause" option in the original script
(via the [Parselmouth](https://parselmouth.readthedocs.io/en/stable/) library)

### Example Usage
```
python ProsodyProMod.py -directory DIRECTORY -target_tier 1 -get_BID_measures 1 -set_initial_normalized_time_to_0 0
```

### Modifications from the original Praat script 
+ An option to add anntotation from other tiers to the following (series) of files (e.g., ```-other_tiers 2,3```)
  + .actutimeX 
  + .normtimeX
  + .means (as .meansMoreTiers)
  + .BID
+ Added raw formant measurements (F1, F2, F3) to .normtimeVoice
+ .BID files now also saved to the folder selected via Choose_working_folder

### Notes
+ means of voice measurements are taken by ignoring undefined values
+ CPP measurements might differ from running the .Praat version (in .means, .meansMoreTiers, .normtimeVoice)
  + Issue with "Get peak prominence" on PowerCepstrum objects returning different results with Interpolation other than "none"



## Praat script version (_ProsodyProMod.praat)

+ Added raw formant measurements (F1, F2, F3) to .normtimeVoice
+ .BID files now also saved to the folder selected via Choose_working_folder



