-- trend_db.tbt_subscribe definition

CREATE TABLE `tbt_subscribe` (
  `id` char(36) NOT NULL DEFAULT uuid(),
  `etd` date NOT NULL,
  `symbol` char(10) NOT NULL,
  `on_price` double NOT NULL,
  `on_percent` double NOT NULL,
  `last_price` double DEFAULT 0,
  `percent_change` double DEFAULT 0,
  `is_trend` tinyint(1) DEFAULT 0,
  `avg_score` decimal(10,0) DEFAULT 0,
  `is_activate` tinyint(1) DEFAULT 1,
  `created_on` datetime DEFAULT current_timestamp(),
  `last_update` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `tbt_subscribe_un` (`symbol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;