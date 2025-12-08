-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS table_tennis_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE table_tennis_db;

-- 1. 院系表 (College)
CREATE TABLE College (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL UNIQUE,
    contact_person VARCHAR(20),
    phone VARCHAR(15)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 球队表 (Team)
CREATE TABLE Team (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(50) NOT NULL,
    established_year YEAR,
    dept_id INT NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES College(dept_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 球员表 (Player)
CREATE TABLE Player (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    gender ENUM('男', '女') NOT NULL,
    grade VARCHAR(10),
    phone VARCHAR(15),
    team_id INT NOT NULL,
    role ENUM('队长', '队员') DEFAULT '队员',
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 赛事阶段表 (Tournament)
CREATE TABLE Tournament (
    tournament_id INT AUTO_INCREMENT PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    year YEAR NOT NULL,
    status ENUM('未开始', '进行中', '已结束') DEFAULT '未开始'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 比赛表 (Match)
CREATE TABLE `Match` (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    scheduled_time DATETIME NOT NULL,
    venue VARCHAR(50),
    tournament_id INT NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    referee VARCHAR(20),
    final_score VARCHAR(10),
    FOREIGN KEY (tournament_id) REFERENCES Tournament(tournament_id) ON DELETE CASCADE,
    FOREIGN KEY (home_team_id) REFERENCES Team(team_id) ON DELETE CASCADE,
    FOREIGN KEY (away_team_id) REFERENCES Team(team_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. 盘次对决表 (Game)
CREATE TABLE Game (
    match_id INT,
    game_id TINYINT,
    game_type ENUM('男单', '女单', '男双', '女双', '混双') NOT NULL,
    home_score TINYINT UNSIGNED,
    away_score TINYINT UNSIGNED,
    winner ENUM('主队', '客队'),
    PRIMARY KEY (match_id, game_id),
    FOREIGN KEY (match_id) REFERENCES `Match`(match_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. 参赛球员表 (Player_In_Game)
CREATE TABLE Player_In_Game (
    match_id INT,
    game_id TINYINT,
    student_id VARCHAR(20),
    PRIMARY KEY (match_id, game_id, student_id),
    FOREIGN KEY (match_id, game_id) REFERENCES Game(match_id, game_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Player(student_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
