from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `article` ADD `category_id` INT NOT NULL;
        CREATE TABLE IF NOT EXISTS `category` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
        CREATE TABLE IF NOT EXISTS `tag` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(50) NOT NULL UNIQUE,
    `created_at` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4;
        ALTER TABLE `article` ADD CONSTRAINT `fk_article_category_48d80539` FOREIGN KEY (`category_id`) REFERENCES `category` (`id`) ON DELETE CASCADE;
        CREATE TABLE `article_tag` (
    `article_id` INT NOT NULL REFERENCES `article` (`id`) ON DELETE CASCADE,
    `tag_id` INT NOT NULL REFERENCES `tag` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `article_tag`;
        ALTER TABLE `article` DROP FOREIGN KEY `fk_article_category_48d80539`;
        ALTER TABLE `article` DROP COLUMN `category_id`;
        DROP TABLE IF EXISTS `category`;
        DROP TABLE IF EXISTS `tag`;"""
