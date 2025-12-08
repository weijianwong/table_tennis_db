-- ============================================
-- 清华大学乒乓球联赛管理系统 - 示例数据
-- ============================================

-- 清空现有数据（可选，仅用于测试）
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Player_In_Game;
TRUNCATE TABLE Game;
TRUNCATE TABLE `Match`;
TRUNCATE TABLE Player;
TRUNCATE TABLE Team;
TRUNCATE TABLE Tournament;
TRUNCATE TABLE College;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 1. 插入院系数据
-- ============================================
INSERT INTO College (dept_id, dept_name, contact_person, phone) VALUES
(1, '计算机系', '张老师', '010-62781234'),
(2, '电子系', '李老师', '010-62782345'),
(3, '自动化系', '王老师', '010-62783456');

-- ============================================
-- 2. 插入球队数据
-- ============================================
INSERT INTO Team (team_id, team_name, established_year, dept_id) VALUES
(1, '计算机系代表队2024', 2024, 1),
(2, '电子系代表队2024', 2024, 2),
(3, '自动化系代表队2024', 2024, 3);

-- ============================================
-- 3. 插入球员数据
-- ============================================
-- 计算机系球员
INSERT INTO Player (student_id, name, gender, grade, phone, team_id, role) VALUES
('2021010101', '张三', '男', '大四', '13800001001', 1, '队长'),
('2021010102', '李四', '男', '大四', '13800001002', 1, '队员'),
('2022010103', '王五', '女', '大三', '13800001003', 1, '队员'),
('2022010104', '赵六', '男', '大三', '13800001004', 1, '队员'),
('2023010105', '孙七', '女', '大二', '13800001005', 1, '队员');

-- 电子系球员
INSERT INTO Player (student_id, name, gender, grade, phone, team_id, role) VALUES
('2021020201', '周八', '男', '大四', '13800002001', 2, '队长'),
('2021020202', '吴九', '男', '大四', '13800002002', 2, '队员'),
('2022020203', '郑十', '女', '大三', '13800002003', 2, '队员'),
('2022020204', '钱一', '男', '大三', '13800002004', 2, '队员'),
('2023020205', '刘二', '女', '大二', '13800002005', 2, '队员');

-- 自动化系球员
INSERT INTO Player (student_id, name, gender, grade, phone, team_id, role) VALUES
('2021030301', '陈三', '男', '大四', '13800003001', 3, '队长'),
('2021030302', '林四', '男', '大四', '13800003002', 3, '队员'),
('2022030303', '黄五', '女', '大三', '13800003003', 3, '队员'),
('2022030304', '徐六', '男', '大三', '13800003004', 3, '队员'),
('2023030305', '杨七', '女', '大二', '13800003005', 3, '队员');

-- ============================================
-- 4. 插入赛事数据
-- ============================================
INSERT INTO Tournament (tournament_id, tournament_name, year, status) VALUES
(1, '第26届清华大学乒乓球联赛', 2024, '进行中');

-- ============================================
-- 5. 插入比赛数据
-- ============================================
-- 比赛1: 计算机系 vs 电子系
INSERT INTO `Match` (match_id, scheduled_time, venue, tournament_id, home_team_id, away_team_id, referee, final_score) VALUES
(1, '2024-11-01 14:00:00', '综合体育馆1号台', 1, 1, 2, '裁判-王裁判', '3:2');

-- 比赛2: 电子系 vs 自动化系
INSERT INTO `Match` (match_id, scheduled_time, venue, tournament_id, home_team_id, away_team_id, referee, final_score) VALUES
(2, '2024-11-08 14:00:00', '综合体育馆2号台', 1, 2, 3, '裁判-李裁判', '3:1');

-- 比赛3: 计算机系 vs 自动化系
INSERT INTO `Match` (match_id, scheduled_time, venue, tournament_id, home_team_id, away_team_id, referee, final_score) VALUES
(3, '2024-11-15 14:00:00', '综合体育馆1号台', 1, 1, 3, '裁判-张裁判', '3:0');

