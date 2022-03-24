-- trend_db.tbt_symbol_log definition

CREATE TABLE `tbt_signals` (
  `id` char(21) NOT NULL,
  `exchange` char(50) NOT NULL,
  `date` date NOT NULL,
  `symbol` char(20) NOT NULL,
  `quotes` char(10) NOT NULL,
  `price` double NOT NULL,
  `percent` double DEFAULT 0,
  `last_update` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;