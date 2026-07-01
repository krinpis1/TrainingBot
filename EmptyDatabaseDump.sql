-- MySQL dump 10.13  Distrib 8.0.19, for Win64 (x86_64)
--
-- Host: localhost    Database: rowing_club_test
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `days_of_week`
--

DROP TABLE IF EXISTS `days_of_week`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `days_of_week` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `days_of_week`
--

LOCK TABLES `days_of_week` WRITE;
/*!40000 ALTER TABLE `days_of_week` DISABLE KEYS */;
INSERT INTO `days_of_week` VALUES (1,'Понедельник'),(2,'Вторник'),(3,'Среда'),(4,'Четверг'),(5,'Пятница'),(6,'Суббота'),(7,'Воскресенье');
/*!40000 ALTER TABLE `days_of_week` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `event_types`
--

DROP TABLE IF EXISTS `event_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `event_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `event_types`
--

LOCK TABLES `event_types` WRITE;
/*!40000 ALTER TABLE `event_types` DISABLE KEYS */;
INSERT INTO `event_types` VALUES (1,'запись создана'),(2,'запись отменена участником'),(3,'запись отменена из-за отмены тренировки'),(4,'запись прошла'),(5,'тренировка назначена'),(6,'тренировка отменена'),(7,'тренировка прошла'),(8,'пользователь добавлен'),(9,'слот добавлен'),(10,'слот изменён'),(11,'группа добавлена');
/*!40000 ALTER TABLE `event_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_type_id` int NOT NULL,
  `user_id` int DEFAULT NULL,
  `training_id` int DEFAULT NULL,
  `registration_id` int DEFAULT NULL,
  `slot_id` int DEFAULT NULL,
  `happened_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `group_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `events_event_types_FK` (`event_type_id`),
  KEY `events_users_FK` (`user_id`),
  KEY `events_trainings_FK` (`training_id`),
  KEY `events_registrations_FK` (`registration_id`),
  KEY `events_slots_FK` (`slot_id`),
  KEY `events_participant_groups_FK` (`group_id`),
  CONSTRAINT `events_event_types_FK` FOREIGN KEY (`event_type_id`) REFERENCES `event_types` (`id`),
  CONSTRAINT `events_participant_groups_FK` FOREIGN KEY (`group_id`) REFERENCES `participant_groups` (`id`),
  CONSTRAINT `events_registrations_FK` FOREIGN KEY (`registration_id`) REFERENCES `registrations` (`id`),
  CONSTRAINT `events_slots_FK` FOREIGN KEY (`slot_id`) REFERENCES `slots` (`id`),
  CONSTRAINT `events_trainings_FK` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`),
  CONSTRAINT `events_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `events`
--

LOCK TABLES `events` WRITE;
/*!40000 ALTER TABLE `events` DISABLE KEYS */;
/*!40000 ALTER TABLE `events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `maps_link` varchar(300) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locations`
--

LOCK TABLES `locations` WRITE;
/*!40000 ALTER TABLE `locations` DISABLE KEYS */;
INSERT INTO `locations` VALUES (1,'Школа 2086','https://yandex.ru/maps/org/shkola_2086_osnovnoye_i_sredneye_obrazovaniye/225506986011?si=w4951c7qh6qy4btyk1euw13m64'),(2,'Ломоносовский корпус','https://yandex.ru/maps/org/moskovskiy_gosudarstvenny_universitet_imeni_m_v_lomonosova/101180021688?si=w4951c7qh6qy4btyk1euw13m64'),(3,'Борисовские пруды','https://yandex.ru/maps/org/lodochnaya_stantsiya/11023930393?si=w4951c7qh6qy4btyk1euw13m64'),(4,'Школа 1553','https://yandex.ru/navi/org/shkola_1553_imeni_v_i_vernadskogo_uchebny_korpus_1/10283488828?si=z7b9ze2j7rgxee3686516ha0rm');
/*!40000 ALTER TABLE `locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `telegram_message_id` bigint NOT NULL,
  `training_id` int NOT NULL,
  `telegram_chat_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_massages_trainings_FK` (`training_id`),
  CONSTRAINT `training_massages_trainings_FK` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participant_groups`
--

DROP TABLE IF EXISTS `participant_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participant_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `telegram_chat_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participant_groups`
--

LOCK TABLES `participant_groups` WRITE;
/*!40000 ALTER TABLE `participant_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `participant_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registration_statuses`
--

DROP TABLE IF EXISTS `registration_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registration_statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_statuses`
--

LOCK TABLES `registration_statuses` WRITE;
/*!40000 ALTER TABLE `registration_statuses` DISABLE KEYS */;
INSERT INTO `registration_statuses` VALUES (1,'активна'),(2,'отменена участником'),(3,'тренировка отменена'),(4,'прошла');
/*!40000 ALTER TABLE `registration_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registrations`
--

DROP TABLE IF EXISTS `registrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `training_id` int NOT NULL,
  `user_id` int NOT NULL,
  `registration_status_id` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `registrations_trainings_FK` (`training_id`),
  KEY `registrations_users_FK` (`user_id`),
  KEY `registrations_registration_statuses_FK` (`registration_status_id`),
  CONSTRAINT `registrations_registration_statuses_FK` FOREIGN KEY (`registration_status_id`) REFERENCES `registration_statuses` (`id`),
  CONSTRAINT `registrations_trainings_FK` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`),
  CONSTRAINT `registrations_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registrations`
--

LOCK TABLES `registrations` WRITE;
/*!40000 ALTER TABLE `registrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `registrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slot_statuses`
--

DROP TABLE IF EXISTS `slot_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `slot_statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `slot_statuses`
--

LOCK TABLES `slot_statuses` WRITE;
/*!40000 ALTER TABLE `slot_statuses` DISABLE KEYS */;
INSERT INTO `slot_statuses` VALUES (1,'активен'),(2,'отменён');
/*!40000 ALTER TABLE `slot_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slots`
--

DROP TABLE IF EXISTS `slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `slots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `day_id` int NOT NULL,
  `time` time NOT NULL,
  `location_id` int NOT NULL,
  `slot_status_id` int NOT NULL DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `slots_days_of_week_FK` (`day_id`),
  KEY `slots_locations_FK` (`location_id`),
  KEY `slots_slot_statuses_FK` (`slot_status_id`),
  CONSTRAINT `slots_days_of_week_FK` FOREIGN KEY (`day_id`) REFERENCES `days_of_week` (`id`),
  CONSTRAINT `slots_locations_FK` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`),
  CONSTRAINT `slots_slot_statuses_FK` FOREIGN KEY (`slot_status_id`) REFERENCES `slot_statuses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `slots`
--

LOCK TABLES `slots` WRITE;
/*!40000 ALTER TABLE `slots` DISABLE KEYS */;
INSERT INTO `slots` VALUES (1,1,'17:30:00',1,1),(2,2,'17:30:00',1,1),(3,2,'19:00:00',1,1),(4,3,'17:30:00',1,1),(5,4,'17:30:00',1,1),(6,4,'19:00:00',1,1),(7,5,'19:00:00',4,1);
/*!40000 ALTER TABLE `slots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `slots_groups`
--

DROP TABLE IF EXISTS `slots_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `slots_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `slot_id` int NOT NULL,
  `group_id` int NOT NULL,
  `max_places` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slots_groups_unique` (`slot_id`,`group_id`),
  KEY `slots_groups_groups_FK` (`group_id`),
  KEY `slots_groups_slots_FK` (`slot_id`),
  CONSTRAINT `slots_groups_groups_FK` FOREIGN KEY (`group_id`) REFERENCES `participant_groups` (`id`),
  CONSTRAINT `slots_groups_slots_FK` FOREIGN KEY (`slot_id`) REFERENCES `slots` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `slots_groups`
--

LOCK TABLES `slots_groups` WRITE;
/*!40000 ALTER TABLE `slots_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `slots_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statistics`
--

DROP TABLE IF EXISTS `statistics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statistics` (
  `user_id` int NOT NULL,
  `period_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `trainings_count` int NOT NULL DEFAULT '0',
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `statistics_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statistics`
--

LOCK TABLES `statistics` WRITE;
/*!40000 ALTER TABLE `statistics` DISABLE KEYS */;
/*!40000 ALTER TABLE `statistics` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `training_statuses`
--

DROP TABLE IF EXISTS `training_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `training_statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `training_statuses`
--

LOCK TABLES `training_statuses` WRITE;
/*!40000 ALTER TABLE `training_statuses` DISABLE KEYS */;
INSERT INTO `training_statuses` VALUES (1,'назначена'),(2,'отменена'),(3,'прошла');
/*!40000 ALTER TABLE `training_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trainings`
--

DROP TABLE IF EXISTS `trainings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trainings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date_time` datetime NOT NULL,
  `location_id` int NOT NULL,
  `training_status_id` int NOT NULL DEFAULT '1',
  `slot_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `trainings_locations_FK` (`location_id`),
  KEY `trainings_training_statuses_FK` (`training_status_id`),
  KEY `trainings_slots_FK` (`slot_id`),
  CONSTRAINT `trainings_locations_FK` FOREIGN KEY (`location_id`) REFERENCES `locations` (`id`),
  CONSTRAINT `trainings_slots_FK` FOREIGN KEY (`slot_id`) REFERENCES `slots` (`id`),
  CONSTRAINT `trainings_training_statuses_FK` FOREIGN KEY (`training_status_id`) REFERENCES `training_statuses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trainings`
--

LOCK TABLES `trainings` WRITE;
/*!40000 ALTER TABLE `trainings` DISABLE KEYS */;
/*!40000 ALTER TABLE `trainings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trainings_groups`
--

DROP TABLE IF EXISTS `trainings_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `trainings_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `training_id` int NOT NULL,
  `group_id` int NOT NULL,
  `max_places` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `trainings_groups_unique` (`training_id`,`group_id`),
  KEY `training_groups_groups_FK` (`group_id`),
  KEY `training_groups_trainings_FK` (`training_id`),
  CONSTRAINT `training_groups_groups_FK` FOREIGN KEY (`group_id`) REFERENCES `participant_groups` (`id`),
  CONSTRAINT `training_groups_trainings_FK` FOREIGN KEY (`training_id`) REFERENCES `trainings` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trainings_groups`
--

LOCK TABLES `trainings_groups` WRITE;
/*!40000 ALTER TABLE `trainings_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `trainings_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_statuses`
--

DROP TABLE IF EXISTS `user_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_statuses`
--

LOCK TABLES `user_statuses` WRITE;
/*!40000 ALTER TABLE `user_statuses` DISABLE KEYS */;
INSERT INTO `user_statuses` VALUES (1,'участник'),(2,'участник-админ'),(3,'тренер'),(4,'неактивен');
/*!40000 ALTER TABLE `user_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `user_status_id` int NOT NULL DEFAULT '1',
  `telegram_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_unique` (`telegram_id`),
  KEY `users_user_statuses_FK` (`user_status_id`),
  KEY `idx_users_telegram_id` (`telegram_id`),
  CONSTRAINT `users_user_statuses_FK` FOREIGN KEY (`user_status_id`) REFERENCES `user_statuses` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users_groups`
--

DROP TABLE IF EXISTS `users_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_groups_unique` (`user_id`,`group_id`),
  KEY `users_groups_participant_groups_FK` (`group_id`),
  CONSTRAINT `users_groups_participant_groups_FK` FOREIGN KEY (`group_id`) REFERENCES `participant_groups` (`id`),
  CONSTRAINT `users_groups_users_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users_groups`
--

LOCK TABLES `users_groups` WRITE;
/*!40000 ALTER TABLE `users_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `users_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'rowing_club_test'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-23 13:27:40
