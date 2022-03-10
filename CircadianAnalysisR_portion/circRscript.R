library(readxl)
library(zoo)
library(ActCR)
getwd()
## dir()

file.list <- list.files(pattern='*.xlsx')
filenames <- c(file.list)

filenames

for (file in filenames)
{
  print(file)
  ## It is important to let R know that in your spreadsheet, NA represents missing
  dat = read_xlsx(file,na = "NaN") 
  
  ## Get only the activity counts
  act_dat = dat[,c(3:1442)]
  
  ## You can simply throw away rows with all NAs
  act_dat = act_dat[rowSums(!is.na(act_dat)) > 0, ]
  
  x = c(t(act_dat))
  act_cr_coef = ActCosinor(x, window = 1)
  print(act_cr_coef)
  
  act_extend_cr_coef = ActExtendCosinor(x, window = 1, lower = c(0, 0, -1, 0, -3),upper = c(Inf, Inf, 1, Inf, 27))
  print(act_extend_cr_coef)
}

## It is important to let R know that in your spreadsheet, NA represents missing
#dat = read_xlsx("EI_1_19_Circadian_Summary_13_8.xlsx",na = "NaN") 

## Get only the activity counts
#act_dat = dat[,c(3:1442)]

## You can simply throw away rows with all NAs
#act_dat = act_dat[rowSums(!is.na(act_dat)) > 0, ]

#x = c(t(act_dat))
#act_cr_coef = ActCosinor(x, window = 1)
#act_cr_coef

#act_extend_cr_coef = ActExtendCosinor(x, window = 1, lower = c(0, 0, -1, 0, -3),upper = c(Inf, Inf, 1, Inf, 27))
#act_extend_cr_coef


