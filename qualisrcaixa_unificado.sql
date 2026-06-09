-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: qualisrcaixa
-- ------------------------------------------------------
-- Server version	8.0.41

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
-- Table structure for table `appquali_arquivoreclamacoes`
--

DROP TABLE IF EXISTS `appquali_arquivoreclamacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_arquivoreclamacoes` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `image` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `data_upload` datetime(6) NOT NULL,
  `reclamacoes_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_arquivoreclamacoes`
--

LOCK TABLES `appquali_arquivoreclamacoes` WRITE;
/*!40000 ALTER TABLE `appquali_arquivoreclamacoes` DISABLE KEYS */;
INSERT INTO `appquali_arquivoreclamacoes` VALUES (1,'itens/Bad_Love.mp3','2025-12-26 05:27:09.165059',1),(2,'itens/Bad_Love_knzSrrh.mp3','2025-12-26 05:28:08.115051',56),(3,'itens/IMG_8690.JPG','2025-12-26 14:55:35.996968',3),(4,'itens/IMG_8518.JPG','2025-12-26 14:59:11.970428',13),(5,'itens/Arquivo_000.jpeg','2025-12-26 20:04:25.719424',57),(6,'itens/IMG_9246.JPG','2025-12-26 20:06:28.740303',58),(7,'itens/IMG_9243.JPG','2025-12-26 20:09:02.928616',59),(8,'itens/IMG_9243.JPG','2025-12-26 20:47:46.585749',60),(9,'itens/IMG_9273.MOV','2025-12-26 23:08:14.458386',60);
/*!40000 ALTER TABLE `appquali_arquivoreclamacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_documento`
--

DROP TABLE IF EXISTS `appquali_documento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_documento` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `arquivos` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `data_upload` datetime(6) NOT NULL,
  `reclamacoes_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_documento`
--

LOCK TABLES `appquali_documento` WRITE;
/*!40000 ALTER TABLE `appquali_documento` DISABLE KEYS */;
INSERT INTO `appquali_documento` VALUES (1,'itens/IMG_9285.JPG','2025-12-26 23:53:13.255694',56),(2,'itens/IMG_9246.JPG','2025-12-27 00:06:00.312737',60);
/*!40000 ALTER TABLE `appquali_documento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_item`
--

DROP TABLE IF EXISTS `appquali_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_item` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `descricao` longtext COLLATE utf8mb3_unicode_ci NOT NULL,
  `criado_em` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_item`
--

LOCK TABLES `appquali_item` WRITE;
/*!40000 ALTER TABLE `appquali_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `appquali_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_itemarquivo`
--

DROP TABLE IF EXISTS `appquali_itemarquivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_itemarquivo` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `arquivo` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `criado_em` datetime(6) NOT NULL,
  `item_id` bigint NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_itemarquivo`
--

LOCK TABLES `appquali_itemarquivo` WRITE;
/*!40000 ALTER TABLE `appquali_itemarquivo` DISABLE KEYS */;
/*!40000 ALTER TABLE `appquali_itemarquivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_reclamacoesarquivo`
--

DROP TABLE IF EXISTS `appquali_reclamacoesarquivo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_reclamacoesarquivo` (
  `id` int NOT NULL AUTO_INCREMENT,
  `itens` varchar(100) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `reclamacoes_id` bigint NOT NULL,
  `data_upload` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=286 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_reclamacoesarquivo`
--

LOCK TABLES `appquali_reclamacoesarquivo` WRITE;
/*!40000 ALTER TABLE `appquali_reclamacoesarquivo` DISABLE KEYS */;
INSERT INTO `appquali_reclamacoesarquivo` VALUES (30,'itens/WhatsApp_Audio_2025-10-29_at_14.57.44.ogg',69,'2025-10-29 01:41:22'),(31,'itens/WhatsApp_Image_2025-10-30_at_12.02.37.jpeg',70,'2025-10-30 01:43:26'),(32,'itens/WhatsApp_Video_2025-10-30_at_13.53.44.mp4',71,'2025-10-30 01:46:48'),(33,'itens/WhatsApp_Image_2025-10-30_at_12.02.37.jpeg',71,'2025-10-30 01:46:48'),(34,'itens/WhatsApp_Audio_2025-10-30_at_17.21.40.ogg',72,'2025-10-30 01:48:16'),(35,'itens/WhatsApp_Image_2025-10-30_at_17.21.39.jpeg',72,'2025-10-30 01:48:16'),(36,'itens/WhatsApp_Image_2025-10-31_at_10.48.40.jpeg',73,'2025-10-31 01:50:39'),(37,'itens/WhatsApp_Image_2025-10-31_at_10.48.37.jpeg',73,'2025-10-31 01:50:39'),(39,'itens/WhatsApp_Image_2025-11-02_at_20.40.18.jpeg',75,'2025-11-02 01:54:38'),(40,'itens/WhatsApp_Image_2025-10-31_at_10.48.40.jpeg',75,'2025-10-31 01:54:38'),(41,'itens/WhatsApp_Image_2025-11-02_at_20.47.48.jpeg',76,'2025-11-02 01:56:11'),(42,'itens/WhatsApp_Image_2025-11-03_at_10.28.42.jpeg',77,'2025-11-03 01:57:53'),(43,'itens/WhatsApp_Image_2025-11-03_at_10.28.41.jpeg',77,'2025-11-03 01:57:53'),(45,'itens/WhatsApp_Image_2025-11-03_at_10.28.42.jpeg',79,'2025-11-03 02:01:59'),(46,'itens/WhatsApp_Image_2025-11-05_at_14.59.13.jpeg',80,'2025-11-05 02:09:37'),(47,'itens/WhatsApp_Video_2025-11-06_at_12.35.02.mp4',81,'2025-11-06 02:11:47'),(48,'itens/WhatsApp_Video_2025-11-06_at_12.35.01.mp4',81,'2025-11-06 02:11:47'),(49,'itens/WhatsApp_Image_2025-11-07_at_11.12.52.jpeg',82,'2025-11-07 02:14:00'),(50,'itens/WhatsApp_Image_2025-11-09_at_10.04.39.jpeg',83,'2025-11-09 02:15:44'),(51,'itens/WhatsApp_Image_2025-11-10_at_09.27.08.jpeg',84,'2025-11-10 02:17:59'),(52,'itens/WhatsApp_Image_2025-11-10_at_09.26.56.jpeg',84,'2025-11-10 02:17:59'),(53,'itens/WhatsApp_Video_2025-11-10_at_09.28.55.mp4',85,'2025-11-10 02:20:28'),(54,'itens/WhatsApp_Video_2025-11-10_at_09.31.08.mp4',86,'2025-11-10 02:22:32'),(55,'itens/WhatsApp_Image_2025-11-11_at_09.17.21.jpeg',88,'2025-11-11 02:28:19'),(56,'itens/WhatsApp_Audio_2025-11-11_at_09.17.20.ogg',88,'2025-11-11 02:28:19'),(57,'itens/WhatsApp_Image_2025-11-11_at_09.17.20.jpeg',88,'2025-11-11 02:28:19'),(61,'itens/WhatsApp_Image_2025-11-12_at_09.04.48.jpeg',89,'2025-11-12 02:30:24'),(62,'itens/WhatsApp_Image_2025-11-12_at_09.04.47.jpeg',89,'2025-11-12 02:30:24'),(63,'itens/WhatsApp_Audio_2025-11-12_at_10.28.49.ogg',90,'2025-11-12 02:34:08'),(64,'itens/WhatsApp_Audio_2025-11-12_at_10.28.48.ogg',90,'2025-11-12 02:34:08'),(65,'itens/WhatsApp_Audio_2025-11-12_at_10.28.46.ogg',90,'2025-11-12 02:34:08'),(66,'itens/WhatsApp_Video_2025-11-12_at_10.28.46.mp4',90,'2025-11-12 02:34:08'),(68,'itens/WhatsApp_Video_2025-11-12_at_10.28.45.mp4',90,'2025-11-12 02:34:08'),(70,'itens/WhatsApp_Image_2025-11-13_at_09.31.19.jpeg',94,'2025-11-13 02:41:40'),(71,'itens/WhatsApp_Image_2025-11-13_at_09.31.17.jpeg',94,'2025-11-13 02:41:40'),(72,'itens/WhatsApp_Image_2025-11-13_at_12.20.01.jpeg',95,'2025-11-13 02:44:28'),(73,'itens/WhatsApp_Audio_2025-11-13_at_12.20.01.ogg',95,'2025-11-13 02:44:28'),(74,'itens/WhatsApp_Video_2025-11-14_at_17.34.08.mp4',97,'2025-11-14 02:47:02'),(75,'itens/WhatsApp_Image_2025-11-16_at_21.49.33.jpeg',98,'2025-11-16 02:48:56'),(76,'itens/WhatsApp_Audio_2025-11-16_at_21.49.32.ogg',98,'2025-11-16 02:48:56'),(77,'itens/WhatsApp_Video_2025-11-17_at_10.41.02.mp4',99,'2025-11-17 02:50:18'),(78,'itens/WhatsApp_Audio_2025-11-17_at_12.27.35.ogg',100,'2025-11-17 02:52:44'),(80,'itens/WhatsApp_Audio_2025-11-18_at_19.10.15.ogg',101,'2025-11-18 02:55:24'),(81,'itens/WhatsApp_Audio_2025-11-20_at_10.00.56.ogg',102,'2025-11-20 02:57:06'),(82,'itens/WhatsApp_Audio_2025-11-18_at_19.10.15.ogg',102,'2025-11-18 02:57:06'),(83,'itens/WhatsApp_Image_2025-11-20_at_17.24.09.jpeg',103,'2025-11-20 02:59:20'),(84,'itens/WhatsApp_Image_2025-11-20_at_17.24.09.jpeg',103,'2025-11-20 02:59:20'),(85,'itens/WhatsApp_Video_2025-11-22_at_10.19.39.mp4',104,'2025-11-22 03:01:12'),(86,'itens/WhatsApp_Image_2025-11-24_at_18.10.00.jpeg',105,'2025-11-24 03:02:37'),(87,'itens/WhatsApp_Image_2025-11-24_at_18.34.41.jpeg',106,'2025-11-24 03:05:13'),(88,'itens/WhatsApp_Image_2025-11-24_at_18.33.53.jpeg',106,'2025-11-24 03:05:13'),(89,'itens/WhatsApp_Image_2025-11-26_at_13.58.23.jpeg',107,'2025-11-26 03:06:36'),(90,'itens/WhatsApp_Image_2025-11-26_at_13.49.42.jpeg',107,'2025-11-26 03:06:36'),(91,'itens/WhatsApp_Audio_2025-11-26_at_16.09.29.ogg',108,'2025-11-26 03:08:55'),(92,'itens/WhatsApp_Audio_2025-11-26_at_16.09.29.ogg',109,'2025-11-26 03:10:23'),(93,'itens/WhatsApp_Audio_2025-11-26_at_16.11.51.ogg',110,'2025-11-26 03:11:12'),(94,'itens/WhatsApp_Audio_2025-12-01_at_09.57.36.ogg',111,'2025-12-01 03:14:42'),(95,'itens/WhatsApp_Image_2025-12-01_at_09.57.36.jpeg',111,'2025-12-01 03:14:42'),(96,'itens/WhatsApp_Video_2025-12-01_at_09.57.35.mp4',111,'2025-12-01 03:14:42'),(97,'itens/WhatsApp_Image_2025-12-01_at_11.41.58.jpeg',112,'2025-12-01 03:16:17'),(98,'itens/WhatsApp_Audio_2025-12-05_at_16.38.02.ogg',113,'2025-12-05 03:18:47'),(99,'itens/WhatsApp_Audio_2025-12-05_at_17.10.10.ogg',114,'2025-12-05 03:21:51'),(100,'itens/WhatsApp_Video_2025-12-05_at_17.10.10.mp4',114,'2025-12-05 03:21:51'),(101,'itens/WhatsApp_Audio_2025-12-08_at_10.11.13.ogg',115,'2025-12-08 03:23:10'),(102,'itens/WhatsApp_Image_2025-12-08_at_10.11.12.jpeg',115,'2025-12-08 03:23:10'),(103,'itens/WhatsApp_Video_2025-12-09_at_18.51.33.mp4',116,'2025-12-09 03:24:24'),(104,'itens/WhatsApp_Audio_2025-12-11_at_12.17.46.ogg',117,'2025-12-11 03:25:59'),(105,'itens/WhatsApp_Image_2025-12-11_at_14.55.04.jpeg',118,'2025-12-11 03:27:44'),(106,'itens/WhatsApp_Image_2025-12-11_at_14.55.04.jpeg',118,'2025-12-11 03:27:44'),(107,'itens/WhatsApp_Image_2025-12-11_at_15.48.52.jpeg',119,'2025-12-11 03:29:35'),(109,'itens/WhatsApp_Image_2025-12-11_at_15.48.53.jpeg',119,'2025-12-11 03:29:35'),(110,'itens/WhatsApp_Image_2025-12-11_at_15.48.54.jpeg',119,'2025-12-11 03:29:35'),(111,'itens/WhatsApp_Image_2025-12-11_at_15.48.55.jpeg',119,'2025-12-11 03:29:35'),(112,'itens/WhatsApp_Audio_2025-12-15_at_13.47.53.ogg',120,'2025-12-15 03:31:01'),(113,'itens/WhatsApp_Image_2025-12-15_at_13.47.53.jpeg',120,'2025-12-15 03:31:01'),(115,'itens/WhatsApp_Image_2025-12-17_at_10.35.35.jpeg',121,'2025-12-17 03:32:34'),(116,'itens/WhatsApp_Image_2025-12-17_at_10.35.34.jpeg',121,'2025-12-17 03:32:34'),(118,'itens/WhatsApp_Image_2025-12-17_at_13.36.19.jpeg',122,'2025-12-17 03:34:41'),(119,'itens/WhatsApp_Image_2025-12-17_at_13.36.18.jpeg',122,'2025-12-17 03:34:41'),(120,'itens/WhatsApp_Image_2025-12-18_at_17.53.25.jpeg',123,'2025-12-18 03:35:47'),(121,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg',124,'2025-12-23 03:38:23'),(122,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg',124,'2025-12-23 03:38:23'),(123,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg',124,'2025-12-23 03:38:23'),(124,'itens/WhatsApp_Image_2025-12-23_at_14.43.57.jpeg',124,'2025-12-23 03:38:23'),(232,'',125,'2025-11-04 18:15:54'),(233,'',126,'2025-11-10 18:15:54'),(234,'',127,'2025-11-12 18:15:54'),(235,'',128,'2025-11-12 18:15:54'),(236,'',129,'2025-11-13 18:15:54'),(237,'',130,'2025-11-13 18:15:54'),(238,'itens/WhatsApp_Image_2026-01-05_at_12.13.18.jpeg',131,'2026-01-06 03:40:55'),(239,'',132,'2026-01-06 03:47:24'),(240,'itens/WhatsApp_Image_2026-01-05_at_09_lBVkuQB.16.46.jpeg',133,'2026-01-06 03:52:58'),(241,'itens/WhatsApp_Audio_2026-01-05_at_10.43.43_1.mpeg',134,'2026-01-06 04:13:24'),(242,'itens/WhatsApp_Image_2026-01-05_at_10.43.43_1.jpeg',134,'2026-01-06 04:13:24'),(243,'itens/WhatsApp_Audio_2026-01-05_at_11_DEj6knw.34.23.ogg',135,'2026-01-06 04:18:04'),(244,'itens/WhatsApp_Audio_2026-01-05_at_11_OtKfonp.34.22.ogg',135,'2026-01-06 04:18:04'),(245,'itens/WhatsApp_Image_2026-01-05_at_11.34.21.jpeg',135,'2026-01-06 04:18:04'),(246,'itens/WhatsApp_Image_2026-01-05_at_11.34.19.jpeg',135,'2026-01-06 04:18:04'),(247,'itens/WhatsApp_Image_2026-01-05_at_12.13.18_2.jpeg',136,'2026-01-06 04:21:12'),(248,'itens/WhatsApp_Image_2026-01-05_at_12_C0EamLK.13.18_2.jpeg',137,'2026-01-06 04:26:14'),(249,'itens/WhatsApp_Image_2026-01-05_at_13.45.02.jpeg',138,'2026-01-06 04:33:39'),(250,'itens/WhatsApp_Video_2026-01-05_at_17.14.54.mp4',139,'2026-01-06 04:36:32'),(251,'itens/WhatsApp_Audio_2026-01-05_at_17.14.53.ogg',139,'2026-01-06 04:36:32'),(252,'itens/WhatsApp_Audio_2026-01-05_at_17.14.52_1.ogg',139,'2026-01-06 04:36:32'),(253,'itens/WhatsApp_Audio_2026-01-05_at_17.14.52.ogg',139,'2026-01-06 04:36:32'),(254,'itens/WhatsApp_Audio_2026-01-05_at_17.14.51.ogg',139,'2026-01-06 04:36:32'),(255,'itens/WhatsApp_Video_2026-01-05_at_17.58.51.mp4',140,'2026-01-06 04:38:22'),(256,'itens/Curriculo_Antonio_Prado.pdf',141,'2026-01-06 16:52:17'),(257,'itens/Nunca_volte.txt',142,'2026-01-06 17:07:07'),(258,'itens/6_perguntas.txt',143,'2026-01-06 21:27:10'),(259,'itens/6_perguntas_rwh6m8J.txt',144,'2026-01-06 21:34:49'),(260,'itens/8_regras.url',145,'2026-01-06 21:38:40'),(261,'itens/6_perguntas_FskV3rV.txt',146,'2026-01-06 21:55:46'),(262,'itens/6_perguntas_NptYXa6.txt',147,'2026-01-06 21:57:27'),(263,'itens/pdf.pdf',148,'2026-01-06 22:05:24'),(264,'itens/Nunca_volte_A84F4S6.txt',149,'2026-01-06 22:16:38'),(265,'itens/8_regras_PIpXPsa.url',150,'2026-01-06 22:46:09'),(266,'itens/Curriculo_19_05_2025_2.pdf',151,'2026-01-06 22:46:33'),(267,'itens/Nunca_volte_4PpUyw1.txt',152,'2026-01-06 22:55:05'),(268,'itens/update_nov_para_out_2025.txt',153,'2026-01-06 22:58:44'),(269,'itens/8_regras_4xqqxAM.url',154,'2026-01-06 23:00:05'),(270,'itens/8_regras_coKG8pY.url',155,'2026-01-06 23:06:34'),(271,'itens/marisa3.JPG',156,'2026-01-06 23:06:59'),(272,'itens/Nunca_volte_c5BvauW.txt',157,'2026-01-06 23:19:54'),(273,'itens/6_perguntas_2SRzGkI.txt',158,'2026-01-06 23:20:25'),(274,'itens/Nunca_volte_6YhhD14.txt',159,'2026-01-06 23:24:13'),(275,'itens/Nunca_volte_u4srnOJ.txt',160,'2026-01-06 23:36:15'),(276,'itens/6_perguntas_xo9EWim.txt',161,'2026-01-06 23:37:29'),(277,'itens/WhatsApp_Video_2026-01-05_at_17_Kfz5tDJ.58.51.mp4',162,'2026-01-06 23:38:57'),(278,'itens/WhatsApp_Audio_2026-01-05_at_17_1fnv9Pj.14.52.ogg',163,'2026-01-06 23:45:49'),(279,'itens/pdf_ujiDAsX.pdf',164,'2026-01-06 23:50:40'),(280,'itens/WhatsApp_Image_2026-01-05_at_12_6ZDDpE0.13.18.jpeg',165,'2026-01-06 23:52:05'),(281,'itens/WhatsApp_Video_2026-01-05_at_17_8mtKhRI.58.51.mp4',166,'2026-01-08 18:30:00'),(282,'itens/WhatsApp_Video_2026-01-05_at_17_w1EFSvE.58.51.mp4',167,'2026-01-10 13:56:03'),(283,'itens/StoneReduced.jpg',168,'2026-01-11 02:18:35'),(284,'itens/PHOTO-2026-01-07-17-22-47.jpg',168,'2026-01-11 02:18:35'),(285,'itens/WhatsApp_Video_2026-01-05_at_17_KD0JVKU.58.51.mp4',168,'2026-01-11 02:18:35');
/*!40000 ALTER TABLE `appquali_reclamacoesarquivo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_reclamacoesarquivo_sagrada`
--

DROP TABLE IF EXISTS `appquali_reclamacoesarquivo_sagrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_reclamacoesarquivo_sagrada` (
  `id` int NOT NULL DEFAULT '0',
  `itens` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `data_upload` datetime(6) NOT NULL,
  `reclamacoes_id` bigint NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_reclamacoesarquivo_sagrada`
--

LOCK TABLES `appquali_reclamacoesarquivo_sagrada` WRITE;
/*!40000 ALTER TABLE `appquali_reclamacoesarquivo_sagrada` DISABLE KEYS */;
INSERT INTO `appquali_reclamacoesarquivo_sagrada` VALUES (30,'itens/WhatsApp_Audio_2025-10-29_at_14.57.44.ogg','2025-12-31 01:41:22.783759',69),(31,'itens/WhatsApp_Image_2025-10-30_at_12.02.37.jpeg','2025-12-31 01:43:26.521919',70),(32,'itens/WhatsApp_Video_2025-10-30_at_13.53.44.mp4','2025-12-31 01:46:48.916786',71),(33,'itens/WhatsApp_Image_2025-10-30_at_12.02.37.jpeg','2025-12-31 01:46:48.932496',71),(34,'itens/WhatsApp_Audio_2025-10-30_at_17.21.40.ogg','2025-12-31 01:48:16.401325',72),(35,'itens/WhatsApp_Image_2025-10-30_at_17.21.39.jpeg','2025-12-31 01:48:16.406040',72),(36,'itens/WhatsApp_Image_2025-10-31_at_10.48.40.jpeg','2025-12-31 01:50:39.034912',73),(37,'itens/WhatsApp_Image_2025-10-31_at_10.48.37.jpeg','2025-12-31 01:50:39.034912',73),(39,'itens/WhatsApp_Image_2025-11-02_at_20.40.18.jpeg','2025-12-31 01:54:38.211437',75),(40,'itens/WhatsApp_Image_2025-10-31_at_10.48.40.jpeg','2025-12-31 01:54:38.215557',75),(41,'itens/WhatsApp_Image_2025-11-02_at_20.47.48.jpeg','2025-12-31 01:56:11.134340',76),(42,'itens/WhatsApp_Image_2025-11-03_at_10.28.42.jpeg','2025-12-31 01:57:53.418373',77),(43,'itens/WhatsApp_Image_2025-11-03_at_10.28.41.jpeg','2025-12-31 01:57:53.418373',77),(45,'itens/WhatsApp_Image_2025-11-03_at_10.28.42.jpeg','2025-12-31 02:01:59.408997',79),(46,'itens/WhatsApp_Image_2025-11-05_at_14.59.13.jpeg','2025-12-31 02:09:37.473968',80),(47,'itens/WhatsApp_Video_2025-11-06_at_12.35.02.mp4','2025-12-31 02:11:47.327604',81),(48,'itens/WhatsApp_Video_2025-11-06_at_12.35.01.mp4','2025-12-31 02:11:47.327604',81),(49,'itens/WhatsApp_Image_2025-11-07_at_11.12.52.jpeg','2025-12-31 02:14:00.096417',82),(50,'itens/WhatsApp_Image_2025-11-09_at_10.04.39.jpeg','2025-12-31 02:15:44.069247',83),(51,'itens/WhatsApp_Image_2025-11-10_at_09.27.08.jpeg','2025-12-31 02:17:59.222382',84),(52,'itens/WhatsApp_Image_2025-11-10_at_09.26.56.jpeg','2025-12-31 02:17:59.228511',84),(53,'itens/WhatsApp_Video_2025-11-10_at_09.28.55.mp4','2025-12-31 02:20:28.028013',85),(54,'itens/WhatsApp_Video_2025-11-10_at_09.31.08.mp4','2025-12-31 02:22:32.536515',86),(55,'itens/WhatsApp_Image_2025-11-11_at_09.17.21.jpeg','2025-12-31 02:28:19.749969',88),(56,'itens/WhatsApp_Audio_2025-11-11_at_09.17.20.ogg','2025-12-31 02:28:19.751989',88),(57,'itens/WhatsApp_Image_2025-11-11_at_09.17.20.jpeg','2025-12-31 02:28:19.757072',88),(61,'itens/WhatsApp_Image_2025-11-12_at_09.04.48.jpeg','2025-12-31 02:30:24.588538',89),(62,'itens/WhatsApp_Image_2025-11-12_at_09.04.47.jpeg','2025-12-31 02:30:24.589560',89),(63,'itens/WhatsApp_Audio_2025-11-12_at_10.28.49.ogg','2025-12-31 02:34:08.759406',90),(64,'itens/WhatsApp_Audio_2025-11-12_at_10.28.48.ogg','2025-12-31 02:34:08.772550',90),(65,'itens/WhatsApp_Audio_2025-11-12_at_10.28.46.ogg','2025-12-31 02:34:08.787525',90),(66,'itens/WhatsApp_Video_2025-11-12_at_10.28.46.mp4','2025-12-31 02:34:08.807791',90),(68,'itens/WhatsApp_Video_2025-11-12_at_10.28.45.mp4','2025-12-31 02:34:08.836254',90),(70,'itens/WhatsApp_Image_2025-11-13_at_09.31.19.jpeg','2025-12-31 02:41:40.488460',94),(71,'itens/WhatsApp_Image_2025-11-13_at_09.31.17.jpeg','2025-12-31 02:41:40.492536',94),(72,'itens/WhatsApp_Image_2025-11-13_at_12.20.01.jpeg','2025-12-31 02:44:28.843768',95),(73,'itens/WhatsApp_Audio_2025-11-13_at_12.20.01.ogg','2025-12-31 02:44:28.847315',95),(74,'itens/WhatsApp_Video_2025-11-14_at_17.34.08.mp4','2025-12-31 02:47:02.363057',97),(75,'itens/WhatsApp_Image_2025-11-16_at_21.49.33.jpeg','2025-12-31 02:48:56.402738',98),(76,'itens/WhatsApp_Audio_2025-11-16_at_21.49.32.ogg','2025-12-31 02:48:56.405923',98),(77,'itens/WhatsApp_Video_2025-11-17_at_10.41.02.mp4','2025-12-31 02:50:18.341765',99),(78,'itens/WhatsApp_Audio_2025-11-17_at_12.27.35.ogg','2025-12-31 02:52:44.170705',100),(80,'itens/WhatsApp_Audio_2025-11-18_at_19.10.15.ogg','2025-12-31 02:55:24.566137',101),(81,'itens/WhatsApp_Audio_2025-11-20_at_10.00.56.ogg','2025-12-31 02:57:06.421571',102),(82,'itens/WhatsApp_Audio_2025-11-18_at_19.10.15.ogg','2025-12-31 02:57:06.429251',102),(83,'itens/WhatsApp_Image_2025-11-20_at_17.24.09.jpeg','2025-12-31 02:59:20.599828',103),(84,'itens/WhatsApp_Image_2025-11-20_at_17.24.09.jpeg','2025-12-31 02:59:20.599828',103),(85,'itens/WhatsApp_Video_2025-11-22_at_10.19.39.mp4','2025-12-31 03:01:12.671409',104),(86,'itens/WhatsApp_Image_2025-11-24_at_18.10.00.jpeg','2025-12-31 03:02:37.747596',105),(87,'itens/WhatsApp_Image_2025-11-24_at_18.34.41.jpeg','2025-12-31 03:05:13.448715',106),(88,'itens/WhatsApp_Image_2025-11-24_at_18.33.53.jpeg','2025-12-31 03:05:13.452045',106),(89,'itens/WhatsApp_Image_2025-11-26_at_13.58.23.jpeg','2025-12-31 03:06:36.004617',107),(90,'itens/WhatsApp_Image_2025-11-26_at_13.49.42.jpeg','2025-12-31 03:06:36.008213',107),(91,'itens/WhatsApp_Audio_2025-11-26_at_16.09.29.ogg','2025-12-31 03:08:55.235187',108),(92,'itens/WhatsApp_Audio_2025-11-26_at_16.09.29.ogg','2025-12-31 03:10:23.578003',109),(93,'itens/WhatsApp_Audio_2025-11-26_at_16.11.51.ogg','2025-12-31 03:11:12.990587',110),(94,'itens/WhatsApp_Audio_2025-12-01_at_09.57.36.ogg','2025-12-31 03:14:42.522152',111),(95,'itens/WhatsApp_Image_2025-12-01_at_09.57.36.jpeg','2025-12-31 03:14:42.533105',111),(96,'itens/WhatsApp_Video_2025-12-01_at_09.57.35.mp4','2025-12-31 03:14:42.548182',111),(97,'itens/WhatsApp_Image_2025-12-01_at_11.41.58.jpeg','2025-12-31 03:16:17.823005',112),(98,'itens/WhatsApp_Audio_2025-12-05_at_16.38.02.ogg','2025-12-31 03:18:47.643868',113),(99,'itens/WhatsApp_Audio_2025-12-05_at_17.10.10.ogg','2025-12-31 03:21:51.030553',114),(100,'itens/WhatsApp_Video_2025-12-05_at_17.10.10.mp4','2025-12-31 03:21:51.036766',114),(101,'itens/WhatsApp_Audio_2025-12-08_at_10.11.13.ogg','2025-12-31 03:23:10.283908',115),(102,'itens/WhatsApp_Image_2025-12-08_at_10.11.12.jpeg','2025-12-31 03:23:10.287845',115),(103,'itens/WhatsApp_Video_2025-12-09_at_18.51.33.mp4','2025-12-31 03:24:24.615793',116),(104,'itens/WhatsApp_Audio_2025-12-11_at_12.17.46.ogg','2025-12-31 03:25:59.323595',117),(105,'itens/WhatsApp_Image_2025-12-11_at_14.55.04.jpeg','2025-12-31 03:27:44.860376',118),(106,'itens/WhatsApp_Image_2025-12-11_at_14.55.04.jpeg','2025-12-31 03:27:44.865465',118),(107,'itens/WhatsApp_Image_2025-12-11_at_15.48.52.jpeg','2025-12-31 03:29:35.348992',119),(109,'itens/WhatsApp_Image_2025-12-11_at_15.48.53.jpeg','2025-12-31 03:29:35.352004',119),(110,'itens/WhatsApp_Image_2025-12-11_at_15.48.54.jpeg','2025-12-31 03:29:35.360209',119),(111,'itens/WhatsApp_Image_2025-12-11_at_15.48.55.jpeg','2025-12-31 03:29:35.361372',119),(112,'itens/WhatsApp_Audio_2025-12-15_at_13.47.53.ogg','2025-12-31 03:31:01.597242',120),(113,'itens/WhatsApp_Image_2025-12-15_at_13.47.53.jpeg','2025-12-31 03:31:01.601648',120),(115,'itens/WhatsApp_Image_2025-12-17_at_10.35.35.jpeg','2025-12-31 03:32:34.738204',121),(116,'itens/WhatsApp_Image_2025-12-17_at_10.35.34.jpeg','2025-12-31 03:32:34.740689',121),(118,'itens/WhatsApp_Image_2025-12-17_at_13.36.19.jpeg','2025-12-31 03:34:41.993216',122),(119,'itens/WhatsApp_Image_2025-12-17_at_13.36.18.jpeg','2025-12-31 03:34:41.994260',122),(120,'itens/WhatsApp_Image_2025-12-18_at_17.53.25.jpeg','2025-12-31 03:35:47.439501',123),(121,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg','2025-12-31 03:38:23.443352',124),(122,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg','2025-12-31 03:38:23.443352',124),(123,'itens/WhatsApp_Image_2025-12-23_at_14.43.56.jpeg','2025-12-31 03:38:23.443352',124),(124,'itens/WhatsApp_Image_2025-12-23_at_14.43.57.jpeg','2025-12-31 03:38:23.443352',124),(136,'itens/WhatsApp_Video_2025-12-09_at_18.51.33_1.mp4','2026-01-04 21:26:52.340287',143);
/*!40000 ALTER TABLE `appquali_reclamacoesarquivo_sagrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `appquali_semanano`
--

DROP TABLE IF EXISTS `appquali_semanano`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `appquali_semanano` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `semana` int unsigned NOT NULL,
  `ano` int unsigned NOT NULL,
  `data_fim` date DEFAULT NULL,
  `data_inicio` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `appquali_semanano_chk_1` CHECK ((`semana` >= 0)),
  CONSTRAINT `appquali_semanano_chk_2` CHECK ((`ano` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `appquali_semanano`
--

LOCK TABLES `appquali_semanano` WRITE;
/*!40000 ALTER TABLE `appquali_semanano` DISABLE KEYS */;
INSERT INTO `appquali_semanano` VALUES (1,1,2026,'2026-01-04','2025-12-29'),(2,2,2026,'2026-01-11','2026-01-05'),(3,2,2026,'2026-01-11','2026-01-05'),(4,2,2026,'2026-01-11','2026-01-05'),(5,15,2025,'2025-04-13','2025-04-07'),(6,2,2025,'2025-01-12','2025-01-06'),(7,46,2026,'2026-11-15','2026-11-09'),(8,46,2025,'2025-11-16','2025-11-10'),(9,2,2026,'2026-01-11','2026-01-05'),(10,35,2026,'2026-08-30','2026-08-24'),(11,33,2025,'2025-08-17','2025-08-11'),(12,53,2026,'2027-01-03','2026-12-28'),(13,15,2026,'2026-04-12','2026-04-06'),(14,17,2035,'2035-04-29','2035-04-23'),(15,2,2026,'2026-01-11','2026-01-05'),(16,2,2026,'2026-01-11','2026-01-05'),(17,44,2025,'2025-11-02','2025-10-27'),(18,44,2025,'2025-11-02','2025-10-27'),(19,2,2026,'2026-01-11','2026-01-05'),(20,2,2026,'2026-01-11','2026-01-05'),(21,2,2025,'2025-01-12','2025-01-06'),(22,2,2025,'2025-01-12','2025-01-06'),(23,40,2025,'2025-10-05','2025-09-29'),(24,2,2025,'2025-01-12','2025-01-06'),(25,2,2025,'2025-01-12','2025-01-06'),(26,2,2025,'2025-01-12','2025-01-06'),(27,2,2025,'2025-01-12','2025-01-06'),(28,2,2025,'2025-01-12','2025-01-06'),(29,2,2025,'2025-01-12','2025-01-06'),(30,2,2025,'2025-01-12','2025-01-06'),(31,2,2025,'2025-01-12','2025-01-06'),(32,2,2025,'2025-01-12','2025-01-06'),(33,2,2025,'2025-01-12','2025-01-06'),(34,2,2025,'2025-01-12','2025-01-06'),(35,2,2025,'2025-01-12','2025-01-06'),(36,2,2025,'2025-01-12','2025-01-06'),(37,2,2025,'2025-01-12','2025-01-06'),(38,2,2025,'2025-01-12','2025-01-06'),(39,2,2025,'2025-01-12','2025-01-06'),(40,2,2025,'2025-01-12','2025-01-06'),(41,2,2025,'2025-01-12','2025-01-06'),(42,2,2025,'2025-01-12','2025-01-06'),(43,2,2026,'2026-01-11','2026-01-05'),(44,44,2025,'2025-11-02','2025-10-27'),(45,53,2026,'2027-01-03','2026-12-28'),(46,53,2026,'2027-01-03','2026-12-28'),(47,2,2025,'2025-01-12','2025-01-06'),(48,2,2025,'2025-01-12','2025-01-06'),(49,2,2025,'2025-01-12','2025-01-06'),(50,8,2035,'2035-02-25','2035-02-19'),(51,9,2035,'2035-03-04','2035-02-26'),(52,38,2026,'2026-09-20','2026-09-14'),(53,2,2025,'2025-01-12','2025-01-06'),(54,47,2025,'2025-11-23','2025-11-17'),(55,35,2026,'2026-08-30','2026-08-24'),(56,48,2045,'2045-12-03','2045-11-27'),(57,25,2025,'2025-06-22','2025-06-16'),(58,47,2025,'2025-11-23','2025-11-17'),(59,46,2025,'2025-11-16','2025-11-10'),(60,45,2025,'2025-11-09','2025-11-03'),(61,45,2026,'2026-11-08','2026-11-02'),(62,32,2026,'2026-08-09','2026-08-03'),(63,27,2027,'2027-07-11','2027-07-05'),(64,34,2025,'2025-08-24','2025-08-18'),(65,33,2025,'2025-08-17','2025-08-11'),(66,25,2025,'2025-06-22','2025-06-16'),(67,44,2025,'2025-11-02','2025-10-27'),(68,45,2025,'2025-11-09','2025-11-03'),(69,46,2025,'2025-11-16','2025-11-10'),(70,46,2025,'2025-11-16','2025-11-10'),(71,46,2025,'2025-11-16','2025-11-10'),(72,2,2025,'2025-01-12','2025-01-06'),(73,3,2025,'2025-01-19','2025-01-13'),(74,3,2026,'2026-01-18','2026-01-12'),(75,2,2026,'2026-01-11','2026-01-05'),(76,1,2026,'2026-01-04','2025-12-29'),(77,2,2026,'2026-01-11','2026-01-05'),(78,2,2026,'2026-01-11','2026-01-05'),(79,3,2026,'2026-01-18','2026-01-12'),(80,4,2026,'2026-01-25','2026-01-19'),(81,1,2025,'2025-01-05','2024-12-30'),(82,2,2025,'2025-01-12','2025-01-06'),(83,11,2025,'2025-03-16','2025-03-10'),(84,46,2025,'2025-11-16','2025-11-10'),(85,46,2025,'2025-11-16','2025-11-10');
/*!40000 ALTER TABLE `appquali_semanano` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb3_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',3,'add_permission'),(6,'Can change permission',3,'change_permission'),(7,'Can delete permission',3,'delete_permission'),(8,'Can view permission',3,'view_permission'),(9,'Can add group',2,'add_group'),(10,'Can change group',2,'change_group'),(11,'Can delete group',2,'delete_group'),(12,'Can view group',2,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add auth group',7,'add_authgroup'),(26,'Can change auth group',7,'change_authgroup'),(27,'Can delete auth group',7,'delete_authgroup'),(28,'Can view auth group',7,'view_authgroup'),(29,'Can add auth group permissions',8,'add_authgrouppermissions'),(30,'Can change auth group permissions',8,'change_authgrouppermissions'),(31,'Can delete auth group permissions',8,'delete_authgrouppermissions'),(32,'Can view auth group permissions',8,'view_authgrouppermissions'),(33,'Can add auth permission',9,'add_authpermission'),(34,'Can change auth permission',9,'change_authpermission'),(35,'Can delete auth permission',9,'delete_authpermission'),(36,'Can view auth permission',9,'view_authpermission'),(37,'Can add auth user',10,'add_authuser'),(38,'Can change auth user',10,'change_authuser'),(39,'Can delete auth user',10,'delete_authuser'),(40,'Can view auth user',10,'view_authuser'),(41,'Can add auth user groups',11,'add_authusergroups'),(42,'Can change auth user groups',11,'change_authusergroups'),(43,'Can delete auth user groups',11,'delete_authusergroups'),(44,'Can view auth user groups',11,'view_authusergroups'),(45,'Can add auth user user permissions',12,'add_authuseruserpermissions'),(46,'Can change auth user user permissions',12,'change_authuseruserpermissions'),(47,'Can delete auth user user permissions',12,'delete_authuseruserpermissions'),(48,'Can view auth user user permissions',12,'view_authuseruserpermissions'),(49,'Can add django admin log',13,'add_djangoadminlog'),(50,'Can change django admin log',13,'change_djangoadminlog'),(51,'Can delete django admin log',13,'delete_djangoadminlog'),(52,'Can view django admin log',13,'view_djangoadminlog'),(53,'Can add django content type',14,'add_djangocontenttype'),(54,'Can change django content type',14,'change_djangocontenttype'),(55,'Can delete django content type',14,'delete_djangocontenttype'),(56,'Can view django content type',14,'view_djangocontenttype'),(57,'Can add django migrations',15,'add_djangomigrations'),(58,'Can change django migrations',15,'change_djangomigrations'),(59,'Can delete django migrations',15,'delete_djangomigrations'),(60,'Can view django migrations',15,'view_djangomigrations'),(61,'Can add django session',16,'add_djangosession'),(62,'Can change django session',16,'change_djangosession'),(63,'Can delete django session',16,'delete_djangosession'),(64,'Can view django session',16,'view_djangosession'),(65,'Can add empresa',17,'add_empresa'),(66,'Can change empresa',17,'change_empresa'),(67,'Can delete empresa',17,'delete_empresa'),(68,'Can view empresa',17,'view_empresa'),(69,'Can add produtos',18,'add_produtos'),(70,'Can change produtos',18,'change_produtos'),(71,'Can delete produtos',18,'delete_produtos'),(72,'Can view produtos',18,'view_produtos'),(73,'Can add reclamacoes',19,'add_reclamacoes'),(74,'Can change reclamacoes',19,'change_reclamacoes'),(75,'Can delete reclamacoes',19,'delete_reclamacoes'),(76,'Can view reclamacoes',19,'view_reclamacoes'),(77,'Can add tipos defeitos',20,'add_tiposdefeitos'),(78,'Can change tipos defeitos',20,'change_tiposdefeitos'),(79,'Can delete tipos defeitos',20,'delete_tiposdefeitos'),(80,'Can view tipos defeitos',20,'view_tiposdefeitos'),(81,'Can add reclamacoes2',21,'add_reclamacoes2'),(82,'Can change reclamacoes2',21,'change_reclamacoes2'),(83,'Can delete reclamacoes2',21,'delete_reclamacoes2'),(84,'Can view reclamacoes2',21,'view_reclamacoes2'),(85,'Can add tecnologia',22,'add_tecnologia'),(86,'Can change tecnologia',22,'change_tecnologia'),(87,'Can delete tecnologia',22,'delete_tecnologia'),(88,'Can view tecnologia',22,'view_tecnologia'),(89,'Can add reclamacoes arquivo',23,'add_reclamacoesarquivo'),(90,'Can change reclamacoes arquivo',23,'change_reclamacoesarquivo'),(91,'Can delete reclamacoes arquivo',23,'delete_reclamacoesarquivo'),(92,'Can view reclamacoes arquivo',23,'view_reclamacoesarquivo'),(93,'Can add arquivo reclamacoes',24,'add_arquivoreclamacoes'),(94,'Can change arquivo reclamacoes',24,'change_arquivoreclamacoes'),(95,'Can delete arquivo reclamacoes',24,'delete_arquivoreclamacoes'),(96,'Can view arquivo reclamacoes',24,'view_arquivoreclamacoes'),(97,'Can add documento',25,'add_documento'),(98,'Can change documento',25,'change_documento'),(99,'Can delete documento',25,'delete_documento'),(100,'Can view documento',25,'view_documento'),(101,'Can add item arquivo',26,'add_itemarquivo'),(102,'Can change item arquivo',26,'change_itemarquivo'),(103,'Can delete item arquivo',26,'delete_itemarquivo'),(104,'Can view item arquivo',26,'view_itemarquivo'),(105,'Can add item',27,'add_item'),(106,'Can change item',27,'change_item'),(107,'Can delete item',27,'delete_item'),(108,'Can view item',27,'view_item'),(109,'Can add seman ano',28,'add_semanano'),(110,'Can change seman ano',28,'change_semanano'),(111,'Can delete seman ano',28,'delete_semanano'),(112,'Can view seman ano',28,'view_semanano');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb3_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb3_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb3_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb3_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb3_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1200000$abCRVICtJzxRxnb5d98Z7h$1TqC1REnYOrcvxbEfHsosVBsEwAKHyB+xTfHif4EQsE=','2026-03-03 23:34:05.321828',1,'admin','','','',1,1,'2025-12-23 20:43:30.365496');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb3_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb3_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb3_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-12-24 01:49:30.623221','11','Produtos object (11)',2,'[{\"changed\": {\"fields\": [\"Produto\"]}}]',18,1),(2,'2025-12-24 04:18:23.401563','42','Reclamacoes2 object (42)',2,'[{\"changed\": {\"fields\": [\"Id tecnol\"]}}]',21,1),(3,'2025-12-24 04:18:44.140890','42','Reclamacoes2 object (42)',2,'[{\"changed\": {\"fields\": [\"Id empresa\"]}}]',21,1),(4,'2025-12-24 04:18:55.639425','41','Reclamacoes2 object (41)',2,'[{\"changed\": {\"fields\": [\"Id tecnol\", \"Id empresa\"]}}]',21,1),(5,'2025-12-25 15:44:13.273076','56','Reclamacoes object (56)',1,'[{\"added\": {}}]',19,1),(6,'2025-12-25 15:57:27.069177','56','Reclamacoes object (56)',2,'[{\"changed\": {\"fields\": [\"Arquivo\"]}}]',19,1),(7,'2025-12-26 05:10:16.055464','56','Reclamacoes object (56)',2,'[]',19,1),(8,'2025-12-26 05:27:09.166058','1','KOBAYASHI\'S',1,'[{\"added\": {}}]',24,1),(9,'2025-12-26 05:28:08.115051','2','Antonio Prado',1,'[{\"added\": {}}]',24,1),(10,'2025-12-26 05:28:59.416702','2','Antonio Prado',2,'[{\"changed\": {\"fields\": [\"Arquivos\"]}}]',24,1),(11,'2025-12-26 14:55:36.013751','3','KOBAYASHI\'S',1,'[{\"added\": {}}]',24,1),(12,'2025-12-26 14:59:11.970428','4','GIACOMOS',1,'[{\"added\": {}}]',24,1),(13,'2025-12-26 15:00:52.940535','4','GIACOMOS',2,'[{\"changed\": {\"fields\": [\"Arquivos\"]}}]',24,1),(14,'2025-12-26 15:01:57.925734','3','DIDIO PIZZA SANTA CECILIA',2,'[{\"changed\": {\"fields\": [\"Reclamacoes\", \"Arquivos\"]}}]',24,1),(15,'2025-12-26 23:08:14.458386','9','Antonio Prado3',1,'[{\"added\": {}}]',24,1),(16,'2025-12-26 23:53:13.255694','1','Antonio Prado',1,'[{\"added\": {}}]',25,1),(17,'2025-12-27 00:06:00.312737','2','Antonio Prado3',1,'[{\"added\": {}}]',25,1),(18,'2025-12-28 20:46:29.161578','1','VINCI',1,'[{\"added\": {}}]',23,1),(19,'2025-12-28 20:49:11.818135','1','VINCI',2,'[{\"changed\": {\"fields\": [\"Arquivos / Anexos: \"]}}]',23,1),(20,'2025-12-29 03:27:01.413674','8','KOBAYASHI\'S',1,'[{\"added\": {}}]',23,1),(21,'2025-12-31 04:32:47.636558','14','Produtos object (14)',1,'[{\"added\": {}}]',18,1),(22,'2025-12-31 04:33:34.759198','1','Produtos object (1)',2,'[{\"changed\": {\"fields\": [\"Produto\"]}}]',18,1),(23,'2025-12-31 05:13:02.281233','1','Produtos object (1)',2,'[{\"changed\": {\"fields\": [\"Produto\"]}}]',18,1),(24,'2026-01-06 03:32:43.119902','15','Produtos object (15)',1,'[{\"added\": {}}]',18,1),(25,'2026-01-07 17:42:53.353963','16','Produtos object (16)',1,'[{\"added\": {}}]',18,1),(26,'2026-01-07 17:43:03.270410','17','Produtos object (17)',1,'[{\"added\": {}}]',18,1),(27,'2026-01-07 17:43:13.830020','18','Produtos object (18)',1,'[{\"added\": {}}]',18,1);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(24,'appQuali','arquivoreclamacoes'),(7,'appQuali','authgroup'),(8,'appQuali','authgrouppermissions'),(9,'appQuali','authpermission'),(10,'appQuali','authuser'),(11,'appQuali','authusergroups'),(12,'appQuali','authuseruserpermissions'),(13,'appQuali','djangoadminlog'),(14,'appQuali','djangocontenttype'),(15,'appQuali','djangomigrations'),(16,'appQuali','djangosession'),(25,'appQuali','documento'),(17,'appQuali','empresa'),(27,'appQuali','item'),(26,'appQuali','itemarquivo'),(18,'appQuali','produtos'),(19,'appQuali','reclamacoes'),(21,'appQuali','reclamacoes2'),(23,'appQuali','reclamacoesarquivo'),(28,'appQuali','semanano'),(22,'appQuali','tecnologia'),(20,'appQuali','tiposdefeitos'),(2,'auth','group'),(3,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb3_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb3_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-12-23 20:42:26.665502'),(2,'auth','0001_initial','2025-12-23 20:42:27.331600'),(3,'admin','0001_initial','2025-12-23 20:42:27.462852'),(4,'admin','0002_logentry_remove_auto_add','2025-12-23 20:42:27.478478'),(5,'admin','0003_logentry_add_action_flag_choices','2025-12-23 20:42:27.506551'),(6,'contenttypes','0002_remove_content_type_name','2025-12-23 20:42:27.687554'),(7,'auth','0002_alter_permission_name_max_length','2025-12-23 20:42:27.749355'),(8,'auth','0003_alter_user_email_max_length','2025-12-23 20:42:27.853902'),(9,'auth','0004_alter_user_username_opts','2025-12-23 20:42:27.860902'),(10,'auth','0005_alter_user_last_login_null','2025-12-23 20:42:27.921462'),(11,'auth','0006_require_contenttypes_0002','2025-12-23 20:42:27.923460'),(12,'auth','0007_alter_validators_add_error_messages','2025-12-23 20:42:27.930465'),(13,'auth','0008_alter_user_username_max_length','2025-12-23 20:42:28.006226'),(14,'auth','0009_alter_user_last_name_max_length','2025-12-23 20:42:28.065661'),(15,'auth','0010_alter_group_name_max_length','2025-12-23 20:42:28.133815'),(16,'auth','0011_update_proxy_permissions','2025-12-23 20:42:28.133815'),(17,'auth','0012_alter_user_first_name_max_length','2025-12-23 20:42:28.199046'),(18,'sessions','0001_initial','2025-12-23 20:42:28.238982'),(19,'appQuali','0001_initial','2025-12-23 21:38:24.580917'),(20,'appQuali','0002_reclamacoes2_tecnologia_delete_reclamacoes','2025-12-24 04:15:29.163621'),(21,'appQuali','0003_reclamacoes','2025-12-25 15:07:24.402588'),(22,'appQuali','0004_reclamacoesarquivo','2025-12-26 04:26:45.372092'),(23,'appQuali','0005_rename_anexo_reclamacoesarquivo_image','2025-12-26 04:26:45.372092'),(24,'appQuali','0006_alter_reclamacoesarquivo_image','2025-12-26 04:27:39.379997'),(25,'appQuali','0002_tecnologia_reclamacoesarquivo','2025-12-26 04:34:35.982203'),(26,'appQuali','0002_tecnologia_arquivoreclamacoes','2025-12-26 05:24:15.269187'),(27,'appQuali','0002_tecnologia_documento','2025-12-26 23:51:36.955207'),(28,'appQuali','0002_tecnologia_itemarquivo','2025-12-27 05:47:22.485948'),(29,'appQuali','0002_tecnologia_item_alter_reclamacoes_table_and_more','2025-12-27 16:56:00.321802'),(30,'appQuali','0002_alter_reclamacoesarquivo_image','2025-12-27 18:10:49.784330'),(31,'appQuali','0003_rename_image_reclamacoesarquivo_item','2025-12-27 18:34:50.757768'),(32,'appQuali','0002_delete_reclamacoesarquivo','2025-12-27 18:42:31.964412'),(33,'appQuali','0002_rename_image_reclamacoesarquivo_itens_and_more','2025-12-28 03:53:47.536305'),(34,'appQuali','0003_alter_reclamacoesarquivo_itens','2025-12-28 20:00:53.159778'),(35,'appQuali','0004_alter_reclamacoesarquivo_itens','2026-01-05 04:47:41.212607'),(36,'appQuali','0005_semanano','2026-01-09 03:53:43.495865'),(37,'appQuali','0006_semanano_data_fim_semanano_data_inicio_and_more','2026-01-09 05:18:39.252925');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb3_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb3_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('0ebn6notgr0br0tprvywl0l2620ste21','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vxZFd:HESs_HbXXJxFpXGdt36C5S6I_u07pqdSB2nST3hT9jo','2026-03-17 23:34:05.324826'),('1cunsry01afa9ulopppfe3m13xht97dp','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vekfQ:74dADsusL0Mr_OQKdh8P4dBHX7c7lj7sVM-tPkrtOLk','2026-01-25 01:54:56.254269'),('dthkkypufcj9icottdrbdb7dnix8lgbw','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vbmZD:ab233Xgq46Lw2SQ1YJFrFjJikSs_0j9qlD_oCBM35Vs','2026-01-16 21:20:15.292582'),('fh55tmojoxm09fkmaf44z77skcl09est','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vY9Ge:V7WEf96NOKqOI0JIzeoSf1hCLdlAxo5i0dBF3mPUvf0','2026-01-06 20:46:04.291157'),('k11qdel5nk7je1ui3vbnt534xpakrelq','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vh8PR:Odxym9wT7DcWz-NyTXaNKZdxSpp0lNLx7LvRNiQOrWg','2026-01-31 15:40:17.041199'),('wkdqgx0o0l29an2mc8msjbbpa27k501v','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vcAcf:STxq6ZyCNRibqXIl7edwsdwjc40EiwmA2ftY4MY3WoU','2026-01-17 23:01:25.007839'),('wyw96po5ivvbkhjuvx935l42lf6l56za','.eJxVjMsOwiAQRf-FtSHAgAwu3fcbyAwMtmrapI-V8d-1SRe6veec-1KZtrXP2yJzHqq6KKtOvxtTeci4g3qn8TbpMo3rPLDeFX3QRXdTlef1cP8Oelr6b22SYLAYWnJILYH3yADMGM8WIpNjK82jbc1VWxIVAzFERAdJUhGj3h_I_zdb:1vYwnf:8YpVADNaO-tJp7SDLACne5iyF84aQHhmdMtPLpS_mZA','2026-01-09 01:39:27.299721');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empresa`
--

DROP TABLE IF EXISTS `empresa`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empresa` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa` varchar(12) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empresa`
--

LOCK TABLES `empresa` WRITE;
/*!40000 ALTER TABLE `empresa` DISABLE KEYS */;
INSERT INTO `empresa` VALUES (1,'Senhor Caixa'),(2,'Doutor Caixa');
/*!40000 ALTER TABLE `empresa` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produtos`
--

DROP TABLE IF EXISTS `produtos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produtos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `produto` varchar(26) COLLATE utf8mb3_unicode_ci NOT NULL,
  `data_inclusao` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data_atualiza` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produtos`
--

LOCK TABLES `produtos` WRITE;
/*!40000 ALTER TABLE `produtos` DISABLE KEYS */;
INSERT INTO `produtos` VALUES (1,'CAIXA DE BOLO','2025-12-26 01:51:46','2025-12-31 05:14:52'),(2,'CAIXA DE ESFIHA','2025-12-26 01:51:46','2025-12-31 05:14:52'),(3,'CAIXA DE PIZZA 25','2025-12-26 01:51:46','2025-12-31 05:14:52'),(4,'CAIXA DE PIZZA 30','2025-12-26 01:51:46','2025-12-31 05:14:52'),(5,'CAIXA DE PIZZA 35','2025-12-26 01:51:46','2025-12-31 05:14:52'),(6,'CAIXA DE PIZZA 40','2025-12-26 01:51:46','2025-12-31 05:14:52'),(7,'CAIXA DE PIZZA BROTO','2025-12-26 01:51:46','2025-12-31 05:14:52'),(8,'CAIXA DE VINHO','2025-12-26 01:51:46','2025-12-31 05:14:52'),(9,'FATIA DE PIZZA','2025-12-26 01:51:46','2025-12-31 05:14:52'),(10,'MALETA DE VINHO','2025-12-26 01:51:46','2025-12-31 05:14:52'),(11,'SANDUICHE DE PÃO POR METRO','2025-12-26 01:51:46','2025-12-31 05:14:52'),(12,'EMBALAGENS ESPECIAIS','2025-12-26 01:51:46','2025-12-31 05:14:52'),(13,'EMBALAGENS DE DOCES','2025-12-26 01:51:46','2025-12-31 05:14:52'),(14,'CAIXA DE TORTA','2025-12-31 04:32:47','2025-12-31 05:14:52'),(15,'Pizza Média 18','2026-01-06 03:32:43','2026-01-06 03:32:43'),(16,'Tapetinho 24,5 cm','2026-01-07 17:42:53','2026-01-07 17:42:53'),(17,'Tapetinho 34,5cm','2026-01-07 17:43:03','2026-01-07 17:43:03'),(18,'Tapetinho 39,5cm','2026-01-07 17:43:13','2026-01-07 17:43:13');
/*!40000 ALTER TABLE `produtos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reclamacoes`
--

DROP TABLE IF EXISTS `reclamacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reclamacoes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `data_reclam` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cliente` varchar(25) COLLATE utf8mb3_unicode_ci NOT NULL,
  `descricao` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `id_defeito` int NOT NULL,
  `vendedora` varchar(12) COLLATE utf8mb3_unicode_ci NOT NULL,
  `id_produto` int NOT NULL,
  `id_tecnol` int NOT NULL,
  `id_empresa` int NOT NULL,
  `comentarios` varchar(193) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `anexos` varchar(300) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `data_atualiza` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=169 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reclamacoes`
--

LOCK TABLES `reclamacoes` WRITE;
/*!40000 ALTER TABLE `reclamacoes` DISABLE KEYS */;
INSERT INTO `reclamacoes` VALUES (69,'2025-12-31 04:41:23','Didio Pizza Santa Cecilia','Embalagens fora de padrão/ruins',5,'Daniele',5,1,1,'É este mesmo cliente que mandei a reclamação na semana passada',NULL,'2026-01-08 03:17:05'),(70,'2025-12-31 04:43:27','Kobayashi\'s','impressão ruim e cheia de falhas',1,'Gabriella',1,1,1,'Aqui onde escreve o nome da pizza as vezes vem escuro e não dá pra escrever - 30/10/2025',NULL,'2025-12-31 04:43:27'),(71,'2025-12-31 04:46:49','Didio Pizza Santa Cecilia','impressão ruim e cheia de falhas',8,'Daniele',5,1,1,'letras borradas',NULL,'2026-01-08 03:17:05'),(72,'2025-12-31 04:48:16','Fundo JESUS PIZZA','Fundo da caixa amolecendo com o calor da pizza',1,'Paulo',5,1,1,NULL,NULL,'2025-12-31 04:48:16'),(73,'2025-12-31 04:50:39','Ice hot','caixas molhadas',5,'Gabriella',5,1,1,'Essas fotos são do primeiro fardo de caixas molhadas que vieram pra gente, molhadas mesmo, não é unida ...',NULL,'2025-12-31 04:50:39'),(74,'2025-12-31 04:53:03','PLANET PIZZA','Lacre não gruda as caixas broto e gigante vieram oleosas novamente',11,'Paulo',7,1,1,'desculpa pelo horário, mas só pra avisar que as caixas broto e gigante vieram oleosas novamente',NULL,'2025-12-31 04:53:03'),(75,'2025-12-31 04:54:38','Piazza NAVONA','22 fundos e 25 tampas',7,'Paulo',5,1,1,NULL,NULL,'2025-12-31 04:54:38'),(76,'2025-12-31 04:56:11','IFome','Caixa de outro cliente',12,'Paulo',5,1,1,'Caixa do IFome entregue no cliente Marsella',NULL,'2025-12-31 04:56:11'),(77,'2025-12-31 04:57:53','Conexao Pizza','impressões ficaram muito ruins, com diversas falhas, má qualidade',8,'Gabriella',1,1,1,'Os profissionais são vocês e o que vc mencionou,  não isenta responsabilidade de vocês,  não sei se terá outro pedido',NULL,'2026-01-08 03:18:09'),(79,'2025-12-31 05:01:59','Sabores do Chef','Umas caixas vem quebradas e a gente não consegue aproveitar',1,'Ana Beatriz',5,1,1,'Faltando uma parte das tampas. Foram cortadas equivocadamente durante a produção.',NULL,'2025-12-31 05:01:59'),(80,'2025-12-31 05:09:37','Sabores do Chef','Tampas chegaram no cliente cortadas e faltando uma parte',9,'Ana Beatriz',5,1,1,'Umas caixas vem quebradas e a gente não consegue aproveitar',NULL,'2025-12-31 05:09:37'),(81,'2025-12-31 05:11:47','Amarelos','Rasgamento ao dobrar para montagem',13,'Evlayne',5,1,1,'Xintiã. dá pra ver que é faca rotativa. Impressão e corte',NULL,'2025-12-31 05:11:47'),(82,'2025-12-31 05:14:00','Giacomos','Entrega incompleta',7,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 05:14:00'),(83,'2025-12-31 05:15:44','Filomena','impressão ruim e cheia de falhas',8,'Paulo',5,1,1,NULL,NULL,'2025-12-31 05:15:44'),(84,'2025-12-31 05:17:59','Raja Pizza','Rasgamento ao dobrar para montagem',13,'Gabriella',1,1,1,'cortes mais fundos do que devia,  caixa separa algumas abas de montagem',NULL,'2025-12-31 05:17:59'),(85,'2025-12-31 05:20:28','Mr Texas Aclimacao','Corte fora do esquadro',10,'Ana Beatriz',5,1,1,NULL,NULL,'2026-01-08 03:18:09'),(86,'2025-12-31 05:22:33','SPP Santo André','Rasgamento ao dobrar para montagem',13,'Daniele',1,1,1,'rasgamento ao dobrar',NULL,'2025-12-31 05:22:33'),(87,'2025-12-31 05:24:38','Raja Pizza','Rasgamento das abas ao dobrar para montagem',13,'Gabriella',4,1,1,'Todas as caixas, segundo o cliente',NULL,'2025-12-31 05:24:38'),(88,'2025-12-31 05:28:20','Cliente da Débora','embalagem empoeirada e rasgada. Entrega fora do horário combinado.',5,'Débora',5,1,1,NULL,NULL,'2025-12-31 05:28:20'),(89,'2025-12-31 05:30:25','Peperoni','Rasgamento ao dobrar para montagem',13,'Fernanda',5,1,1,NULL,NULL,'2025-12-31 05:30:25'),(90,'2025-12-31 05:34:09','LA CASA PIZZARIA','Caixas com defeito no material, na impressão e no corte/embalagem',13,'Gabriella',1,1,1,'relatou caixas com defeito no material, na impressão e no corte/embalagem',NULL,'2025-12-31 05:34:09'),(91,'2025-12-31 05:36:27','Cliente El Papi','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'vc me orientou a aumentar o meu pedido, fiz e mesmo assim nada das cxs chegarem.',NULL,'2025-12-31 05:36:27'),(92,'2025-12-31 05:37:24','BENDITA ESFIHA','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'FECHANDO A LOJA PORQUE NÃO TEM CAIXA PARA TRABALHAR [20:58, 12/11/2025] +55 11 99714-6438:',NULL,'2025-12-31 05:37:24'),(93,'2025-12-31 05:38:08','PLANET PIZZA SBC','Entrega incompleta',7,'Paulo',2,1,1,'RECLAMANDO QUE NÃO FOI UM ITEM QUE ESTAVA COBRANDO NA NOTA',NULL,'2025-12-31 05:38:08'),(94,'2025-12-31 05:41:40','Cliente da Gabriella','Caixas sem encaixe para travas',15,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 05:41:40'),(95,'2025-12-31 05:44:29','Umberto I','Avarias na embalagem Caixas amontoadas no caminhão -',2,'Gabriella',1,1,1,'Cliente está reclamando que o pedido dele foi por transportadora , e não foi transportado da maneira correta,',NULL,'2025-12-31 05:44:29'),(96,'2025-12-31 05:45:29','ARBOVILLE','Caixas avariadas',2,'Gabriella',5,1,1,'Cliente está reclamando que o pedido dele foi por transportadora , e não foi transportado da maneira correta, caixas chegaram com avarias  Alega que se continuar indo por transportadora não irá',NULL,'2025-12-31 05:45:29'),(97,'2025-12-31 05:47:02','Didio Pizza Santa Cecilia','Corte fora do esquadro e impressão com manchas',8,'Daniele',5,1,1,NULL,NULL,'2026-01-08 03:19:59'),(98,'2025-12-31 05:48:56','La Picolina','Baixa resistência do papelão',1,'Paulo',5,1,1,NULL,NULL,'2025-12-31 05:48:56'),(99,'2025-12-31 05:50:18','Pizza Cesar Mooca','Faltando fundos',7,'Daniele',5,1,1,NULL,NULL,'2025-12-31 05:50:18'),(100,'2025-12-31 05:52:44','PEQUENAS DELICIAS','Baixa resistência do papelão',1,'Ana Beatriz',1,1,1,'Caixas amolecem e amassam quando são colocadas uma sobre outra.',NULL,'2025-12-31 05:52:44'),(101,'2025-12-31 05:55:25','Pao da Vida','Tom da cor diferente, papel mais fraco, trava não cortada corretamente',8,'Ana Beatriz',5,1,1,'Além das reclamações sobre qualidade, questionou o preço.',NULL,'2026-01-08 03:18:09'),(102,'2025-12-31 05:57:06','Arabian','Cheiro de erva doce',3,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 05:57:06'),(103,'2025-12-31 05:59:21','Varanda Itália','Impressão fora de esquadro',10,'Ana Beatriz',1,1,1,'Marca ficou descentralizada em dois pacotes',NULL,'2025-12-31 05:59:21'),(104,'2025-12-31 06:01:13','Dona Toscana','Lacre fora de posição',11,'Paulo',6,3,1,NULL,NULL,'2026-01-07 02:43:12'),(105,'2025-12-31 06:02:38','Porto Pizzaria','Tampas chegaram no cliente cortadas e faltando uma parte',9,'Paulo',5,1,1,NULL,NULL,'2025-12-31 06:02:38'),(106,'2025-12-31 06:05:13','Rebeca','Falta de encaixe para uma das travas',15,'Paulo',5,1,1,'Dessa forma não trava a caixa.',NULL,'2025-12-31 06:05:13'),(107,'2025-12-31 06:06:36','360 PIZZA','Tampas com diâmetro maior que o especificado.',14,'Fernanda',5,1,1,NULL,NULL,'2025-12-31 06:06:36'),(108,'2025-12-31 06:08:55','LA CASA PIZZARIA FRUTAL','Caixas grudadas no pacote',2,'Gabriella',1,1,1,NULL,NULL,'2025-12-31 06:08:55'),(109,'2025-12-31 06:10:24','LA CASA PIZZARIA FRUTAL','Impressão com as tonalidades das cores variando',8,'Gabriella',5,1,1,'Cliente diz que está perdendo muitas caixas e falou que se continuar indo dessa forma irá devolver todo o pedido',NULL,'2025-12-31 06:10:24'),(110,'2025-12-31 06:11:13','LA CASA PIZZARIA FRUTAL','Embalagem danificada no transporte.',5,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 06:11:13'),(111,'2025-12-31 06:14:42','Didio Pizza Santa Cecilia','Baixa resistência do papelão',1,'Daniele',5,1,1,'Fundo amolecendo',NULL,'2026-01-08 03:19:59'),(112,'2025-12-31 06:16:18','Ponto Com','Receberam uma caixa de outro cliente (Forno à Lenha)',12,'Paulo',7,1,1,'Mandaram um pacote de broto de outra pizzaria para nós',NULL,'2025-12-31 06:16:18'),(113,'2025-12-31 06:18:48','Didio Pizza Santa Cecilia','Baixa resistência do papelão',1,'Daniele',5,1,1,'Reclamou que na reposição das caixas com baixa resistência, ainda voltaram caixas do lote anterior.',NULL,'2026-01-08 03:19:59'),(114,'2025-12-31 06:21:51','Arabian','Caixas com diferentes tonalidades, mais escuras e outras mais claras.',8,'Gabriella',5,1,1,'No áudio a cliente reporta que a caixa mais clara é também a menos resistente (mais fraca).',NULL,'2025-12-31 06:21:51'),(115,'2025-12-31 06:23:10','Pizza Cesar Guarulhos','impressão ruim e cheia de falhas',8,'Daniele',5,1,1,NULL,NULL,'2025-12-31 06:23:10'),(116,'2025-12-31 06:24:25','MARCO LUCCIO','Lacres não colam na caixa',11,'Carine',5,3,1,'Reclamando que os lacres não estão colando na caixa. A impressão aqui é DIGITAL',NULL,'2025-12-31 06:24:25'),(117,'2025-12-31 06:25:59','Don Rafaello - Cajamar','Trava fora de medida',15,'Daniele',5,1,1,NULL,NULL,'2025-12-31 06:25:59'),(118,'2025-12-31 06:27:45','DELIZIE DEI BISCOTTI','Impressão borrada.',8,'Gabriella',1,3,1,NULL,NULL,'2025-12-31 06:27:45'),(119,'2025-12-31 06:29:35','Didio Pizza Santa Cecilia','Caixas avariadas',1,'Daniele',5,1,1,NULL,NULL,'2026-01-08 03:19:59'),(120,'2025-12-31 06:31:02','Tre Duarte','Impressão com manchas',8,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 06:31:02'),(121,'2025-12-31 06:32:35','FAMIGLIA BONINO','Impressão desbotada e variando entre as caixas.',8,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 06:32:35'),(122,'2025-12-31 06:34:42','FAMIGLIA BONINO','Embalagem em formato diferente e danificada.',5,'Gabriella',5,1,1,'O cliente perguntou: \"O que faço com isso?\"',NULL,'2025-12-31 06:34:42'),(123,'2025-12-31 06:35:47','Osteria da casa','Impressão com manchas',8,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 06:35:47'),(124,'2025-12-31 06:38:23','VINCI','Embalagens rasgadas',5,'Neide',5,3,1,'Cliente questiona a qualidade do serviço da transportadora Marajá.',NULL,'2025-12-31 06:38:23'),(125,'2026-01-05 21:08:56','SALA VIP','A caixa da pizza estava extremamente mole.',1,'Daniele',1,1,1,'o entregador quando foi tirar da mochila a pizza quase virou e caiu toda no chão.',NULL,'2025-11-04 21:08:56'),(126,'2026-01-05 21:10:59','RAJA PIZZA','Rasgamento das abas ao dobrar para montagem',13,'Gabriella',5,1,1,'Todas as caixas, segundo o cliente',NULL,'2025-11-10 21:10:59'),(127,'2026-01-05 21:12:18','CLIENTE EL PAPI','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'Vc me orientou a aumentar o meu pedido, fiz e mesmo assim nada das cxs chegarem.',NULL,'2025-11-12 21:12:18'),(128,'2026-01-05 21:13:25','BENDITA ESFIHA','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'FECHANDO A LOJA PORQUE NÃO TEM CAIXA PARA TRABALHAR [20:58, 12/11/2025] +55 11 99714-6438:',NULL,'2025-11-12 21:13:25'),(129,'2026-01-05 21:14:34','PLANET PIZZA SBC','Entrega incompleta',7,'Paulo',5,1,1,'RECLAMANDO QUE NÃO FOI UM ITEM QUE ESTAVA COBRANDO NA NOTA',NULL,'2026-01-05 21:14:34'),(130,'2026-01-05 21:15:54','ARBOVILLE','Caixas avariadas',2,'Gabriella',5,1,1,'Cliente estão reclamando que o pedido dele foi por transportadora e não foi transportado da maneira correta, caixas chegaram',NULL,'2025-11-13 21:15:54'),(131,'2026-01-06 06:40:55','PIZZA CESAR ABC','Faltando parte dos fundos',7,'Daniele',15,1,1,'Pizza Cesar ABC, esta localizando umas faltas de fundos nos fardos.',NULL,'2026-01-06 03:42:45'),(132,'2026-01-06 06:47:24','PIZZA CESAR ABC','Pizza Grande 11 sem tampa',7,'Daniele',6,1,1,NULL,NULL,'2026-01-06 06:47:24'),(133,'2026-01-06 06:52:58','Pizza Soul','Cliente está reclamando da impressão (flexográfica)',8,'Gabriella',3,1,1,'Problemas em 2 pacotes',NULL,'2026-01-06 06:52:58'),(134,'2026-01-06 07:13:24','Pizzaria Palmeiras','Algumas embalagens sujas, empoeiradas',1,'Gabrielly',5,1,1,NULL,NULL,'2026-01-06 07:13:24'),(135,'2026-01-06 07:18:04','PEQUENAS DELICIAS','Embalagens molhadas',5,'Ana Beatriz',13,1,1,'Cliente se diz surpresa pois nunca tinha recebido embalagens com problemas',NULL,'2026-01-06 07:18:04'),(136,'2026-01-06 07:21:12','PIZZA CESAR ABC','Média 18 sem fundo',7,'Daniele',15,1,1,NULL,NULL,'2026-01-06 07:21:12'),(137,'2026-01-06 07:26:14','PIZZA CESAR ABC','Falatando tampas',7,'Daniele',6,1,1,NULL,NULL,'2026-01-06 07:26:14'),(138,'2026-01-06 07:33:39','PEQUENAS DELICIAS','Papelão para estar \"vindo mais fino\"',1,'Ana Beatriz',16,1,1,'A cliente que a caixa parecia \"desfazer\" ao fechar e que teve de jogar várias fora.',NULL,'2026-01-06 07:33:39'),(139,'2026-01-06 07:36:32','ROMANNA PIZZARIA','Embalagens molhadas',5,'Gabriella',1,2,2,'Caixa de pizza redonda',NULL,'2026-01-06 07:36:32'),(140,'2026-01-06 07:38:22','Didio Pizza Santa Cecilia','Caixa com verniz que não gruda o lacre',11,'Daniele',4,3,1,NULL,NULL,'2026-01-08 03:19:59');
/*!40000 ALTER TABLE `reclamacoes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reclamacoes_copia`
--

DROP TABLE IF EXISTS `reclamacoes_copia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reclamacoes_copia` (
  `id` int unsigned NOT NULL DEFAULT '0',
  `data_reclam` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `cliente` varchar(25) COLLATE utf8mb3_unicode_ci NOT NULL,
  `descricao` varchar(100) COLLATE utf8mb3_unicode_ci NOT NULL,
  `id_defeito` int NOT NULL,
  `vendedora` varchar(12) COLLATE utf8mb3_unicode_ci NOT NULL,
  `id_produto` int NOT NULL,
  `id_tecnol` int NOT NULL,
  `id_empresa` int NOT NULL,
  `comentarios` varchar(193) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `anexos` varchar(300) COLLATE utf8mb3_unicode_ci DEFAULT NULL,
  `data_atualiza` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reclamacoes_copia`
--

LOCK TABLES `reclamacoes_copia` WRITE;
/*!40000 ALTER TABLE `reclamacoes_copia` DISABLE KEYS */;
INSERT INTO `reclamacoes_copia` VALUES (69,'2025-12-31 04:41:23','Dídio Pizza Santa Cecília','Embalagens fora de padrão/ruins',5,'Daniele',5,1,1,'É este mesmo cliente que mandei a reclamação na semana passada',NULL,'2025-12-31 04:41:23'),(70,'2025-12-31 04:43:27','Kobayashi\'s','impressão ruim e cheia de falhas',1,'Gabriella',1,1,1,'Aqui onde escreve o nome da pizza as vezes vem escuro e não dá pra escrever - 30/10/2025',NULL,'2025-12-31 04:43:27'),(71,'2025-12-31 04:46:49','Dídio Pizza Santa Cecília','impressão ruim e cheia de falhas',8,'Daniele',5,1,1,'letras borradas',NULL,'2025-12-31 04:46:49'),(72,'2025-12-31 04:48:16','Fundo JESUS PIZZA','Fundo da caixa amolecendo com o calor da pizza',1,'Paulo',5,1,1,NULL,NULL,'2025-12-31 04:48:16'),(73,'2025-12-31 04:50:39','Ice hot','caixas molhadas',5,'Gabriella',5,1,1,'Essas fotos são do primeiro fardo de caixas molhadas que vieram pra gente, molhadas mesmo, não é unida ...',NULL,'2025-12-31 04:50:39'),(74,'2025-12-31 04:53:03','PLANET PIZZA','Lacre não gruda as caixas broto e gigante vieram oleosas novamente',11,'Paulo',7,1,1,'desculpa pelo horário, mas só pra avisar que as caixas broto e gigante vieram oleosas novamente',NULL,'2025-12-31 04:53:03'),(75,'2025-12-31 04:54:38','Piazza NAVONA','22 fundos e 25 tampas',7,'Paulo',5,1,1,NULL,NULL,'2025-12-31 04:54:38'),(76,'2025-12-31 04:56:11','IFome','Caixa de outro cliente',12,'Paulo',5,1,1,'Caixa do IFome entregue no cliente Marsella',NULL,'2025-12-31 04:56:11'),(77,'2025-12-31 04:57:53','Conexão Pizza','impressões ficaram muito ruins, com diversas falhas, má qualidade',8,'Gabriella',1,1,1,'Os profissionais são vocês e o que vc mencionou,  não isenta responsabilidade de vocês,  não sei se terá outro pedido',NULL,'2025-12-31 04:57:53'),(79,'2025-12-31 05:01:59','Sabores do Chef','Umas caixas vem quebradas e a gente não consegue aproveitar',1,'Ana Beatriz',5,1,1,'Faltando uma parte das tampas. Foram cortadas equivocadamente durante a produção.',NULL,'2025-12-31 05:01:59'),(80,'2025-12-31 05:09:37','Sabores do Chef','Tampas chegaram no cliente cortadas e faltando uma parte',9,'Ana Beatriz',5,1,1,'Umas caixas vem quebradas e a gente não consegue aproveitar',NULL,'2025-12-31 05:09:37'),(81,'2025-12-31 05:11:47','Amarelos','Rasgamento ao dobrar para montagem',13,'Evlayne',5,1,1,'Xintiã. dá pra ver que é faca rotativa. Impressão e corte',NULL,'2025-12-31 05:11:47'),(82,'2025-12-31 05:14:00','Giacomos','Entrega incompleta',7,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 05:14:00'),(83,'2025-12-31 05:15:44','Filomena','impressão ruim e cheia de falhas',8,'Paulo',5,1,1,NULL,NULL,'2025-12-31 05:15:44'),(84,'2025-12-31 05:17:59','Raja Pizza','Rasgamento ao dobrar para montagem',13,'Gabriella',1,1,1,'cortes mais fundos do que devia,  caixa separa algumas abas de montagem',NULL,'2025-12-31 05:17:59'),(85,'2025-12-31 05:20:28','Mr Texas Aclimação','Corte fora do esquadro',10,'Ana Beatriz',5,1,1,NULL,NULL,'2025-12-31 05:20:28'),(86,'2025-12-31 05:22:33','SPP Santo André','Rasgamento ao dobrar para montagem',13,'Daniele',1,1,1,'rasgamento ao dobrar',NULL,'2025-12-31 05:22:33'),(87,'2025-12-31 05:24:38','Raja Pizza','Rasgamento das abas ao dobrar para montagem',13,'Gabriella',4,1,1,'Todas as caixas, segundo o cliente',NULL,'2025-12-31 05:24:38'),(88,'2025-12-31 05:28:20','Cliente da Débora','embalagem empoeirada e rasgada. Entrega fora do horário combinado.',5,'Débora',5,1,1,NULL,NULL,'2025-12-31 05:28:20'),(89,'2025-12-31 05:30:25','Peperoni','Rasgamento ao dobrar para montagem',13,'Fernanda',5,1,1,NULL,NULL,'2025-12-31 05:30:25'),(90,'2025-12-31 05:34:09','LA CASA PIZZARIA','Caixas com defeito no material, na impressão e no corte/embalagem',13,'Gabriella',1,1,1,'relatou caixas com defeito no material, na impressão e no corte/embalagem',NULL,'2025-12-31 05:34:09'),(91,'2025-12-31 05:36:27','Cliente El Papi','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'vc me orientou a aumentar o meu pedido, fiz e mesmo assim nada das cxs chegarem.',NULL,'2025-12-31 05:36:27'),(92,'2025-12-31 05:37:24','BENDITA ESFIHA','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'FECHANDO A LOJA PORQUE NÃO TEM CAIXA PARA TRABALHAR [20:58, 12/11/2025] +55 11 99714-6438:',NULL,'2025-12-31 05:37:24'),(93,'2025-12-31 05:38:08','PLANET PIZZA SBC','Entrega incompleta',7,'Paulo',2,1,1,'RECLAMANDO QUE NÃO FOI UM ITEM QUE ESTAVA COBRANDO NA NOTA',NULL,'2025-12-31 05:38:08'),(94,'2025-12-31 05:41:40','Cliente da Gabriella','Caixas sem encaixe para travas',15,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 05:41:40'),(95,'2025-12-31 05:44:29','Umberto I','Avarias na embalagem Caixas amontoadas no caminhão -',2,'Gabriella',1,1,1,'Cliente está reclamando que o pedido dele foi por transportadora , e não foi transportado da maneira correta,',NULL,'2025-12-31 05:44:29'),(96,'2025-12-31 05:45:29','ARBOVILLE','Caixas avariadas',2,'Gabriella',5,1,1,'Cliente está reclamando que o pedido dele foi por transportadora , e não foi transportado da maneira correta, caixas chegaram com avarias  Alega que se continuar indo por transportadora não irá',NULL,'2025-12-31 05:45:29'),(97,'2025-12-31 05:47:02','Dídio Pizza Santa Cecília','Corte fora do esquadro e impressão com manchas',8,'Daniele',5,1,1,NULL,NULL,'2025-12-31 05:47:02'),(98,'2025-12-31 05:48:56','La Picolina','Baixa resistência do papelão',1,'Paulo',5,1,1,NULL,NULL,'2025-12-31 05:48:56'),(99,'2025-12-31 05:50:18','Pizza Cesar Mooca','Faltando fundos',7,'Daniele',5,1,1,NULL,NULL,'2025-12-31 05:50:18'),(100,'2025-12-31 05:52:44','PEQUENAS DELICIAS','Baixa resistência do papelão',1,'Ana Beatriz',1,1,1,'Caixas amolecem e amassam quando são colocadas uma sobre outra.',NULL,'2025-12-31 05:52:44'),(101,'2025-12-31 05:55:25','Pão da Vida','Tom da cor diferente, papel mais fraco, trava não cortada corretamente',8,'Ana Beatriz',5,1,1,'Além das reclamações sobre qualidade, questionou o preço.',NULL,'2025-12-31 05:55:25'),(102,'2025-12-31 05:57:06','Arabian','Cheiro de erva doce',3,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 05:57:06'),(103,'2025-12-31 05:59:21','Varanda Itália','Impressão fora de esquadro',10,'Ana Beatriz',1,1,1,'Marca ficou descentralizada em dois pacotes',NULL,'2025-12-31 05:59:21'),(104,'2025-12-31 06:01:13','Dona Toscana','Lacre fora de posição',11,'Paulo',6,1,1,NULL,NULL,'2025-12-31 06:01:13'),(105,'2025-12-31 06:02:38','Porto Pizzaria','Tampas chegaram no cliente cortadas e faltando uma parte',9,'Paulo',5,1,1,NULL,NULL,'2025-12-31 06:02:38'),(106,'2025-12-31 06:05:13','Rebeca','Falta de encaixe para uma das travas',15,'Paulo',5,1,1,'Dessa forma não trava a caixa.',NULL,'2025-12-31 06:05:13'),(107,'2025-12-31 06:06:36','360 PIZZA','Tampas com diâmetro maior que o especificado.',14,'Fernanda',5,1,1,NULL,NULL,'2025-12-31 06:06:36'),(108,'2025-12-31 06:08:55','LA CASA PIZZARIA FRUTAL','Caixas grudadas no pacote',2,'Gabriella',1,1,1,NULL,NULL,'2025-12-31 06:08:55'),(109,'2025-12-31 06:10:24','LA CASA PIZZARIA FRUTAL','Impressão com as tonalidades das cores variando',8,'Gabriella',5,1,1,'Cliente diz que está perdendo muitas caixas e falou que se continuar indo dessa forma irá devolver todo o pedido',NULL,'2025-12-31 06:10:24'),(110,'2025-12-31 06:11:13','LA CASA PIZZARIA FRUTAL','Embalagem danificada no transporte.',5,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 06:11:13'),(111,'2025-12-31 06:14:42','Dídio Pizza Santa Cecília','Baixa resistência do papelão',1,'Daniele',5,1,1,'Fundo amolecendo',NULL,'2025-12-31 06:14:42'),(112,'2025-12-31 06:16:18','Ponto Com','Receberam uma caixa de outro cliente (Forno à Lenha)',12,'Paulo',7,1,1,'Mandaram um pacote de broto de outra pizzaria para nós',NULL,'2025-12-31 06:16:18'),(113,'2025-12-31 06:18:48','Dídio Pizza Santa Cecília','Baixa resistência do papelão',1,'Daniele',5,1,1,'Reclamou que na reposição das caixas com baixa resistência, ainda voltaram caixas do lote anterior.',NULL,'2025-12-31 06:18:48'),(114,'2025-12-31 06:21:51','Arabian','Caixas com diferentes tonalidades, mais escuras e outras mais claras.',8,'Gabriella',5,1,1,'No áudio a cliente reporta que a caixa mais clara é também a menos resistente (mais fraca).',NULL,'2025-12-31 06:21:51'),(115,'2025-12-31 06:23:10','Pizza Cesar Guarulhos','impressão ruim e cheia de falhas',8,'Daniele',5,1,1,NULL,NULL,'2025-12-31 06:23:10'),(116,'2025-12-31 06:24:25','MARCO LUCCIO','Lacres não colam na caixa',11,'Carine',5,3,1,'Reclamando que os lacres não estão colando na caixa. A impressão aqui é DIGITAL',NULL,'2025-12-31 06:24:25'),(117,'2025-12-31 06:25:59','Don Rafaello - Cajamar','Trava fora de medida',15,'Daniele',5,1,1,NULL,NULL,'2025-12-31 06:25:59'),(118,'2025-12-31 06:27:45','DELIZIE DEI BISCOTTI','Impressão borrada.',8,'Gabriella',1,3,1,NULL,NULL,'2025-12-31 06:27:45'),(119,'2025-12-31 06:29:35','Dídio Pizza Santa Cecília','Caixas avariadas',1,'Daniele',5,1,1,NULL,NULL,'2025-12-31 06:29:35'),(120,'2025-12-31 06:31:02','Tre Duarte','Impressão com manchas',8,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 06:31:02'),(121,'2025-12-31 06:32:35','FAMIGLIA BONINO','Impressão desbotada e variando entre as caixas.',8,'Gabriella',5,1,1,NULL,NULL,'2025-12-31 06:32:35'),(122,'2025-12-31 06:34:42','FAMIGLIA BONINO','Embalagem em formato diferente e danificada.',5,'Gabriella',5,1,1,'O cliente perguntou: \"O que faço com isso?\"',NULL,'2025-12-31 06:34:42'),(123,'2025-12-31 06:35:47','Osteria da casa','Impressão com manchas',8,'Evlayne',5,1,1,NULL,NULL,'2025-12-31 06:35:47'),(124,'2025-12-31 06:38:23','VINCI','Embalagens rasgadas',5,'Neide',5,3,1,'Cliente questiona a qualidade do serviço da transportadora Marajá.',NULL,'2025-12-31 06:38:23'),(125,'2026-01-05 21:08:56','SALA VIP','A caixa da pizza estava extremamente mole.',1,'Daniele',1,1,1,'o entregador quando foi tirar da mochila a pizza quase virou e caiu toda no chão.',NULL,'2025-11-04 21:08:56'),(126,'2026-01-05 21:10:59','RAJA PIZZA','Rasgamento das abas ao dobrar para montagem',13,'Gabriella',5,1,1,'Todas as caixas, segundo o cliente',NULL,'2025-11-10 21:10:59'),(127,'2026-01-05 21:12:18','CLIENTE EL PAPI','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'Vc me orientou a aumentar o meu pedido, fiz e mesmo assim nada das cxs chegarem.',NULL,'2025-11-12 21:12:18'),(128,'2026-01-05 21:13:25','BENDITA ESFIHA','Falta de embalagens para trabalhar.',6,'Paulo',2,1,1,'FECHANDO A LOJA PORQUE NÃO TEM CAIXA PARA TRABALHAR [20:58, 12/11/2025] +55 11 99714-6438:',NULL,'2025-11-12 21:13:25'),(129,'2026-01-05 21:14:34','PLANET PIZZA SBC','Entrega incompleta',7,'Paulo',5,1,1,'RECLAMANDO QUE NÃO FOI UM ITEM QUE ESTAVA COBRANDO NA NOTA',NULL,'2026-01-05 21:14:34'),(130,'2026-01-05 21:15:54','ARBOVILLE','Caixas avariadas',2,'Gabriella',5,1,1,'Cliente estão reclamando que o pedido dele foi por transportadora e não foi transportado da maneira correta, caixas chegaram',NULL,'2025-11-13 21:15:54'),(131,'2026-01-06 06:40:55','PIZZA CESAR ABC','Faltando parte dos fundos',7,'Daniele',15,1,1,'Pizza Cesar ABC, esta localizando umas faltas de fundos nos fardos.',NULL,'2026-01-06 03:42:45'),(132,'2026-01-06 06:47:24','PIZZA CESAR ABC','Pizza Grande 11 sem tampa',7,'Daniele',6,1,1,NULL,NULL,'2026-01-06 06:47:24'),(133,'2026-01-06 06:52:58','Pizza Soul','Cliente está reclamando da impressão (flexográfica)',8,'Gabriella',3,1,1,'Problemas em 2 pacotes',NULL,'2026-01-06 06:52:58'),(134,'2026-01-06 07:13:24','Pizzaria Palmeiras','Algumas embalagens sujas, empoeiradas',1,'Gabrielly',5,1,1,NULL,NULL,'2026-01-06 07:13:24'),(135,'2026-01-06 07:18:04','PEQUENAS DELICIAS','Embalagens molhadas',5,'Ana Beatriz',13,1,1,'Cliente se diz surpresa pois nunca tinha recebido embalagens com problemas',NULL,'2026-01-06 07:18:04'),(136,'2026-01-06 07:21:12','PIZZA CESAR ABC','Média 18 sem fundo',7,'Daniele',15,1,1,NULL,NULL,'2026-01-06 07:21:12'),(137,'2026-01-06 07:26:14','PIZZA CESAR ABC','Falatando tampas',7,'Daniele',6,1,1,NULL,NULL,'2026-01-06 07:26:14'),(138,'2026-01-06 07:33:39','PEQUENAS DELICIAS','Papelão para estar \"vindo mais fino\"',1,'Ana Beatriz',16,1,1,'A cliente que a caixa parecia \"desfazer\" ao fechar e que teve de jogar várias fora.',NULL,'2026-01-06 07:33:39'),(139,'2026-01-06 07:36:32','ROMANNA PIZZARIA','Embalagens molhadas',5,'Gabriella',1,2,2,'Caixa de pizza redonda',NULL,'2026-01-06 07:36:32'),(140,'2026-01-06 07:38:22','Didio Pizza Santa Cecilia','Caixa com verniz que não gruda o lacre',11,'Daniele',4,1,1,NULL,NULL,'2026-01-06 07:38:22');
/*!40000 ALTER TABLE `reclamacoes_copia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tecnologia`
--

DROP TABLE IF EXISTS `tecnologia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tecnologia` (
  `id` int NOT NULL,
  `tecnologia` varchar(30) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tecnologia`
--

LOCK TABLES `tecnologia` WRITE;
/*!40000 ALTER TABLE `tecnologia` DISABLE KEYS */;
INSERT INTO `tecnologia` VALUES (1,'Flexografia'),(2,'Offset'),(3,'Flexocromia W1'),(4,'Flexocromia W2');
/*!40000 ALTER TABLE `tecnologia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipos_defeitos`
--

DROP TABLE IF EXISTS `tipos_defeitos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipos_defeitos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo_defeito` varchar(49) COLLATE utf8mb3_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipos_defeitos`
--

LOCK TABLES `tipos_defeitos` WRITE;
/*!40000 ALTER TABLE `tipos_defeitos` DISABLE KEYS */;
INSERT INTO `tipos_defeitos` VALUES (1,'baixa resistência do papelão'),(2,'caixa avariada'),(3,'cheiro na embalagem'),(4,'desfolhamento do papelão'),(5,'embalagem com defeito'),(6,'entrega atrasada'),(7,'entrega incompleta'),(8,'impressão borrões / tons / falhas'),(9,'falta parte da tampa'),(10,'impressão fora de centro_esquadro'),(11,'lacre não cola _ fora de posição'),(12,'mistura de produtos'),(13,'rasgamento na dobra'),(14,'tampa redonda fora de medida'),(15,'trava ausente ou não encaixa');
/*!40000 ALTER TABLE `tipos_defeitos` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-31 20:29:46
