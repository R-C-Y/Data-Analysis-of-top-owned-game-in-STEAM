#1. Which developer has worked on the most games(select top5)?
SELECT Developer, COUNT(GameID) AS TotalGames
FROM Developers d
JOIN Developer_and_Games dg ON d.Developer_ID = dg.Developer_ID
GROUP BY Developer
ORDER BY TotalGames DESC
limit 5;

#2. Which publisher has worked on the most games(select top5)?
SELECT Publisher, COUNT(pg.GameID) AS PublishedGames
FROM Publishers p
JOIN Publisher_and_Games pg ON p.Publisher_ID = pg.Publisher_ID
GROUP BY Publisher
ORDER BY PublishedGames DESC
LIMIT 5;


#3. What is the average price of each genre of game?
SELECT g.Genres, AVG(game.Price) AS AvgPrice
FROM Games game
JOIN Genres_and_Games gag ON game.GameID = gag.GameID
JOIN Genres g ON gag.Genre_ID = g.Genre_ID
GROUP BY g.Genres
ORDER BY AvgPrice DESC;


#4. Which game has the greatest difference between positive and negative reviews and its genre?
SELECT 
    g.Name, 
    g.Positive - g.Negative AS CommentDifference,
    GROUP_CONCAT(gen.Genres) AS Genres
FROM (
    SELECT Name, Positive, Negative,
           RANK() OVER (ORDER BY Positive - Negative DESC) AS Ranking,
           GameID
    FROM Games
) g
JOIN Genres_and_Games gag ON g.GameID = gag.GameID
JOIN Genres gen ON gag.Genre_ID = gen.Genre_ID
WHERE g.Ranking <= 5
GROUP BY g.Name, CommentDifference;


#5.	For games that support multiple platforms, which game types (Genres) have the longest average playtime (Playtime)?
SELECT 
    g.Genres,
    AVG(game.Average_playtime_forever) AS AvgPlaytime
FROM Games game
JOIN Genres_and_Games gag ON game.GameID = gag.GameID
JOIN Genres g ON gag.Genre_ID = g.Genre_ID
JOIN Platform p ON game.GameID = p.GameID
WHERE p.Supports_Multiple_Platforms = 'YES'
GROUP BY g.Genres
ORDER BY AvgPlaytime DESC
LIMIT 5;



#6.	Which genres have the highest gross revenues? Which genres contribute the top 50% of total revenue?
WITH GenreRevenue AS (
    SELECT g.Genres, SUM(game.Price * game.Estimated_owners) AS TotalRevenue
    FROM Games game
    JOIN Genres_and_Games gag ON game.GameID = gag.GameID
    JOIN Genres g ON gag.Genre_ID = g.Genre_ID
    GROUP BY g.Genres
),
CumulativeRevenue AS (
    SELECT Genres, TotalRevenue,
           SUM(TotalRevenue) OVER (ORDER BY TotalRevenue DESC) AS CumulativeRevenue,
           SUM(TotalRevenue) OVER () AS GrandTotalRevenue
    FROM GenreRevenue
)
SELECT Genres, TotalRevenue
FROM CumulativeRevenue
WHERE CumulativeRevenue <= 0.5 * GrandTotalRevenue;

#7. What is the percentage distribution of positive and negative reviews among the games supported by only one platform or multiply ones?
SELECT 
    Supports_Multiple_Platforms AS PlatformType,
    SUM(g.Positive) AS TotalPositiveComments,
    SUM(g.Negative) AS TotalNegativeComments,
    ROUND(SUM(g.Positive) * 100.0 / NULLIF(SUM(g.Positive) + SUM(g.Negative), 0), 2) AS PositiveCommentPercentage,
    ROUND(SUM(g.Negative) * 100.0 / NULLIF(SUM(g.Positive) + SUM(g.Negative), 0), 2) AS NegativeCommentPercentage
FROM Games g
JOIN Platform p ON g.GameID = p.GameID
GROUP BY Supports_Multiple_Platforms;


#8.	What types of games perform best in terms of average play length and what percentage of those games are priced above the average price of all games?
WITH AveragePrice AS (
    SELECT AVG(Price) AS GlobalAveragePrice
    FROM Games
),
GenrePlaytime AS (
    SELECT 
        g.Genres,
        AVG(game.Average_playtime_forever) AS AvgPlaytime,
        COUNT(CASE WHEN game.Price > (SELECT GlobalAveragePrice FROM AveragePrice) THEN 1 END) * 100.0 / COUNT(*) AS AboveAveragePricePercentage
    FROM Games game
    JOIN Genres_and_Games gag ON game.GameID = gag.GameID
    JOIN Genres g ON gag.Genre_ID = g.Genre_ID
    GROUP BY g.Genres
)
SELECT Genres, AvgPlaytime, AboveAveragePricePercentage
FROM GenrePlaytime
ORDER BY AvgPlaytime DESC;



