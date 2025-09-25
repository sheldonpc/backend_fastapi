from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `financialnews` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(255) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `is_published` BOOL NOT NULL DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `news_type` VARCHAR(50) NOT NULL DEFAULT 'general',
    `symbol` VARCHAR(50),
    `sentiment_score` DOUBLE,
    `source_url` VARCHAR(500),
    `author_id` INT NOT NULL,
    CONSTRAINT `fk_financia_user_f47840fc` FOREIGN KEY (`author_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4 COMMENT='金融信息';
        CREATE TABLE IF NOT EXISTS `index_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(50) NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `timestamp` DATETIME(6) NOT NULL,
    `price` DECIMAL(15,4) NOT NULL,
    `change` DECIMAL(15,4),
    `change_percent` VARCHAR(20),
    `open_today` DECIMAL(15,4),
    `close_yesterday` DECIMAL(15,4),
    `highest` DECIMAL(15,4),
    `lowest` DECIMAL(15,4),
    `volume` VARCHAR(50),
    `amount` VARCHAR(50),
    `data_type` VARCHAR(30) NOT NULL,
    `market_region` VARCHAR(30) NOT NULL,
    `updated_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='股指和贵金属实时数据';
        CREATE TABLE IF NOT EXISTS `sentimentanalysis` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL,
    `analysis_date` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `sentiment_score` DOUBLE NOT NULL,
    `confidence` DOUBLE NOT NULL,
    `summary` LONGTEXT NOT NULL,
    `news_count` INT NOT NULL DEFAULT 0
) CHARACTER SET utf8mb4 COMMENT='市场情绪分析结果';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `index_data`;
        DROP TABLE IF EXISTS `sentimentanalysis`;
        DROP TABLE IF EXISTS `financialnews`;"""
