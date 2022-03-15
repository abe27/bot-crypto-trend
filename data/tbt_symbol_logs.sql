-- trend_db.tbt_symbol_log definition

CREATE TABLE `tbt_signals` (
  `id` char(21) NOT NULL,
  `date` date NOT NULL,
  `symbol` char(20) NOT NULL,
  `price` double NOT NULL,
  `percent` double DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;