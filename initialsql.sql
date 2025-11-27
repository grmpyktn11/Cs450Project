CREATE TABLE Game (
    steamAppId NUMBER PRIMARY KEY,
    gameName VARCHAR2(200) NOT NULL,
    steamUrl VARCHAR2(500),
    basePrice NUMBER(10,2) NOT NULL CHECK (basePrice >= 0),
    currPrice NUMBER(10,2) NOT NULL CHECK (currPrice >= 0),
    rating NUMBER(5,2) CHECK (rating >= 0 AND rating <= 100),
    genre VARCHAR2(100),
    releaseDate DATE,
    description VARCHAR2(1000)
);

CREATE TABLE PriceHistory (
    priceHistoryID NUMBER PRIMARY KEY,
    steamAppId NUMBER NOT NULL UNIQUE, 
    originalPrice NUMBER(10,2) NOT NULL CHECK (originalPrice >= 0),
    allTimeLow NUMBER(10,2) NOT NULL CHECK (allTimeLow >= 0),
    currentPrice NUMBER(10,2) NOT NULL CHECK (currentPrice >= 0),

    CONSTRAINT fk_pricehistory_game
        FOREIGN KEY (steamAppId)
        REFERENCES Game(steamAppId)
);


COMMIT;