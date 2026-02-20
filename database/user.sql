-- 用户表
INSERT INTO wb.user (id, username, password, createTime) VALUES (6, 'kerwin zhang', '123', '2025-04-26');
-- 新增用户
INSERT INTO wb.user (id, username, password, createTime, is_admin) VALUES (7, 'Alex', '123456', NOW(), 0);
INSERT INTO wb.user (id, username, password, createTime, is_admin) VALUES (8, 'Sarah', '123456', NOW(), 0);
-- 新增管理员
INSERT INTO wb.user (id, username, password, createTime, is_admin) VALUES (9, 'Admin', '123456', NOW(), 1);