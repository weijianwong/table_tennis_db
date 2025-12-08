-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS after_game_insert;
DROP TRIGGER IF EXISTS after_game_update;
DROP TRIGGER IF EXISTS after_game_delete;

-- Trigger after inserting a new game
DELIMITER $$
CREATE TRIGGER after_game_insert
AFTER INSERT ON Game
FOR EACH ROW
BEGIN
    DECLARE home_wins INT DEFAULT 0;
    DECLARE away_wins INT DEFAULT 0;

    -- Count wins for home and away teams
    SELECT
        SUM(CASE WHEN winner = '主队' THEN 1 ELSE 0 END),
        SUM(CASE WHEN winner = '客队' THEN 1 ELSE 0 END)
    INTO home_wins, away_wins
    FROM Game
    WHERE match_id = NEW.match_id;

    -- Update the Match table with the new score
    UPDATE `Match`
    SET final_score = CONCAT(home_wins, ':', away_wins)
    WHERE match_id = NEW.match_id;
END$$
DELIMITER ;

-- Trigger after updating a game
DELIMITER $$
CREATE TRIGGER after_game_update
AFTER UPDATE ON Game
FOR EACH ROW
BEGIN
    DECLARE home_wins INT DEFAULT 0;
    DECLARE away_wins INT DEFAULT 0;

    -- Count wins for home and away teams
    SELECT
        SUM(CASE WHEN winner = '主队' THEN 1 ELSE 0 END),
        SUM(CASE WHEN winner = '客队' THEN 1 ELSE 0 END)
    INTO home_wins, away_wins
    FROM Game
    WHERE match_id = NEW.match_id;

    -- Update the Match table with the new score
    UPDATE `Match`
    SET final_score = CONCAT(home_wins, ':', away_wins)
    WHERE match_id = NEW.match_id;
END$$
DELIMITER ;

-- Trigger after deleting a game
DELIMITER $$
CREATE TRIGGER after_game_delete
AFTER DELETE ON Game
FOR EACH ROW
BEGIN
    DECLARE home_wins INT DEFAULT 0;
    DECLARE away_wins INT DEFAULT 0;

    -- Count wins for home and away teams
    SELECT
        SUM(CASE WHEN winner = '主队' THEN 1 ELSE 0 END),
        SUM(CASE WHEN winner = '客队' THEN 1 ELSE 0 END)
    INTO home_wins, away_wins
    FROM Game
    WHERE match_id = OLD.match_id;

    -- Update the Match table with the new score
    UPDATE `Match`
    SET final_score = CONCAT(IFNULL(home_wins, 0), ':', IFNULL(away_wins, 0))
    WHERE match_id = OLD.match_id;
END$$
DELIMITER ;