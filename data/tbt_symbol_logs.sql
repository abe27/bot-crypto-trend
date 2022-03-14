-- trend_db.tbt_symbol_log definition

CREATE TABLE `tbt_symbol_log` (
  `id` char(36) NOT NULL,
  `date` datetime NOT NULL,
  `symbol` char(20) NOT NULL,
  `price` double NOT NULL,
  `percent` double DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;