-- ============================================
-- 6. 插入盘次对决数据（五盘三胜制）
-- ============================================

-- ==================== 比赛1: 计算机系 vs 电子系 (3:2) ====================

-- 比赛1 - 第1盘: 男单 (计算机系 张三 vs 电子系 周八) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(1, 1, '男单', 11, 8, '主队');

-- 比赛1 - 第2盘: 女单 (计算机系 王五 vs 电子系 郑十) - 电子系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(1, 2, '女单', 9, 11, '客队');

-- 比赛1 - 第3盘: 男双 (计算机系 李四+赵六 vs 电子系 吴九+钱一) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(1, 3, '男双', 11, 7, '主队');

-- 比赛1 - 第4盘: 女双 (计算机系 王五+孙七 vs 电子系 郑十+刘二) - 电子系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(1, 4, '女双', 8, 11, '客队');

-- 比赛1 - 第5盘: 混双 (计算机系 张三+王五 vs 电子系 周八+郑十) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(1, 5, '混双', 11, 9, '主队');

-- ==================== 比赛2: 电子系 vs 自动化系 (3:1) ====================

-- 比赛2 - 第1盘: 男单 (电子系 周八 vs 自动化系 陈三) - 电子系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(2, 1, '男单', 11, 6, '主队');

-- 比赛2 - 第2盘: 女单 (电子系 郑十 vs 自动化系 黄五) - 自动化系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(2, 2, '女单', 9, 11, '客队');

-- 比赛2 - 第3盘: 男双 (电子系 吴九+钱一 vs 自动化系 林四+徐六) - 电子系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(2, 3, '男双', 11, 5, '主队');

-- 比赛2 - 第4盘: 混双 (电子系 周八+郑十 vs 自动化系 陈三+黄五) - 电子系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(2, 4, '混双', 11, 8, '主队');

-- 比赛2 - 第5盘: 男单 (电子系 钱一 vs 自动化系 徐六) - 未进行
-- 注意：3:1已分出胜负，第5盘可能不需要进行

-- ==================== 比赛3: 计算机系 vs 自动化系 (3:0) ====================

-- 比赛3 - 第1盘: 男单 (计算机系 张三 vs 自动化系 陈三) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(3, 1, '男单', 11, 7, '主队');

-- 比赛3 - 第2盘: 女单 (计算机系 王五 vs 自动化系 黄五) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(3, 2, '女单', 11, 6, '主队');

-- 比赛3 - 第3盘: 男双 (计算机系 李四+赵六 vs 自动化系 林四+徐六) - 计算机系胜
INSERT INTO Game (match_id, game_id, game_type, home_score, away_score, winner) VALUES
(3, 3, '男双', 11, 9, '主队');

-- 比赛3 - 第4盘和第5盘未进行（已3:0分出胜负）

-- ============================================
-- 7. 插入参赛球员数据
-- ============================================

-- ==================== 比赛1的参赛球员 ====================

-- 比赛1 - 第1盘 (男单): 张三 vs 周八
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(1, 1, '2021010101'),  -- 张三 (计算机系)
(1, 1, '2021020201');  -- 周八 (电子系)

-- 比赛1 - 第2盘 (女单): 王五 vs 郑十
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(1, 2, '2022010103'),  -- 王五 (计算机系)
(1, 2, '2022020203');  -- 郑十 (电子系)

-- 比赛1 - 第3盘 (男双): 李四+赵六 vs 吴九+钱一
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(1, 3, '2021010102'),  -- 李四 (计算机系)
(1, 3, '2022010104'),  -- 赵六 (计算机系)
(1, 3, '2021020202'),  -- 吴九 (电子系)
(1, 3, '2022020204');  -- 钱一 (电子系)

-- 比赛1 - 第4盘 (女双): 王五+孙七 vs 郑十+刘二
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(1, 4, '2022010103'),  -- 王五 (计算机系)
(1, 4, '2023010105'),  -- 孙七 (计算机系)
(1, 4, '2022020203'),  -- 郑十 (电子系)
(1, 4, '2023020205');  -- 刘二 (电子系)

