/*
making the genre table first
it has no dependancies to we shoudl make it befoer others
*/

CREATE TABLE Genre (
    genreID NUMBER PRIMARY KEY,
    genreName VARCHAR2(100) NOT NULL UNIQUE,
    description VARCHAR2(500)
);


CREATE TABLE Game (
    steamAppId NUMBER PRIMARY KEY,
    gameName VARCHAR2(200) NOT NULL,
    steamUrl VARCHAR2(500),
    basePrice NUMBER(10,2) NOT NULL CHECK (basePrice >= 0),
    rating NUMBER(5,2) CHECK (rating >= 0 AND rating <= 100),
    releaseDate DATE,
    description VARCHAR2(1000),
    genreID NUMBER NOT NULL UNIQUE,
    CONSTRAINT fk_game_genre FOREIGN KEY (genreID) 
        REFERENCES Genre(genreID)
);

CREATE TABLE PriceHistory (
    priceHistoryID NUMBER PRIMARY KEY,
    steamAppId NUMBER NOT NULL,
    recordedDate DATE NOT NULL,
    discountPercent NUMBER(5,2) DEFAULT 0 
        CHECK (discountPercent >= 0 AND discountPercent <= 100),
    currentPrice NUMBER(10,2) NOT NULL CHECK (currentPrice >= 0),
    CONSTRAINT fk_pricehistory_game FOREIGN KEY (steamAppId) 
        REFERENCES Game(steamAppId),
    CONSTRAINT uk_pricehistory_date UNIQUE (steamAppId, recordedDate)
);

//inserting things into the table
INSERT INTO Genre VALUES (1, 'RPG', 'Role-playing games involving character progression and narrative choices.');
INSERT INTO Genre VALUES (2, 'Simulation', 'Games that simulate real-world or imagined activities.');
INSERT INTO Genre VALUES (3, 'Strategy', 'Games focused on planning, tactics, and resource management.');
INSERT INTO Genre VALUES (4, 'Action', 'Fast-paced games emphasizing reflexes and combat.');

INSERT INTO Game VALUES (
    292030,
    'The Witcher 3: Wild Hunt',
    'https://store.steampowered.com/app/292030',
    39.99,
    93.00,
    TO_DATE('2015-05-19', 'YYYY-MM-DD'),
    'An epic open-world RPG where you play as Geralt of Rivia, a monster hunter.',
    1
);

INSERT INTO Game VALUES (
    427520,
    'Factorio',
    'https://store.steampowered.com/app/427520',
    35.00,
    90.00,
    TO_DATE('2020-08-14', 'YYYY-MM-DD'),
    'A factory-building game focused on resource management and automation.',
    2
);

INSERT INTO Game VALUES (
    570,
    'Dota 2',
    'https://store.steampowered.com/app/570',
    0.00,
    89.00,
    TO_DATE('2013-07-09', 'YYYY-MM-DD'),
    'A multiplayer online battle arena (MOBA) game.',
    3
);

INSERT INTO Game VALUES (
    730,
    'Counter-Strike: Global Offensive',
    'https://store.steampowered.com/app/730',
    0.00,
    87.50,
    TO_DATE('2012-08-21', 'YYYY-MM-DD'),
    'A team-based first-person shooter emphasizing tactics and precision.',
    4
);

INSERT INTO PriceHistory VALUES (1, 292030, TO_DATE('2024-10-01', 'YYYY-MM-DD'), 50.00, 19.99);
INSERT INTO PriceHistory VALUES (2, 292030, TO_DATE('2025-02-01', 'YYYY-MM-DD'), 60.00, 15.99);
INSERT INTO PriceHistory VALUES (3, 427520, TO_DATE('2025-01-01', 'YYYY-MM-DD'), 20.00, 28.00);
INSERT INTO PriceHistory VALUES (4, 570, TO_DATE('2025-03-01', 'YYYY-MM-DD'), 0.00, 0.00);
INSERT INTO PriceHistory VALUES (5, 730, TO_DATE('2025-03-01', 'YYYY-MM-DD'), 0.00, 0.00);



/*test for view price history*/
SELECT ph.recordedDate, ph.discountPercent, ph.currentPrice
FROM PriceHistory ph
JOIN Game g ON ph.steamAppId = g.steamAppId
WHERE g.gameName = 'The Witcher 3: Wild Hunt'
ORDER BY ph.recordedDate;

/*find all the games that are free*/
SELECT gameName, rating
FROM Game
WHERE basePrice = 0;

/*find highest rated game by gnre*/
SELECT ge.genreName, g.gameName, g.rating
FROM Game g
JOIN Genre ge ON g.genreID = ge.genreID
ORDER BY g.rating DESC;

/*average discount per game */
SELECT g.gameName, ROUND(AVG(ph.discountPercent), 2) AS avgDiscount
FROM Game g
JOIN PriceHistory ph ON g.steamAppId = ph.steamAppId
GROUP BY g.gameName
ORDER BY avgDiscount DESC;
