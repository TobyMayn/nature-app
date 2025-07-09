-- MySQL dump 10.13  Distrib 9.3.0, for Linux (x86_64)
--
-- Host: localhost    Database: nature_app
-- ------------------------------------------------------
-- Server version       9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `identified_areas`
--

DROP TABLE IF EXISTS `identified_areas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `identified_areas` (
  `identified_area_id` int NOT NULL AUTO_INCREMENT,
  `location_id` int DEFAULT NULL,
  `geometry` polygon NOT NULL /*!80003 SRID 25832 */,
  `classification_type` varchar(50) NOT NULL,
  `confidence_score` decimal(5,2) DEFAULT NULL,
  `analysis_date` date NOT NULL,
  `duration_untouched_years` int DEFAULT NULL,
  `derived_from_orthophoto_ids` json DEFAULT NULL,
  `derived_from_lai_map_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`identified_area_id`),
  KEY `location_id` (`location_id`),
  KEY `derived_from_lai_map_id` (`derived_from_lai_map_id`),
  CONSTRAINT `identified_areas_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`) ON DELETE CASCADE,
  CONSTRAINT `identified_areas_ibfk_2` FOREIGN KEY (`derived_from_lai_map_id`) REFERENCES `lai_maps` (`lai_map_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `identified_areas`
--

LOCK TABLES `identified_areas` WRITE;
/*!40000 ALTER TABLE `identified_areas` DISABLE KEYS */;
/*!40000 ALTER TABLE `identified_areas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lai_maps`
--

DROP TABLE IF EXISTS `lai_maps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `lai_maps` (
  `lai_map_id` int NOT NULL AUTO_INCREMENT,
  `capture_date` date NOT NULL,
  `geographic_extent` polygon NOT NULL /*!80003 SRID 25832 */,
  `resolution_meters_per_pixel` decimal(8,4) DEFAULT NULL,
  `calculation_algorithm_version` varchar(20) DEFAULT NULL,
  `storage_url` text NOT NULL,
  `derived_from_satellite_photo_id` int DEFAULT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`lai_map_id`),
  KEY `derived_from_satellite_photo_id` (`derived_from_satellite_photo_id`),
  CONSTRAINT `lai_maps_ibfk_1` FOREIGN KEY (`derived_from_satellite_photo_id`) REFERENCES `satellite_photos` (`photo_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lai_maps`
--

LOCK TABLES `lai_maps` WRITE;
/*!40000 ALTER TABLE `lai_maps` DISABLE KEYS */;
/*!40000 ALTER TABLE `lai_maps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `area` polygon NOT NULL /*!80003 SRID 25832 */,
  PRIMARY KEY (`location_id`),
  UNIQUE KEY `location_id` (`location_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locations`
--

LOCK TABLES `locations` WRITE;
/*!40000 ALTER TABLE `locations` DISABLE KEYS */;
/*!40000 ALTER TABLE `locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orthophotos`
--

DROP TABLE IF EXISTS `orthophotos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orthophotos` (
  `photo_id` int NOT NULL,
  `flight_height_meters` decimal(10,2) DEFAULT NULL,
  `sensor_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`photo_id`),
  CONSTRAINT `orthophotos_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`photo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orthophotos`
--

LOCK TABLES `orthophotos` WRITE;
/*!40000 ALTER TABLE `orthophotos` DISABLE KEYS */;
/*!40000 ALTER TABLE `orthophotos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `photos`
--

DROP TABLE IF EXISTS `photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `photos` (
  `photo_id` int NOT NULL AUTO_INCREMENT,
  `capture_date` datetime NOT NULL,
  `geographic_extent` polygon NOT NULL /*!80003 SRID 25832 */,
  `resolution_meters_per_pixel` decimal(8,4) DEFAULT NULL,
  `storage_url` text NOT NULL,
  `photo_type` enum('orthophoto','satellite') NOT NULL,
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`photo_id`),
  UNIQUE KEY `photo_id` (`photo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `photos`
--

LOCK TABLES `photos` WRITE;
/*!40000 ALTER TABLE `photos` DISABLE KEYS */;
/*!40000 ALTER TABLE `photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `results`
--

DROP TABLE IF EXISTS `results`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `results` (
  `result_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `location_id` int DEFAULT NULL,
  `analysis_date` date NOT NULL,
  `analysis_type` enum('untouched_area','lai_time_series') NOT NULL,
  `request_parameters` json DEFAULT NULL,
  `status` enum('PENDING','RUNNING','COMPLETE','FAILED') NOT NULL,
  `requested_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `completed_at` datetime DEFAULT NULL,
  `error_message` text,
  `linked_identified_area_id` int DEFAULT NULL,
  `linked_lai_map_id` int DEFAULT NULL,
  PRIMARY KEY (`result_id`),
  KEY `user_id` (`user_id`),
  KEY `location_id` (`location_id`),
  KEY `linked_identified_area_id` (`linked_identified_area_id`),
  KEY `linked_lai_map_id` (`linked_lai_map_id`),
  CONSTRAINT `results_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`),
  CONSTRAINT `results_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`),
  CONSTRAINT `results_ibfk_3` FOREIGN KEY (`linked_identified_area_id`) REFERENCES `identified_areas` (`identified_area_id`) ON DELETE SET NULL,
  CONSTRAINT `results_ibfk_4` FOREIGN KEY (`linked_lai_map_id`) REFERENCES `lai_maps` (`lai_map_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `results`
--

LOCK TABLES `results` WRITE;
/*!40000 ALTER TABLE `results` DISABLE KEYS */;
/*!40000 ALTER TABLE `results` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `satellite_photos`
--

DROP TABLE IF EXISTS `satellite_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `satellite_photos` (
  `photo_id` int NOT NULL,
  `satellite_name` enum('sentinel-2','landsat-8') NOT NULL,
  `bands_included` json DEFAULT NULL,
  `cloud_cover_percentage` decimal(5,2) DEFAULT NULL,
  PRIMARY KEY (`photo_id`),
  CONSTRAINT `satellite_photos_ibfk_1` FOREIGN KEY (`photo_id`) REFERENCES `photos` (`photo_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `satellite_photos`
--

LOCK TABLES `satellite_photos` WRITE;
/*!40000 ALTER TABLE `satellite_photos` DISABLE KEYS */;
/*!40000 ALTER TABLE `satellite_photos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL,
  `username` varchar(25) NOT NULL,
  `password_hash` varchar(30) NOT NULL,
  `email` varchar(30) DEFAULT NULL,
  `municipality` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-09  9:42:54