-- 比赛1 - 第5盘 (混双): 张三+王五 vs 周八+郑十
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(1, 5, '2021010101'),  -- 张三 (计算机系)
(1, 5, '2022010103'),  -- 王五 (计算机系)
(1, 5, '2021020201'),  -- 周八 (电子系)
(1, 5, '2022020203');  -- 郑十 (电子系)

-- ==================== 比赛2的参赛球员 ====================

-- 比赛2 - 第1盘 (男单): 周八 vs 陈三
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(2, 1, '2021020201'),  -- 周八 (电子系)
(2, 1, '2021030301');  -- 陈三 (自动化系)

-- 比赛2 - 第2盘 (女单): 郑十 vs 黄五
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(2, 2, '2022020203'),  -- 郑十 (电子系)
(2, 2, '2022030303');  -- 黄五 (自动化系)

-- 比赛2 - 第3盘 (男双): 吴九+钱一 vs 林四+徐六
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(2, 3, '2021020202'),  -- 吴九 (电子系)
(2, 3, '2022020204'),  -- 钱一 (电子系)
(2, 3, '2021030302'),  -- 林四 (自动化系)
(2, 3, '2022030304');  -- 徐六 (自动化系)

-- 比赛2 - 第4盘 (混双): 周八+郑十 vs 陈三+黄五
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(2, 4, '2021020201'),  -- 周八 (电子系)
(2, 4, '2022020203'),  -- 郑十 (电子系)
(2, 4, '2021030301'),  -- 陈三 (自动化系)
(2, 4, '2022030303');  -- 黄五 (自动化系)

-- ==================== 比赛3的参赛球员 ====================

-- 比赛3 - 第1盘 (男单): 张三 vs 陈三
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(3, 1, '2021010101'),  -- 张三 (计算机系)
(3, 1, '2021030301');  -- 陈三 (自动化系)

-- 比赛3 - 第2盘 (女单): 王五 vs 黄五
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(3, 2, '2022010103'),  -- 王五 (计算机系)
(3, 2, '2022030303');  -- 黄五 (自动化系)

-- 比赛3 - 第3盘 (男双): 李四+赵六 vs 林四+徐六
INSERT INTO Player_In_Game (match_id, game_id, student_id) VALUES
(3, 3, '2021010102'),  -- 李四 (计算机系)
(3, 3, '2022010104'),  -- 赵六 (计算机系)
(3, 3, '2021030302'),  -- 林四 (自动化系)
(3, 3, '2022030304');  -- 徐六 (自动化系)

-- ============================================
-- 数据插入完成
-- ============================================

-- 验证数据
SELECT '院系数据:' AS '';
SELECT * FROM College;

SELECT '球队数据:' AS '';
SELECT * FROM Team;

SELECT '球员数据:' AS '';
SELECT * FROM Player ORDER BY team_id, role DESC, student_id;

SELECT '赛事数据:' AS '';
SELECT * FROM Tournament;

SELECT '比赛数据:' AS '';
SELECT * FROM `Match`;

SELECT '盘次对决数据:' AS '';
SELECT * FROM Game ORDER BY match_id, game_id;

SELECT '参赛球员数据:' AS '';
SELECT * FROM Player_In_Game ORDER BY match_id, game_id, student_id;

-- 统计信息
SELECT '=== 数据统计 ===' AS '';
SELECT '总院系数' AS 类型, COUNT(*) AS 数量 FROM College
UNION ALL
SELECT '总球队数', COUNT(*) FROM Team
UNION ALL
SELECT '总球员数', COUNT(*) FROM Player
UNION ALL
SELECT '总赛事数', COUNT(*) FROM Tournament
UNION ALL
SELECT '总比赛数', COUNT(*) FROM `Match`
UNION ALL
SELECT '总盘次数', COUNT(*) FROM Game
UNION ALL
SELECT '总参赛记录数', COUNT(*) FROM Player_In_Game;