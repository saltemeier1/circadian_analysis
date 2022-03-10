circadianAnalysis.py takes raw data from Philips Spectrum Pro watch and creates csv file that contains the activity for each minute of each day.
Each row represents a new day while each column represents a new minute of activity.

RUNNING circadianAnalysis.py:::::::::::::::::::::::::::::::::::::::::

Place all csv actigraphy files that you want to be parsed into J:\Actigraphy Data\CircadianScript\Reports.
Then, you can open up the command prompt. Once opened, navigate into the folder that has this script, J:\Actigraphy Data\CircadianScript.
Once in this folder, you can type this into the command prompt window:

python circadianAnalysis.py

After this runs to completion, close the command window. You can now navigate to J:\Actigraphy Data\CircadianScript\Summary using File Explorer.
Here, you should find a new Excel file titled, "Day_Year_Circadian_summary_Hour_Minute" where Day,Year, Hour, and Minute correspond to when you ran this script.
This file holds all the participant data. 