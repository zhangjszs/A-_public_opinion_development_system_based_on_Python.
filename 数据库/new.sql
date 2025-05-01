-- --------------------------------------------------------
-- 主机:                           127.0.0.1
-- 服务器版本:                        5.7.40 - MySQL Community Server (GPL)
-- 服务器操作系统:                      Win64
-- HeidiSQL 版本:                  12.3.0.6589
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8mb4 */; -- 默认连接使用 utf8mb4
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- 导出 wb 的数据库结构, 设置默认字符集为 utf8mb4
CREATE DATABASE IF NOT EXISTS `wb` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `wb`;

-- 导出 表 wb.article 结构
-- 删掉旧表（如果存在），确保使用新结构创建
DROP TABLE IF EXISTS `article`;
CREATE TABLE `article` (
                           `id` bigint(20) NOT NULL, -- 假设 ID 是主键且不为空
                           `likeNum` bigint(20) DEFAULT NULL,
                           `commentsLen` bigint(20) DEFAULT NULL,
                           `reposts_count` bigint(20) DEFAULT NULL,
                           `region` text COLLATE utf8mb4_unicode_ci,
                           `content` mediumtext COLLATE utf8mb4_unicode_ci, -- 修改为 MEDIUMTEXT 以支持更长内容
                           `contentLen` bigint(20) DEFAULT NULL,
                           `created_at` date DEFAULT NULL, -- 修改为 DATE 类型
                           `type` text COLLATE utf8mb4_unicode_ci,
                           `detailUrl` text COLLATE utf8mb4_unicode_ci,
                           `authorAvatar` text COLLATE utf8mb4_unicode_ci,
                           `authorName` text COLLATE utf8mb4_unicode_ci,
                           `authorDetail` text COLLATE utf8mb4_unicode_ci,
                           `isVip` tinyint(1) DEFAULT 0, -- 修改为 TINYINT(1) 并设置默认值
                           PRIMARY KEY (`id`), -- 添加主键 (假设 id 是唯一的)
                           INDEX `idx_created_at` (`created_at`) -- 为日期添加索引，便于按时间查询
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 导出 表 wb.comments 结构
-- 删掉旧表（如果存在），确保使用新结构创建
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
                            `comment_id` int(11) NOT NULL AUTO_INCREMENT, -- 添加自增主键
                            `articleId` bigint(20) DEFAULT NULL,
                            `created_at` date DEFAULT NULL, -- 修改为 DATE 类型
                            `like_counts` bigint(20) DEFAULT NULL,
                            `region` text COLLATE utf8mb4_unicode_ci,
                            `content` mediumtext COLLATE utf8mb4_unicode_ci, -- 修改为 MEDIUMTEXT
                            `authorName` text COLLATE utf8mb4_unicode_ci,
                            `authorGender` varchar(1) COLLATE utf8mb4_unicode_ci DEFAULT NULL, -- 修改为 VARCHAR(1)
                            `authorAddress` text COLLATE utf8mb4_unicode_ci,
                            `authorAvatar` text COLLATE utf8mb4_unicode_ci,
                            PRIMARY KEY (`comment_id`), -- 设置主键
                            INDEX `idx_articleId` (`articleId`) -- 为 articleId 添加索引，加速评论查找
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 导出 表 wb.user 结构
-- 删掉旧表（如果存在），确保使用新结构创建
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `username` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
    -- 严重警告: 密码绝不应明文存储！应用程序应存储密码的哈希值。
                        `password` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
                        `createTime` date DEFAULT NULL, -- 修改为 DATE 类型
                        PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; -- 修改表字符集为 utf8mb4

-- 重新插入 user 数据 (注意 createTime 格式现在是 YYYY-MM-DD)
INSERT INTO `user` (`id`, `username`, `password`, `createTime`) VALUES
                                                                    (2, 'Edward', '123123', '2023-03-06'),
                                                                    (3, 'EdwardD', '123123', '2023-08-08'),
                                                                    (4, '19123', '19123', '2024-03-18'),
                                                                    (5, 'qwd', '123', '2024-03-18');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;