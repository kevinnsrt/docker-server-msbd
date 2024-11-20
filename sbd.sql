/*
SQLyog Ultimate v13.1.1 (64 bit)
MySQL - 10.4.32-MariaDB : Database - spotify
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`spotify` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;

USE `spotify`;

/*Table structure for table `artists` */

DROP TABLE IF EXISTS `artists`;

CREATE TABLE `artists` (
  `id` varchar(50) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `monthlyListeners` int(11) DEFAULT NULL,
  `worldRank` int(11) DEFAULT NULL,
  `biography` text DEFAULT NULL,
  `last_updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `artists` */

/*Table structure for table `artists_history` */

DROP TABLE IF EXISTS `artists_history`;

CREATE TABLE `artists_history` (
  `id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT NULL,
  `followers` int(11) DEFAULT NULL,
  `monthlyListeners` int(11) DEFAULT NULL,
  `worldRank` int(11) DEFAULT NULL,
  `biography` text DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `artists_history` */

/*Table structure for table `topcities` */

DROP TABLE IF EXISTS `topcities`;

CREATE TABLE `topcities` (
  `artist_id` varchar(50) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` char(2) DEFAULT NULL,
  `numberOfListeners` int(11) DEFAULT NULL,
  `last_updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `topcities_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `topcities` */

/*Table structure for table `topcities_history` */

DROP TABLE IF EXISTS `topcities_history`;

CREATE TABLE `topcities_history` (
  `artist_id` varchar(50) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `country` char(2) DEFAULT NULL,
  `numberOfListeners` int(11) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `topcities_history` */

/*Table structure for table `toptracks` */

DROP TABLE IF EXISTS `toptracks`;

CREATE TABLE `toptracks` (
  `id` varchar(50) NOT NULL,
  `artist_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `streamCount` int(11) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `contentRating` varchar(10) DEFAULT NULL,
  `last_updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `artist_id` (`artist_id`),
  CONSTRAINT `toptracks_ibfk_1` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `toptracks` */

/*Table structure for table `toptracks_history` */

DROP TABLE IF EXISTS `toptracks_history`;

CREATE TABLE `toptracks_history` (
  `id` varchar(50) DEFAULT NULL,
  `artist_id` varchar(50) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `streamCount` int(11) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `contentRating` varchar(10) DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

/*Data for the table `toptracks_history` */

/* Trigger structure for table `artists` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `before_update_artists` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `before_update_artists` BEFORE UPDATE ON `artists` FOR EACH ROW BEGIN
  INSERT INTO artists_history (id, name, verified, followers, monthlyListeners, worldRank, biography, timestamp)
  VALUES (OLD.id, OLD.name, OLD.verified, OLD.followers, OLD.monthlyListeners, OLD.worldRank, OLD.biography, NOW());
END */$$


DELIMITER ;

/* Trigger structure for table `topcities` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `before_update_topcities` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `before_update_topcities` BEFORE UPDATE ON `topcities` FOR EACH ROW 
BEGIN
    INSERT INTO topcities_history (artist_id, city, country, numberOfListeners, timestamp)
    VALUES (OLD.artist_id, OLD.city, OLD.country, OLD.numberOfListeners, NOW());
END */$$


DELIMITER ;

/* Trigger structure for table `toptracks` */

DELIMITER $$

/*!50003 DROP TRIGGER*//*!50032 IF EXISTS */ /*!50003 `before_update_toptracks` */$$

/*!50003 CREATE */ /*!50017 DEFINER = 'root'@'localhost' */ /*!50003 TRIGGER `before_update_toptracks` BEFORE UPDATE ON `toptracks` FOR EACH ROW 
BEGIN
    INSERT INTO toptracks_history (id, artist_id, name, streamCount, duration, contentRating, timestamp)
    VALUES (OLD.id, OLD.artist_id, OLD.name, OLD.streamCount, OLD.duration, OLD.contentRating, NOW());
END */$$


DELIMITER ;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
