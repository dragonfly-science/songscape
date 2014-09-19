#scores <- read.csv('scores.csv')

analysed <- scores[!is.na(scores$analysis_id), ]
scores <- with(scores[!is.na(scores$analysis_id), ], rbind(tapply(peak, site, length), tapply(male_kiwi, site, sum), tapply(female_kiwi, site, sum) ))

