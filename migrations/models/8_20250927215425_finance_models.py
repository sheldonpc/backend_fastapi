from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `bond_yield_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `cn_2y` DECIMAL(8,4) NOT NULL COMMENT '中国国债收益率2年',
    `cn_5y` DECIMAL(8,4) NOT NULL COMMENT '中国国债收益率5年',
    `cn_10y` DECIMAL(8,4) NOT NULL COMMENT '中国国债收益率10年',
    `cn_30y` DECIMAL(8,4) NOT NULL COMMENT '中国国债收益率30年',
    `cn_spread_10y_2y` DECIMAL(8,4) NOT NULL COMMENT '中国国债收益率10年-2年',
    `cn_gdp_growth` DECIMAL(8,4) COMMENT '中国GDP年增率',
    `us_2y` DECIMAL(8,4) NOT NULL COMMENT '美国国债收益率2年',
    `us_5y` DECIMAL(8,4) NOT NULL COMMENT '美国国债收益率5年',
    `us_10y` DECIMAL(8,4) NOT NULL COMMENT '美国国债收益率10年',
    `us_30y` DECIMAL(8,4) NOT NULL COMMENT '美国国债收益率30年',
    `us_spread_10y_2y` DECIMAL(8,4) NOT NULL COMMENT '美国国债收益率10年-2年',
    `us_gdp_growth` DECIMAL(8,4) COMMENT '美国GDP年增率'
) CHARACTER SET utf8mb4 COMMENT='债券收益率历史数据模型';
        CREATE TABLE IF NOT EXISTS `cn_index_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `price` DECIMAL(15,4) NOT NULL,
    `change` DECIMAL(15,4) NOT NULL,
    `change_percent` DECIMAL(15,4) NOT NULL,
    `open_today` DECIMAL(15,4) NOT NULL,
    `highest` DECIMAL(15,4) NOT NULL,
    `lowest` DECIMAL(15,4) NOT NULL,
    `close_yesterday` DECIMAL(15,4) NOT NULL,
    `amplitude` DECIMAL(15,4) NOT NULL,
    `timestamp` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='中国指数实时数据';
        CREATE TABLE IF NOT EXISTS `cn_stock_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `latest_price` DECIMAL(10,2) NOT NULL COMMENT '最新价',
    `high_price` DECIMAL(10,2) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(10,2) NOT NULL COMMENT '最低价',
    `open_price` DECIMAL(10,2) NOT NULL COMMENT '今开价',
    `code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `name` VARCHAR(50) NOT NULL COMMENT '股票简称',
    `prev_close` DECIMAL(10,2) NOT NULL COMMENT '昨收价',
    `net_profit` DECIMAL(20,2) NOT NULL COMMENT '净利润',
    `market_cap` DECIMAL(20,2) NOT NULL COMMENT '总市值',
    `float_market_cap` DECIMAL(20,2) NOT NULL COMMENT '流通市值',
    `industry` VARCHAR(50) NOT NULL COMMENT '所属行业',
    `region` VARCHAR(50) NOT NULL COMMENT '地域板块',
    `pe_ttm` DECIMAL(10,2) NOT NULL COMMENT '市盈率（动态，TTM）',
    `pe_static` DECIMAL(10,2) NOT NULL COMMENT '市盈率（静态）',
    `pe_rolling` DECIMAL(10,2) NOT NULL COMMENT '市盈率（滚动）',
    `listing_date` VARCHAR(8) NOT NULL COMMENT '上市日期',
    UNIQUE KEY `uid_cn_stock_da_code_b654bb` (`code`)
) CHARACTER SET utf8mb4 COMMENT='中国股票数据模型 (精确匹配15个字段)';
        CREATE TABLE IF NOT EXISTS `east_money_history_news` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL COMMENT '新闻标题',
    `summary` LONGTEXT NOT NULL COMMENT '新闻摘要',
    `publish_time` DATETIME(6) NOT NULL COMMENT '发布时间',
    `source` VARCHAR(500) COMMENT '新闻来源'
) CHARACTER SET utf8mb4 COMMENT='东方财富历史新闻数据模型';
        CREATE TABLE IF NOT EXISTS `gold_real_time_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL COMMENT '黄金品种代码',
    `name` VARCHAR(50) NOT NULL COMMENT '黄金品种名称',
    `exchange` VARCHAR(30) NOT NULL COMMENT '交易所/市场',
    `current_price` DECIMAL(12,3) NOT NULL COMMENT '当前价格',
    `prev_close` DECIMAL(12,3) COMMENT '昨收价',
    `open_price` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high_price` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `bid_price` DECIMAL(12,3) COMMENT '买价',
    `ask_price` DECIMAL(12,3) COMMENT '卖价',
    `volume` BIGINT COMMENT '成交量',
    `change_amount` DECIMAL(10,3) COMMENT '涨跌额',
    `change_percent` DECIMAL(10,3) COMMENT '涨跌幅(%)',
    `unit` VARCHAR(20) NOT NULL COMMENT '价格单位',
    `update_time` VARCHAR(10) NOT NULL COMMENT '更新时间',
    `data_date` DATE NOT NULL COMMENT '数据日期',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_gold_real_t_symbol_f54363` (`symbol`, `data_date`),
    KEY `idx_gold_real_t_symbol_f54363` (`symbol`, `data_date`)
) CHARACTER SET utf8mb4 COMMENT='黄金实时数据模型';
        CREATE TABLE IF NOT EXISTS `sz399006_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `open` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `close` DECIMAL(12,3) NOT NULL COMMENT '收盘价',
    `volume` BIGINT NOT NULL COMMENT '成交量'
) CHARACTER SET utf8mb4 COMMENT='恒生历史数据模型';
        CREATE TABLE IF NOT EXISTS `historyforeigncurrencydata` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `date` DATE NOT NULL,
    `price` DECIMAL(15,4) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='外汇历史数据';
        CREATE TABLE IF NOT EXISTS `hotstock` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `followers` INT NOT NULL,
    `price` DECIMAL(15,4) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='热门股票';
        CREATE TABLE IF NOT EXISTS `market_index_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `index_code` VARCHAR(10) NOT NULL COMMENT '指数代码',
    `index_name` VARCHAR(50) NOT NULL COMMENT '指数名称',
    `last_price` DECIMAL(12,3) NOT NULL COMMENT '最新价',
    `change` DECIMAL(10,4) NOT NULL COMMENT '涨跌幅',
    `change_amount` DECIMAL(10,3) NOT NULL COMMENT '涨跌额',
    `up_num` INT NOT NULL COMMENT '上涨家数',
    `down_num` INT NOT NULL COMMENT '下跌家数',
    `flat_num` INT NOT NULL COMMENT '平盘家数',
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_market_inde_index_c_c2b48a` (`index_code`, `update_time`)
) CHARACTER SET utf8mb4 COMMENT='主要指数涨跌数据模型';
        CREATE TABLE IF NOT EXISTS `market_up_down_stats` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `up_num` INT NOT NULL COMMENT '上涨家数',
    `down_num` INT NOT NULL COMMENT '下跌家数',
    `flat_num` INT NOT NULL COMMENT '平盘家数',
    `rise_num` INT NOT NULL COMMENT '上涨家数(全市场)',
    `fall_num` INT NOT NULL COMMENT '下跌家数(全市场)',
    `average_rise` DECIMAL(10,4) NOT NULL COMMENT '平均涨跌幅',
    `up_2` INT NOT NULL COMMENT '涨幅2%以上',
    `up_4` INT NOT NULL COMMENT '涨幅4%以上',
    `up_6` INT NOT NULL COMMENT '涨幅6%以上',
    `up_8` INT NOT NULL COMMENT '涨幅8%以上',
    `up_10` INT NOT NULL COMMENT '涨幅10%以上',
    `down_2` INT NOT NULL COMMENT '跌幅2%以上',
    `down_4` INT NOT NULL COMMENT '跌幅4%以上',
    `down_6` INT NOT NULL COMMENT '跌幅6%以上',
    `down_8` INT NOT NULL COMMENT '跌幅8%以上',
    `down_10` INT NOT NULL COMMENT '跌幅10%以上',
    `suspend_num` INT NOT NULL COMMENT '停牌家数',
    `status` BOOL NOT NULL COMMENT '数据状态',
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='全市场涨跌统计';
        CREATE TABLE IF NOT EXISTS `minutelevelcnstockdata` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(50) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='中国股票分钟级数据';
        CREATE TABLE IF NOT EXISTS `new_stock_listing` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `stock_code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `stock_name` VARCHAR(50) NOT NULL COMMENT '股票名称',
    `ipo_price` DECIMAL(10,2) NOT NULL COMMENT '发行价',
    `ipo_pe` DECIMAL(10,2) NOT NULL COMMENT '发行市盈率',
    `allot_max` INT NOT NULL COMMENT '申购上限(股)',
    `lot_rate` DECIMAL(10,4) NOT NULL COMMENT '中签率',
    `issue_vol` BIGINT NOT NULL COMMENT '发行总量',
    `listing_date` DATE NOT NULL COMMENT '上市日期',
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='新股上市数据';
        CREATE TABLE IF NOT EXISTS `news` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL COMMENT '新闻标题',
    `content` LONGTEXT NOT NULL COMMENT '新闻内容',
    `publish_time` DATETIME(6) NOT NULL COMMENT '发布时间',
    `source` VARCHAR(500) COMMENT '新闻来源',
    KEY `idx_news_title_e5067a` (`title`, `publish_time`)
) CHARACTER SET utf8mb4 COMMENT='新闻数据模型';
        CREATE TABLE IF NOT EXISTS `news3` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `title` VARCHAR(200) NOT NULL COMMENT '新闻标题',
    `content` LONGTEXT NOT NULL COMMENT '新闻内容',
    `publish_time` DATETIME(6) NOT NULL COMMENT '发布时间',
    `source` VARCHAR(500) COMMENT '新闻来源'
) CHARACTER SET utf8mb4 COMMENT='新闻数据模型';
        CREATE TABLE IF NOT EXISTS `news4` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `publish_time` DATETIME(6) NOT NULL COMMENT '发布时间',
    `content` LONGTEXT NOT NULL COMMENT '新闻内容'
) CHARACTER SET utf8mb4 COMMENT='新闻数据模型';
        CREATE TABLE IF NOT EXISTS `oil_real_time_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL COMMENT '原油品种代码',
    `name` VARCHAR(50) NOT NULL COMMENT '原油品种名称',
    `unit` VARCHAR(20) NOT NULL COMMENT '价格单位' DEFAULT '美元/桶',
    `current_price` DECIMAL(10,3) NOT NULL COMMENT '当前价格',
    `change_amount` DECIMAL(10,3) NOT NULL COMMENT '涨跌额',
    `change_percent` DECIMAL(10,3) NOT NULL COMMENT '涨跌幅(%)',
    `prev_close` DECIMAL(10,3) NOT NULL COMMENT '昨收价',
    `open_price` DECIMAL(10,3) NOT NULL COMMENT '今开价',
    `high_price` DECIMAL(10,3) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(10,3) NOT NULL COMMENT '最低价',
    `update_time` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_oil_real_ti_symbol_d7309e` (`symbol`, `update_time`),
    KEY `idx_oil_real_ti_symbol_ea101e` (`symbol`)
) CHARACTER SET utf8mb4 COMMENT='原油实时数据模型（根据网页显示格式）';
        CREATE TABLE IF NOT EXISTS `realtimeforeigncurrencydata` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `buying_price` DECIMAL(15,4) NOT NULL,
    `selling_price` DECIMAL(15,4) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='外汇实时数据';
        CREATE TABLE IF NOT EXISTS `rich_list` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `rank` INT NOT NULL COMMENT '排名',
    `wealth` DECIMAL(12,2) NOT NULL COMMENT '财富(亿元)',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `company` VARCHAR(100) NOT NULL COMMENT '企业',
    `industry` VARCHAR(100) NOT NULL COMMENT '行业',
    `year` INT NOT NULL COMMENT '榜单年份',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_rich_list_year_c77417` (`year`, `rank`)
) CHARACTER SET utf8mb4 COMMENT='富豪排行榜数据模型';
        CREATE TABLE IF NOT EXISTS `sh000001_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `open` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `close` DECIMAL(12,3) NOT NULL COMMENT '收盘价',
    `volume` BIGINT NOT NULL COMMENT '成交量'
) CHARACTER SET utf8mb4 COMMENT='上证指数历史数据模型';
        CREATE TABLE IF NOT EXISTS `spx_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `name` VARCHAR(50) NOT NULL COMMENT '股票名称',
    `open` DECIMAL(12,3) NOT NULL COMMENT '今开',
    `close` DECIMAL(12,3) NOT NULL COMMENT '最新价',
    `high` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `amplitude` DECIMAL(10,3) NOT NULL COMMENT '振幅'
) CHARACTER SET utf8mb4 COMMENT='标普500历史数据模型';
        CREATE TABLE IF NOT EXISTS `sz399001_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `open` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `close` DECIMAL(12,3) NOT NULL COMMENT '收盘价',
    `volume` BIGINT NOT NULL COMMENT '成交量'
) CHARACTER SET utf8mb4 COMMENT='深证成指历史数据模型';
        CREATE TABLE IF NOT EXISTS `sz399006_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE COMMENT '交易日期',
    `open` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `close` DECIMAL(12,3) NOT NULL COMMENT '收盘价',
    `volume` BIGINT NOT NULL COMMENT '成交量'
) CHARACTER SET utf8mb4 COMMENT='创业板指历史数据模型';
        CREATE TABLE IF NOT EXISTS `silver_real_time_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL COMMENT '白银品种代码',
    `name` VARCHAR(50) NOT NULL COMMENT '白银品种名称',
    `exchange` VARCHAR(30) NOT NULL COMMENT '交易所/市场',
    `current_price` DECIMAL(12,3) NOT NULL COMMENT '当前价格',
    `prev_close` DECIMAL(12,3) COMMENT '昨收价',
    `open_price` DECIMAL(12,3) NOT NULL COMMENT '开盘价',
    `high_price` DECIMAL(12,3) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(12,3) NOT NULL COMMENT '最低价',
    `bid_price` DECIMAL(12,3) COMMENT '买价',
    `ask_price` DECIMAL(12,3) COMMENT '卖价',
    `volume` BIGINT COMMENT '成交量',
    `change_amount` DECIMAL(10,3) COMMENT '涨跌额',
    `change_percent` DECIMAL(10,3) COMMENT '涨跌幅(%)',
    `unit` VARCHAR(20) NOT NULL COMMENT '价格单位',
    `update_time` VARCHAR(10) NOT NULL COMMENT '更新时间',
    `data_date` DATE NOT NULL COMMENT '数据日期',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_silver_real_symbol_3e8702` (`symbol`, `data_date`),
    KEY `idx_silver_real_symbol_3e8702` (`symbol`, `data_date`)
) CHARACTER SET utf8mb4 COMMENT='白银实时数据模型';
        CREATE TABLE IF NOT EXISTS `specific_stock_history` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL COMMENT '日期',
    `code` VARCHAR(10) NOT NULL COMMENT '股票代码',
    `open_price` DECIMAL(10,2) NOT NULL COMMENT '开盘价',
    `close_price` DECIMAL(10,2) NOT NULL COMMENT '收盘价',
    `high_price` DECIMAL(10,2) NOT NULL COMMENT '最高价',
    `low_price` DECIMAL(10,2) NOT NULL COMMENT '最低价',
    `volume` BIGINT NOT NULL COMMENT '成交量(手)',
    `amount` DECIMAL(20,2) NOT NULL COMMENT '成交额(元)',
    `amplitude` DECIMAL(10,2) NOT NULL COMMENT '振幅(%)',
    `change_percent` DECIMAL(10,2) NOT NULL COMMENT '涨跌幅(%)',
    `change_amount` DECIMAL(10,2) NOT NULL COMMENT '涨跌额',
    `turnover_rate` DECIMAL(10,2) NOT NULL COMMENT '换手率(%)',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY `uid_specific_st_date_79b6cb` (`date`, `code`),
    KEY `idx_specific_st_code_03899a` (`code`, `date`)
) CHARACTER SET utf8mb4 COMMENT='个股历史行情数据表';
        CREATE TABLE IF NOT EXISTS `usa_index_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `code` VARCHAR(20) NOT NULL,
    `name` VARCHAR(50) NOT NULL,
    `price` DECIMAL(15,4) NOT NULL,
    `change` DECIMAL(15,4) NOT NULL,
    `change_percent` DECIMAL(15,4) NOT NULL,
    `open_today` DECIMAL(15,4) NOT NULL,
    `highest` DECIMAL(15,4) NOT NULL,
    `lowest` DECIMAL(15,4) NOT NULL,
    `close_yesterday` DECIMAL(15,4) NOT NULL,
    `amplitude` DECIMAL(15,4) NOT NULL,
    `timestamp` DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4 COMMENT='美国指数实时数据';
        CREATE TABLE IF NOT EXISTS `vix_real_time_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `symbol` VARCHAR(20) NOT NULL COMMENT '指数代码' DEFAULT 'znb_VIX',
    `name` VARCHAR(50) NOT NULL COMMENT '指数名称' DEFAULT 'VIX恐慌指数',
    `current_price` DECIMAL(8,4) NOT NULL COMMENT '当前价格',
    `change_amount` DECIMAL(8,4) NOT NULL COMMENT '涨跌额',
    `change_percent` DECIMAL(8,2) NOT NULL COMMENT '涨跌幅(%)',
    `open_price` DECIMAL(8,4) NOT NULL COMMENT '今开价',
    `high_price` DECIMAL(8,4) NOT NULL COMMENT '最高价',
    `prev_close` DECIMAL(8,4) NOT NULL COMMENT '昨收价',
    `low_price` DECIMAL(8,4) NOT NULL COMMENT '最低价',
    `update_time` VARCHAR(10) NOT NULL COMMENT '更新时间',
    `data_date` VARCHAR(10) NOT NULL COMMENT '数据日期',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4 COMMENT='VIX恐慌指数实时数据模型';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `gold_real_time_data`;
        DROP TABLE IF EXISTS `usa_index_data`;
        DROP TABLE IF EXISTS `sh000001_history`;
        DROP TABLE IF EXISTS `minutelevelcnstockdata`;
        DROP TABLE IF EXISTS `bond_yield_history`;
        DROP TABLE IF EXISTS `hotstock`;
        DROP TABLE IF EXISTS `new_stock_listing`;
        DROP TABLE IF EXISTS `cn_index_data`;
        DROP TABLE IF EXISTS `market_up_down_stats`;
        DROP TABLE IF EXISTS `spx_history`;
        DROP TABLE IF EXISTS `oil_real_time_data`;
        DROP TABLE IF EXISTS `news3`;
        DROP TABLE IF EXISTS `silver_real_time_data`;
        DROP TABLE IF EXISTS `news`;
        DROP TABLE IF EXISTS `vix_real_time_data`;
        DROP TABLE IF EXISTS `sz399006_history`;
        DROP TABLE IF EXISTS `realtimeforeigncurrencydata`;
        DROP TABLE IF EXISTS `sz399006_history`;
        DROP TABLE IF EXISTS `market_index_data`;
        DROP TABLE IF EXISTS `news4`;
        DROP TABLE IF EXISTS `rich_list`;
        DROP TABLE IF EXISTS `sz399001_history`;
        DROP TABLE IF EXISTS `cn_stock_data`;
        DROP TABLE IF EXISTS `historyforeigncurrencydata`;
        DROP TABLE IF EXISTS `east_money_history_news`;
        DROP TABLE IF EXISTS `specific_stock_history`;"""
