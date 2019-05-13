# geoguessr

These programs let you play customised seasons of GeoGuessr Games.
Pasting the result link into the program it collects all the relevant data from the website
and calculates the points each competitor earned.
It also keeps track (over several seasons) of the players average scores in each country.


Save the three python files to your computer.

You need to run the geo.py file with the following changes:
  - set the variable path to the location of the GeoGuessr.py file on your computer
  - set names to the names of the players you play that geoguessr season against


The plot.py file lets you plot your performance in different countries.
  - set the variable path to the location of the Country_scores.csv file on your computer
  - set name to one of the names of the players


Changes in season length and point system need to be done in the GeoGuessr class found in the Geoguessr.py file.


There might be some issues with players scoring the exact same amount of points.

You should adapt the program if you play every season against in a different group
as the country statistic is collected over all seasons.






##### Point System #######

- In a game of n players the player in first position gets n points, the player in k-th position gets n-k points, i.e
  1st 3 points, 2nd 1 point, 3rd 0 points.
- Every player gets 0.2 points for each correctly guessed country and 1 points for a total score over 20000.
- If the player in the last position scored within 90% of the best score every player expect the first receives
  one extra point.

The player with the most points in the last three games gets three extra points.

Over the course of the season an extra point is awarded to the player who
  - scored most 2nd places
  - had the smallest standard divation in his results
  - had the highest standard divation in his results
  - earned the best last place
  - won with the biggest win margin
  - came second with the biggest margin to third place
  - won the closest game (first to last)
  - won the highest scoring game
  - won the lowest scoring game

The player with the n highest scores get n points.

You are awarded run points if you scored over 12000 points at least 10 times in a row.
For a run of n games you get n-9 points.
Similarily, you obtain run points if you scored over 95% of the average at least 5 times in a row.
