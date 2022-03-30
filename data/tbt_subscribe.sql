-- trend_db.tbt_subscribe definition

CREATE TABLE `tbt_investments` (
  `id` char(21) NOT NULL,
  `exchange` char(50) NOT NULL,
  `momentum` char(25) NOT NULL,
  `symbol` char(10) NOT NULL,
  `quotes` char(10) NOT NULL,
  `price` double(10,8) NOT NULL,
  `percent` double(10,2) NOT NULL,
  `last_price` double(10,8) DEFAULT 0.00000000,
  `percent_change` double(10,2) DEFAULT 0.00,
  `is_trend` tinyint(1) DEFAULT 0,
  `avg_score` decimal(10,2) DEFAULT 0.00,
  `is_activate` tinyint(1) DEFAULT 1,
  `created_on` datetime DEFAULT current_timestamp(),
  `last_update` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;