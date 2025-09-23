-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- 主機： mysql:3306
-- 產生時間： 2025 年 09 月 23 日 16:02
-- 伺服器版本： 9.4.0
-- PHP 版本： 8.2.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `manager_reviews_db`
--

-- --------------------------------------------------------

--
-- 資料表結構 `extracted_food_items`
--

CREATE TABLE `extracted_food_items` (
  `id` bigint NOT NULL COMMENT '統一自增主鍵',
  `review_id` bigint NOT NULL COMMENT '關聯review_analysis表的id',
  `dish_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '料理名稱（如：臭豆腐、蚵仔煎）',
  `vendor_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '店家攤位名稱（如：326臭臭鍋）',
  `description` text COLLATE utf8mb4_unicode_ci COMMENT '口味食材體驗描述',
  `price` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '價格資訊（如有提及）',
  `rating_sentiment` enum('positive','negative','neutral') COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '評價情感傾向',
  `data_completeness` enum('complete','partial','minimal') COLLATE utf8mb4_unicode_ci DEFAULT 'partial' COMMENT '資料完整度標記（complete=店家+料理+描述完整, partial=部分資訊, minimal=僅描述性內容）',
  `extracted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提取時間'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='結構化食物項目表 - 從評論中提取的具體食物資訊';

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `extracted_food_items`
--
ALTER TABLE `extracted_food_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_extracted_food_review_id` (`review_id`) COMMENT '基於review_id的關聯查詢索引',
  ADD KEY `idx_extracted_food_dish_name` (`dish_name`) COMMENT '基於料理名稱的查詢索引',
  ADD KEY `idx_extracted_food_vendor_name` (`vendor_name`) COMMENT '基於店家名稱的查詢索引',
  ADD KEY `idx_extracted_food_sentiment` (`rating_sentiment`) COMMENT '基於評價情感的篩選索引',
  ADD KEY `idx_extracted_food_completeness` (`data_completeness`) COMMENT '基於資料完整度的篩選索引',
  ADD KEY `idx_extracted_food_completeness_sentiment` (`data_completeness`,`rating_sentiment`) COMMENT '基於完整度和情感傾向的複合索引';

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `extracted_food_items`
--
ALTER TABLE `extracted_food_items`
  MODIFY `id` bigint NOT NULL AUTO_INCREMENT COMMENT '統一自增主鍵';
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
