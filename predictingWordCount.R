library(tidyverse)
library(stringr)
library(caTools)
library(car)
library(quantmod)
library(MASS)
library(corrplot)

naruto = read_csv("C:\\Users\\saipr\\Desktop\\Programming\\ao3Models\\naruto.csv")
head(naruto)
y = naruto$words

#Step 1: Clean and finalize our variables
#int: number of characters, relationships, freeforms
narutoCleaned = naruto %>% 
  mutate(numChar = rapply(str_split(characters, ","), length, how = "unlist")) %>%
  mutate(numRel = rapply(str_split(relationships, ","), length, how = "unlist")) %>%
  mutate(numFree = rapply(str_split(freeforms, ","), length, how = "unlist")) %>%
#booleans: is it slow burn, alternate universe, hurt comfort, crack
  mutate(isSlowBurn = grepl("slow burn", freeforms, ignore.case = TRUE)) %>%
  mutate(isAU = grepl("AU|Alternate Universe", freeforms, ignore.case = TRUE)) %>%
  mutate(isHurtComfort = grepl("Hurt/Comfort|Hurt and Comfort", freeforms, ignore.case = TRUE)) %>%
  mutate(isCrack = grepl("crack|crackfic", freeforms, ignore.case = TRUE)) %>%
  mutate(isNonProse = grepl("podcast|art|comic|chatfic", freeforms, ignore.case = TRUE)) %>%
  mutate(isFixItFic = grepl("fix it|fix-it", freeforms, ignore.case = TRUE)) %>%
#scale / normalize everything that's numeric
  mutate_if(is.numeric, scale) %>%
#drop fandoms, relationships, characters, freeforms, index, names AND dependent variable Words
  subset(select = -c(relationships, freeforms, characters, ...1, names, fandoms, words))
#factorize ratings, warnings, anything else that's still a string
narutoCleaned <- as.data.frame(unclass(narutoCleaned), stringsAsFactors = TRUE)
narutoCleaned$words <- y

#our most basic linear model
modelWords = lm(words ~., data = narutoCleaned)
summary(modelWords)
#check for multicor
vif(modelWords)


#NOTE THE FOLLOWING:
  #Kudos and bookmarks are multicolinear by a fair amount - and while both are significant, we're dropping bookmarks because it's lesso
  #we're also dropping the booleans because none of them, as well as the num of char, rel, free, war ended up being significant
  #the warnings are all multicollinear, but two of them seem to matter - if they used all four warnings, or if they used no warnings at all
  #similarly only one rating matters - if its gen
narutoCleaned = narutoCleaned %>%
  mutate(isNoWarnings = grepl("Choose Not To Use Archive Warnings, No Archive Warnings Apply", warnings, ignore.case = TRUE))%>% 
  mutate(isAllWarnings = grepl("Graphic Depictions Of Violence, Major Character Death, Rape/Non-Con, Underage", warnings, ignore.case = TRUE))%>%
  mutate(isGen = grepl("General Audiences", ratings, ignore.case = TRUE))%>%
  subset(select = -c(bookmarks, isSlowBurn, isAU, isHurtComfort, isCrack, isNonProse, isFixItFic, numChar, numRel, numFree, warnings, ratings, collections, kudos))

#Try number 2
#our most basic linear model
modelWords = lm(words ~., data = narutoCleaned)
summary(modelWords)
#check for multicor
vif(modelWords)