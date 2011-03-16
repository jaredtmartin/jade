-- MySQL dump 10.13  Distrib 5.1.49, for debian-linux-gnu (i686)
--
-- Host: localhost    Database: jade
-- ------------------------------------------------------
-- Server version	5.1.49-1ubuntu8.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `auth_group_permissions_425ae3c4` (`group_id`),
  KEY `auth_group_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `auth_message_403f60f` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_message`
--

LOCK TABLES `auth_message` WRITE;
/*!40000 ALTER TABLE `auth_message` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=267 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add permission',1,'add_permission'),(2,'Can change permission',1,'change_permission'),(3,'Can delete permission',1,'delete_permission'),(4,'Can add group',2,'add_group'),(5,'Can change group',2,'change_group'),(6,'Can delete group',2,'delete_group'),(7,'Can add user',3,'add_user'),(8,'Can change user',3,'change_user'),(9,'Can delete user',3,'delete_user'),(10,'Can add message',4,'add_message'),(11,'Can change message',4,'change_message'),(12,'Can delete message',4,'delete_message'),(13,'Can add content type',5,'add_contenttype'),(14,'Can change content type',5,'change_contenttype'),(15,'Can delete content type',5,'delete_contenttype'),(16,'Can add session',6,'add_session'),(17,'Can change session',6,'change_session'),(18,'Can delete session',6,'delete_session'),(19,'Can add site',7,'add_site'),(20,'Can change site',7,'change_site'),(21,'Can delete site',7,'delete_site'),(22,'Can add log entry',8,'add_logentry'),(23,'Can change log entry',8,'change_logentry'),(24,'Can delete log entry',8,'delete_logentry'),(25,'Can add tab',9,'add_tab'),(26,'Can change tab',9,'change_tab'),(27,'Can delete tab',9,'delete_tab'),(28,'Can add setting',10,'add_setting'),(29,'Can change setting',10,'change_setting'),(30,'Can delete setting',10,'delete_setting'),(34,'Can add report',12,'add_report'),(35,'Can change report',12,'change_report'),(36,'Can delete report',12,'delete_report'),(37,'Can add unit',13,'add_unit'),(38,'Can change unit',13,'change_unit'),(39,'Can delete unit',13,'delete_unit'),(40,'Can add category',14,'add_category'),(41,'Can change category',14,'change_category'),(42,'Can delete category',14,'delete_category'),(43,'Can add item',15,'add_item'),(44,'Can change item',15,'change_item'),(45,'Can delete item',15,'delete_item'),(46,'Can view costs',15,'view_cost'),(47,'Can view items',15,'view_item'),(48,'Can add service',15,'add_service'),(49,'Can change service',15,'change_service'),(50,'Can delete service',15,'delete_service'),(51,'Can view services',15,'view_service'),(52,'Can add linked item',16,'add_linkeditem'),(53,'Can change linked item',16,'change_linkeditem'),(54,'Can delete linked item',16,'delete_linkeditem'),(55,'Can add price group',17,'add_pricegroup'),(56,'Can change price group',17,'change_pricegroup'),(57,'Can delete price group',17,'delete_pricegroup'),(58,'Can add price',18,'add_price'),(59,'Can change price',18,'change_price'),(60,'Can delete price',18,'delete_price'),(61,'Can add account',19,'add_account'),(62,'Can change account',19,'change_account'),(63,'Can delete account',19,'delete_account'),(64,'Can view accounts',19,'view_account'),(65,'Can add tax rate',20,'add_taxrate'),(66,'Can change tax rate',20,'change_taxrate'),(67,'Can delete tax rate',20,'delete_taxrate'),(68,'Can add account group',21,'add_accountgroup'),(69,'Can change account group',21,'change_accountgroup'),(70,'Can delete account group',21,'delete_accountgroup'),(71,'Can add contact',22,'add_contact'),(72,'Can change contact',22,'change_contact'),(73,'Can delete contact',22,'delete_contact'),(74,'Can add client',19,'add_client'),(75,'Can change client',19,'change_client'),(76,'Can delete client',19,'delete_client'),(77,'Can view clients',19,'view_client'),(78,'Can add vendor',19,'add_vendor'),(79,'Can change vendor',19,'change_vendor'),(80,'Can delete vendor',19,'delete_vendor'),(81,'Can view vendors',19,'view_vendor'),(82,'Can add garantee offer',23,'add_garanteeoffer'),(83,'Can change garantee offer',23,'change_garanteeoffer'),(84,'Can delete garantee offer',23,'delete_garanteeoffer'),(85,'Can add user profile',24,'add_userprofile'),(86,'Can change user profile',24,'change_userprofile'),(87,'Can delete user profile',24,'delete_userprofile'),(88,'Can add transaction',25,'add_transaction'),(89,'Can change transaction',25,'change_transaction'),(90,'Can delete transaction',25,'delete_transaction'),(91,'Can view transactions',25,'view_transaction'),(206,'Can add client payment',37,'add_clientpayment'),(205,'Can view clients',29,'view_client'),(204,'Can delete client',29,'delete_client'),(203,'Can change client',29,'change_client'),(202,'Can add client',29,'add_client'),(99,'Can add sale',25,'add_sale'),(100,'Can change sale',25,'change_sale'),(101,'Can delete sale',25,'delete_sale'),(102,'Can view sales',25,'view_sale'),(103,'Can view sales',25,'view_receipt'),(104,'Can add sale return',25,'add_salereturn'),(105,'Can change sale return',25,'change_salereturn'),(106,'Can delete sale return',25,'delete_salereturn'),(107,'Can add purchase',25,'add_purchase'),(108,'Can change purchase',25,'change_purchase'),(109,'Can delete purchase',25,'delete_purchase'),(110,'Can view purchases',25,'view_purchase'),(111,'Can add purchase return',25,'add_purchasereturn'),(112,'Can change purchase return',25,'change_purchasereturn'),(113,'Can delete purchase return',25,'delete_purchasereturn'),(114,'Can add cash closing',25,'add_cashclosing'),(115,'Can change cash closing',25,'change_cashclosing'),(116,'Can delete cash closing',25,'delete_cashclosing'),(117,'Can view cash_closings',25,'view_cash_closing'),(118,'Can add payment',25,'add_payment'),(119,'Can change payment',25,'change_payment'),(120,'Can delete payment',25,'delete_payment'),(121,'Can add client payment',25,'add_clientpayment'),(122,'Can change client payment',25,'change_clientpayment'),(123,'Can delete client payment',25,'delete_clientpayment'),(124,'Can add client refund',25,'add_clientrefund'),(125,'Can change client refund',25,'change_clientrefund'),(126,'Can delete client refund',25,'delete_clientrefund'),(127,'Can add vendor payment',25,'add_vendorpayment'),(128,'Can change vendor payment',25,'change_vendorpayment'),(129,'Can delete vendor payment',25,'delete_vendorpayment'),(130,'Can add vendor refund',25,'add_vendorrefund'),(131,'Can change vendor refund',25,'change_vendorrefund'),(132,'Can delete vendor refund',25,'delete_vendorrefund'),(133,'Can add sale tax',25,'add_saletax'),(134,'Can change sale tax',25,'change_saletax'),(135,'Can delete sale tax',25,'delete_saletax'),(136,'Can add purchase tax',25,'add_purchasetax'),(137,'Can change purchase tax',25,'change_purchasetax'),(138,'Can delete purchase tax',25,'delete_purchasetax'),(139,'Can add discount',25,'add_discount'),(140,'Can change discount',25,'change_discount'),(141,'Can delete discount',25,'delete_discount'),(142,'Can add sale discount',25,'add_salediscount'),(143,'Can change sale discount',25,'change_salediscount'),(144,'Can delete sale discount',25,'delete_salediscount'),(145,'Can add purchase discount',25,'add_purchasediscount'),(146,'Can change purchase discount',25,'change_purchasediscount'),(147,'Can delete purchase discount',25,'delete_purchasediscount'),(148,'Can add garantee',25,'add_garantee'),(149,'Can change garantee',25,'change_garantee'),(150,'Can delete garantee',25,'delete_garantee'),(151,'Can add client garantee',25,'add_clientgarantee'),(152,'Can change client garantee',25,'change_clientgarantee'),(153,'Can delete client garantee',25,'delete_clientgarantee'),(154,'Can add vendor garantee',25,'add_vendorgarantee'),(155,'Can change vendor garantee',25,'change_vendorgarantee'),(156,'Can delete vendor garantee',25,'delete_vendorgarantee'),(157,'Can add equity',25,'add_equity'),(158,'Can change equity',25,'change_equity'),(159,'Can delete equity',25,'delete_equity'),(160,'Can add count',25,'add_count'),(161,'Can change count',25,'change_count'),(162,'Can delete count',25,'delete_count'),(163,'Can view counts',25,'view_count'),(164,'Can post counts',25,'post_count'),(165,'Can post counts as sales',25,'post_count_sale'),(166,'Can add transfer',25,'add_transfer'),(167,'Can change transfer',25,'change_transfer'),(168,'Can delete transfer',25,'delete_transfer'),(169,'Can view transfers',25,'view_transfer'),(170,'Can view sites',25,'view_site'),(171,'Can add production',25,'add_production'),(172,'Can change production',25,'change_production'),(173,'Can delete production',25,'delete_production'),(174,'Can view productions',25,'view_production'),(175,'Can add process',25,'add_process'),(176,'Can change process',25,'change_process'),(177,'Can delete process',25,'delete_process'),(178,'Can view processes',25,'view_process'),(179,'Can add job',25,'add_job'),(180,'Can change job',25,'change_job'),(181,'Can delete job',25,'delete_job'),(182,'Can start production',25,'start_production'),(183,'Can finish production',25,'finish_production'),(184,'Can view jobs',25,'view_job'),(185,'Can add updates run',55,'add_updatesrun'),(186,'Can change updates run',55,'change_updatesrun'),(187,'Can delete updates run',55,'delete_updatesrun'),(191,'Can add sale',31,'add_sale'),(192,'Can change sale',31,'change_sale'),(193,'Can delete sale',31,'delete_sale'),(194,'Can view sales',31,'view_sale'),(195,'Can view sales',31,'view_receipt'),(196,'Can add sale return',32,'add_salereturn'),(197,'Can change sale return',32,'change_salereturn'),(198,'Can delete sale return',32,'delete_salereturn'),(207,'Can change client payment',37,'change_clientpayment'),(208,'Can delete client payment',37,'delete_clientpayment'),(209,'Can add client refund',38,'add_clientrefund'),(210,'Can change client refund',38,'change_clientrefund'),(211,'Can delete client refund',38,'delete_clientrefund'),(212,'Can add vendor payment',39,'add_vendorpayment'),(213,'Can change vendor payment',39,'change_vendorpayment'),(214,'Can delete vendor payment',39,'delete_vendorpayment'),(215,'Can add vendor refund',40,'add_vendorrefund'),(216,'Can change vendor refund',40,'change_vendorrefund'),(217,'Can delete vendor refund',40,'delete_vendorrefund'),(218,'Can add vendor',30,'add_vendor'),(219,'Can change vendor',30,'change_vendor'),(220,'Can delete vendor',30,'delete_vendor'),(221,'Can view vendors',30,'view_vendor'),(222,'Can add purchase',33,'add_purchase'),(223,'Can change purchase',33,'change_purchase'),(224,'Can delete purchase',33,'delete_purchase'),(225,'Can view purchases',33,'view_purchase'),(226,'Can add purchase return',34,'add_purchasereturn'),(227,'Can change purchase return',34,'change_purchasereturn'),(228,'Can delete purchase return',34,'delete_purchasereturn'),(229,'Can add equity',49,'add_equity'),(230,'Can change equity',49,'change_equity'),(231,'Can delete equity',49,'delete_equity'),(251,'Can add purchase tax',42,'add_purchasetax'),(250,'Can delete sale tax',41,'delete_saletax'),(248,'Can add sale tax',41,'add_saletax'),(249,'Can change sale tax',41,'change_saletax'),(255,'Can change extra value',64,'change_extravalue'),(254,'Can add extra value',64,'add_extravalue'),(253,'Can delete purchase tax',42,'delete_purchasetax'),(252,'Can change purchase tax',42,'change_purchasetax'),(256,'Can delete extra value',64,'delete_extravalue'),(260,'Can add transaction tipo',67,'add_transactiontipo'),(261,'Can change transaction tipo',67,'change_transactiontipo'),(262,'Can delete transaction tipo',67,'delete_transactiontipo'),(263,'Can add entry',68,'add_entry'),(264,'Can change entry',68,'change_entry'),(265,'Can delete entry',68,'delete_entry'),(266,'Can view entries',68,'view_entry');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'jared','','','asd@asd.asd','sha1$0cb51$d1b52dc3b9490ec7a205082980fcf0bda3ffbef2',1,1,1,'2011-01-11 22:23:19','2010-12-20 18:07:04'),(2,'tester','','','','sha1$33128$b383a16ba08e2a064f4c62c8dbcfbc4eddbf6bdc',1,1,1,'2010-12-29 08:43:42','2010-12-29 08:27:25'),(3,'limited','','','','sha1$a37d1$b6678f45c202ff8cabc8ae6f5e11de613378bd1f',0,1,0,'2010-12-29 08:27:48','2010-12-29 08:27:48');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `auth_user_groups_403f60f` (`user_id`),
  KEY `auth_user_groups_425ae3c4` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_403f60f` (`user_id`),
  KEY `auth_user_user_permissions_1e014c8f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
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
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_403f60f` (`user_id`),
  KEY `django_admin_log_1bb8f392` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2010-12-24 11:49:01',1,12,'1','Factura de Consumidor Final',2,'Changed body.'),(2,'2010-12-24 19:20:46',1,12,'13','Cotizacion',1,''),(3,'2010-12-24 19:22:52',1,10,'50','Last automatic barcode',3,''),(4,'2010-12-29 08:12:55',1,10,'42','Date format',2,'Changed _value.'),(5,'2010-12-29 08:27:25',1,3,'2','tester',1,''),(6,'2010-12-29 08:27:36',1,3,'2','tester',2,'Changed is_staff and is_superuser.'),(7,'2010-12-29 08:27:48',1,3,'3','limited',1,''),(8,'2010-12-29 09:08:09',1,22,'3','Big Daddy',1,''),(9,'2010-12-29 12:33:49',1,12,'1','Factura de Consumidor Final',2,'Changed body.'),(10,'2010-12-29 12:43:05',1,12,'1','Factura de Consumidor Final',2,'Changed body.'),(11,'2010-12-31 11:42:55',1,10,'42','Date format',2,'Modificado/a _value.'),(17,'2010-12-31 12:15:40',1,10,'42','Date format',2,'Modificado/a _value.'),(18,'2010-12-31 12:29:20',1,20,'3','Retencion Consumidor Final',2,'Modificado/a value y price_includes_tax.'),(19,'2010-12-31 13:35:44',1,20,'4','Retencion Credito Fiscal',2,'Changed value and price_includes_tax.'),(20,'2010-12-31 22:01:51',1,19,'7','Proveedores',2,'Changed multiplier.'),(22,'2011-01-04 09:43:54',1,9,'4','Production',2,'Modificado/a url.');
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=70 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'permission','auth','permission'),(2,'group','auth','group'),(3,'user','auth','user'),(4,'message','auth','message'),(5,'content type','contenttypes','contenttype'),(6,'session','sessions','session'),(7,'site','sites','site'),(8,'log entry','admin','logentry'),(9,'tab','inventory','tab'),(10,'setting','inventory','setting'),(12,'report','inventory','report'),(13,'unit','inventory','unit'),(14,'category','inventory','category'),(15,'item','inventory','item'),(16,'linked item','inventory','linkeditem'),(17,'price group','inventory','pricegroup'),(18,'price','inventory','price'),(19,'account','inventory','account'),(20,'tax rate','inventory','taxrate'),(21,'account group','inventory','accountgroup'),(22,'contact','inventory','contact'),(23,'garantee offer','inventory','garanteeoffer'),(24,'user profile','inventory','userprofile'),(25,'transaction','inventory','transaction'),(69,'payment','inventory','payment'),(64,'extra value','inventory','extravalue'),(28,'service','inventory','service'),(29,'client','inventory','client'),(30,'vendor','inventory','vendor'),(31,'sale','inventory','sale'),(32,'sale return','inventory','salereturn'),(33,'purchase','inventory','purchase'),(34,'purchase return','inventory','purchasereturn'),(35,'cash closing','inventory','cashclosing'),(67,'transaction tipo','inventory','transactiontipo'),(37,'client payment','inventory','clientpayment'),(38,'client refund','inventory','clientrefund'),(39,'vendor payment','inventory','vendorpayment'),(40,'vendor refund','inventory','vendorrefund'),(41,'sale tax','inventory','saletax'),(42,'purchase tax','inventory','purchasetax'),(43,'discount','inventory','discount'),(44,'sale discount','inventory','salediscount'),(45,'purchase discount','inventory','purchasediscount'),(46,'garantee','inventory','garantee'),(47,'client garantee','inventory','clientgarantee'),(48,'vendor garantee','inventory','vendorgarantee'),(49,'equity','inventory','equity'),(50,'count','inventory','count'),(51,'transfer','inventory','transfer'),(52,'production','production','production'),(53,'process','production','process'),(54,'job','production','job'),(55,'updates run','updates','updatesrun'),(68,'entry','inventory','entry');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('375a8728acbfbd6ca8fc63183e5b119c','gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigECdS4xMmExNDM2NGM4MjY5N2U3MzJl\nZmIzM2UxMmY5OGFlZA==\n','2011-01-12 08:43:42'),('1a210faff0150a89decb729bd7796fed','gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigEBdS43N2IyNjExZjE3MDg1Yjc3Nzk1\nYmI5MjBmZjVjYWIwNA==\n','2011-01-13 15:30:40'),('a826bbbc4b0cc2028b57cbb6036cf674','gAJ9cQEoVQ1fYXV0aF91c2VyX2lkcQKKAQFVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28u\nY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQ9kamFuZ29fbGFuZ3VhZ2VxBVgC\nAAAAZXNxBnUuYjEwNzI2MDk1NjY0YzFmMGYyMGQ4MDAwZTY4NGQwOGQ=\n','2011-01-21 11:45:40'),('50146d1e92624e34e8b16c4592df7675','gAJ9cQEoVRJfYXV0aF91c2VyX2JhY2tlbmRxAlUpZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5k\ncy5Nb2RlbEJhY2tlbmRxA1UNX2F1dGhfdXNlcl9pZHEEigEBdS43N2IyNjExZjE3MDg1Yjc3Nzk1\nYmI5MjBmZjVjYWIwNA==\n','2011-01-25 22:23:19'),('9ae5b14f48075ddb25dc6ee5a9e41485','gAJ9cQEoVQ1fYXV0aF91c2VyX2lkcQKKAQFVEl9hdXRoX3VzZXJfYmFja2VuZHEDVSlkamFuZ28u\nY29udHJpYi5hdXRoLmJhY2tlbmRzLk1vZGVsQmFja2VuZHEEVQ9kamFuZ29fbGFuZ3VhZ2VxBVgC\nAAAAZXNxBnUuYjEwNzI2MDk1NjY0YzFmMGYyMGQ4MDAwZTY4NGQwOGQ=\n','2011-01-18 09:44:13');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
INSERT INTO `django_site` VALUES (1,'example.com','example.com');
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_account`
--

DROP TABLE IF EXISTS `inventory_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `number` varchar(32) NOT NULL,
  `multiplier` int(11) NOT NULL,
  `tipo` varchar(16) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_account_6223029` (`site_id`)
) ENGINE=MyISAM AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_account`
--

LOCK TABLES `inventory_account` WRITE;
/*!40000 ALTER TABLE `inventory_account` DISABLE KEYS */;
INSERT INTO `inventory_account` VALUES (1,'Activos','01',1,'Account',1),(2,'Efectivo','0101',1,'Account',1),(3,'Inventario','0102',1,'Account',1),(4,'Banco','0103',1,'Account',1),(5,'Clientes','0104',1,'Account',1),(6,'Pasivos','02',-1,'Account',1),(7,'Proveedores','0201',-1,'Account',1),(9,'Impuestos','0202',-1,'Account',1),(10,'Impuestos de Ventas','020201',-1,'Account',1),(11,'Impuestos de Ventas de Consumidor Final','02020101',-1,'Account',1),(25,'Impuestos de Ventas de Credito Fiscal','02020102',-1,'Account',1),(27,'Retencion de Ventas de Consumidor Final','02020103',-1,'Account',1),(28,'Retencion de Ventas de Credito Fiscal','02020104',-1,'Account',1),(12,'Impuestos de Compras','020202',-1,'Account',1),(13,'Impuestos de Compras de Consumidor Final','02020201',-1,'Account',1),(26,'Impuestos de Compras de Credito Fiscal','02020202',-1,'Account',1),(14,'Patrocinio','03',-1,'Account',1),(15,'Ingresos','04',-1,'Account',1),(16,'Ingresos de Consumidor Final','0401',-1,'Account',1),(17,'Ventas de Consumidor Final','040101',-1,'Account',1),(18,'Descuentos de Consumidor Final','040102',1,'Account',1),(19,'Devoluciones de Consumidor Final','040103',1,'Account',1),(29,'Ingresos de Credito Fiscal','0402',-1,'Account',1),(30,'Ventas de Credito Fiscal','040201',-1,'Account',1),(31,'Descuentos de Credito Fiscal','040202',1,'Account',1),(32,'Devoluciones de Credito Fiscal','040203',1,'Account',1),(20,'Gastos','05',1,'Account',1),(21,'Gastos de Inventario','0501',1,'Account',1),(22,'Gastos de Cuentas Fisicas','0502',1,'Account',1),(23,'Gastos de Transferencias','0503',1,'Account',1),(24,'Gastos de Produccion','0504',1,'Account',1),(8,'No Especificado','020101',1,'Vendor',1),(33,'Anonimo','0104001',1,'Client',1);
/*!40000 ALTER TABLE `inventory_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_accountgroup`
--

DROP TABLE IF EXISTS `inventory_accountgroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_accountgroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `revenue_account_id` int(11) NOT NULL,
  `discounts_account_id` int(11) NOT NULL,
  `returns_account_id` int(11) NOT NULL,
  `default_tax_rate_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_accountgroup_62e27613` (`revenue_account_id`),
  KEY `inventory_accountgroup_7a849693` (`discounts_account_id`),
  KEY `inventory_accountgroup_219920aa` (`returns_account_id`),
  KEY `inventory_accountgroup_46cff5c2` (`default_tax_rate_id`),
  KEY `inventory_accountgroup_6223029` (`site_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_accountgroup`
--

LOCK TABLES `inventory_accountgroup` WRITE;
/*!40000 ALTER TABLE `inventory_accountgroup` DISABLE KEYS */;
INSERT INTO `inventory_accountgroup` VALUES (1,'Consumidor Final',17,18,19,1,1),(2,'Credito Fiscal',30,31,32,2,1);
/*!40000 ALTER TABLE `inventory_accountgroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_category`
--

DROP TABLE IF EXISTS `inventory_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_category`
--

LOCK TABLES `inventory_category` WRITE;
/*!40000 ALTER TABLE `inventory_category` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_client`
--

DROP TABLE IF EXISTS `inventory_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_client` (
  `contact_ptr_id` int(11) NOT NULL,
  `receipt_id` int(11) NOT NULL,
  PRIMARY KEY (`contact_ptr_id`),
  KEY `inventory_client_78ec3aab` (`receipt_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_client`
--

LOCK TABLES `inventory_client` WRITE;
/*!40000 ALTER TABLE `inventory_client` DISABLE KEYS */;
INSERT INTO `inventory_client` VALUES (33,1);
/*!40000 ALTER TABLE `inventory_client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_clientpayment`
--

DROP TABLE IF EXISTS `inventory_clientpayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_clientpayment` (
  `transaction_ptr_id` int(11) NOT NULL,
  UNIQUE KEY `transaction_ptr_id` (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_clientpayment`
--

LOCK TABLES `inventory_clientpayment` WRITE;
/*!40000 ALTER TABLE `inventory_clientpayment` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_clientpayment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_clientrefund`
--

DROP TABLE IF EXISTS `inventory_clientrefund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_clientrefund` (
  `transaction_ptr_id` int(11) NOT NULL,
  UNIQUE KEY `transaction_ptr_id` (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_clientrefund`
--

LOCK TABLES `inventory_clientrefund` WRITE;
/*!40000 ALTER TABLE `inventory_clientrefund` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_clientrefund` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_contact`
--

DROP TABLE IF EXISTS `inventory_contact`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_contact` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tax_group_name` varchar(32) NOT NULL,
  `price_group_id` int(11) NOT NULL,
  `receipt_id` int(11) NOT NULL,
  `account_group_id` int(11) NOT NULL,
  `address` varchar(32) NOT NULL,
  `state_name` varchar(32) NOT NULL,
  `country` varchar(32) NOT NULL,
  `home_phone` varchar(32) NOT NULL,
  `cell_phone` varchar(32) NOT NULL,
  `work_phone` varchar(32) NOT NULL,
  `fax` varchar(32) NOT NULL,
  `tax_number` varchar(32) NOT NULL,
  `description` longtext NOT NULL,
  `email` varchar(32) NOT NULL,
  `registration` varchar(32) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `account_id` int(11) NOT NULL,
  `credit_days` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `account_id` (`account_id`),
  KEY `inventory_contact_2f5f464c` (`price_group_id`),
  KEY `inventory_contact_78ec3aab` (`receipt_id`),
  KEY `inventory_contact_56358a24` (`account_group_id`),
  KEY `inventory_contact_403f60f` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_contact`
--

LOCK TABLES `inventory_contact` WRITE;
/*!40000 ALTER TABLE `inventory_contact` DISABLE KEYS */;
INSERT INTO `inventory_contact` VALUES (1,'',1,1,1,'','','','','','','','','','','',NULL,8,30),(2,'',1,1,1,'','','','','','','','','','','',NULL,33,30);
/*!40000 ALTER TABLE `inventory_contact` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_cost`
--

DROP TABLE IF EXISTS `inventory_cost`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_cost` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_cost`
--

LOCK TABLES `inventory_cost` WRITE;
/*!40000 ALTER TABLE `inventory_cost` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_cost` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_document`
--

DROP TABLE IF EXISTS `inventory_document`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_document` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `number` varchar(32) NOT NULL,
  `date` datetime NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_document_6223029` (`site_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_document`
--

LOCK TABLES `inventory_document` WRITE;
/*!40000 ALTER TABLE `inventory_document` DISABLE KEYS */;
INSERT INTO `inventory_document` VALUES (1,'1001','2011-01-11 22:04:57',1),(2,'C10001','2011-01-12 00:12:09',1),(3,'C10002','2011-01-12 00:12:09',1),(4,'C10003','2011-01-12 00:29:16',1);
/*!40000 ALTER TABLE `inventory_document` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_entry`
--

DROP TABLE IF EXISTS `inventory_entry`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_entry` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `transaction_id` int(11) NOT NULL,
  `value` decimal(8,2) NOT NULL,
  `account_id` int(11) NOT NULL,
  `delivered` tinyint(1) NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  `item_id` int(11) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `tipo` varchar(16) NOT NULL,
  `serial` varchar(32) DEFAULT NULL,
  `date` datetime NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_entry_45d19ab3` (`transaction_id`),
  KEY `inventory_entry_6f2fe10e` (`account_id`),
  KEY `inventory_entry_67b70d25` (`item_id`),
  KEY `inventory_entry_6223029` (`site_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_entry`
--

LOCK TABLES `inventory_entry` WRITE;
/*!40000 ALTER TABLE `inventory_entry` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_entry` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_equity`
--

DROP TABLE IF EXISTS `inventory_equity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_equity` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_equity`
--

LOCK TABLES `inventory_equity` WRITE;
/*!40000 ALTER TABLE `inventory_equity` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_equity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_extravalue`
--

DROP TABLE IF EXISTS `inventory_extravalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_extravalue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `value` decimal(8,2) DEFAULT NULL,
  `transaction_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_extravalue_45d19ab3` (`transaction_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_extravalue`
--

LOCK TABLES `inventory_extravalue` WRITE;
/*!40000 ALTER TABLE `inventory_extravalue` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_extravalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_garanteeoffer`
--

DROP TABLE IF EXISTS `inventory_garanteeoffer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_garanteeoffer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `months` int(11) NOT NULL,
  `price` decimal(8,2) NOT NULL,
  `item_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_garanteeoffer_67b70d25` (`item_id`),
  KEY `inventory_garanteeoffer_6223029` (`site_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_garanteeoffer`
--

LOCK TABLES `inventory_garanteeoffer` WRITE;
/*!40000 ALTER TABLE `inventory_garanteeoffer` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_garanteeoffer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_item`
--

DROP TABLE IF EXISTS `inventory_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `bar_code` varchar(64) NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  `minimum` decimal(8,2) NOT NULL,
  `maximum` decimal(8,2) NOT NULL,
  `default_cost` decimal(8,2) NOT NULL,
  `location` varchar(32) NOT NULL,
  `description` varchar(1024) NOT NULL,
  `unit_id` int(11) NOT NULL,
  `auto_bar_code` tinyint(1) NOT NULL,
  `tipo` varchar(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `inventory_item_cac2c6` (`unit_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_item`
--

LOCK TABLES `inventory_item` WRITE;
/*!40000 ALTER TABLE `inventory_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_linkeditem`
--

DROP TABLE IF EXISTS `inventory_linkeditem`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_linkeditem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent_id` int(11) NOT NULL,
  `child_id` int(11) NOT NULL,
  `quantity` decimal(8,2) NOT NULL,
  `fixed` decimal(8,2) NOT NULL,
  `relative` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_linkeditem_63f17a16` (`parent_id`),
  KEY `inventory_linkeditem_259e5c21` (`child_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_linkeditem`
--

LOCK TABLES `inventory_linkeditem` WRITE;
/*!40000 ALTER TABLE `inventory_linkeditem` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_linkeditem` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_price`
--

DROP TABLE IF EXISTS `inventory_price`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_price` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `item_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  `fixed_discount` decimal(8,2) NOT NULL,
  `relative_discount` decimal(8,2) NOT NULL,
  `fixed` decimal(8,2) NOT NULL,
  `relative` decimal(8,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_price_425ae3c4` (`group_id`),
  KEY `inventory_price_67b70d25` (`item_id`),
  KEY `inventory_price_6223029` (`site_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_price`
--

LOCK TABLES `inventory_price` WRITE;
/*!40000 ALTER TABLE `inventory_price` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_price` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_pricegroup`
--

DROP TABLE IF EXISTS `inventory_pricegroup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_pricegroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_pricegroup`
--

LOCK TABLES `inventory_pricegroup` WRITE;
/*!40000 ALTER TABLE `inventory_pricegroup` DISABLE KEYS */;
INSERT INTO `inventory_pricegroup` VALUES (1,'Public'),(2,'Mayoreo');
/*!40000 ALTER TABLE `inventory_pricegroup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_purchase`
--

DROP TABLE IF EXISTS `inventory_purchase`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_purchase` (
  `transaction_ptr_id` int(11) NOT NULL,
  `calculated_cost` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_purchase`
--

LOCK TABLES `inventory_purchase` WRITE;
/*!40000 ALTER TABLE `inventory_purchase` DISABLE KEYS */;
INSERT INTO `inventory_purchase` VALUES (8,NULL);
/*!40000 ALTER TABLE `inventory_purchase` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_purchasereturn`
--

DROP TABLE IF EXISTS `inventory_purchasereturn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_purchasereturn` (
  `purchase_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`purchase_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_purchasereturn`
--

LOCK TABLES `inventory_purchasereturn` WRITE;
/*!40000 ALTER TABLE `inventory_purchasereturn` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_purchasereturn` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_purchasetax`
--

DROP TABLE IF EXISTS `inventory_purchasetax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_purchasetax` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_purchasetax`
--

LOCK TABLES `inventory_purchasetax` WRITE;
/*!40000 ALTER TABLE `inventory_purchasetax` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_purchasetax` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_report`
--

DROP TABLE IF EXISTS `inventory_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `body` longtext NOT NULL,
  `image` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_report`
--

LOCK TABLES `inventory_report` WRITE;
/*!40000 ALTER TABLE `inventory_report` DISABLE KEYS */;
INSERT INTO `inventory_report` VALUES (1,'Factura de Consumidor Final','<!--# Jade Inventory Control System-->\r\n<!--#Copyright (C) 2010  Jared T. Martin-->\r\n\r\n<!--#    This program is free software: you can redistribute it and/or modify-->\r\n<!--#    it under the terms of the GNU General Public License as published by-->\r\n<!--#    the Free Software Foundation, either version 3 of the License, or-->\r\n<!--#    (at your option) any later version.-->\r\n\r\n<!--#    This program is distributed in the hope that it will be useful,-->\r\n<!--#    but WITHOUT ANY WARRANTY; without even the implied account of-->\r\n<!--#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the-->\r\n<!--#    GNU General Public License for more details.-->\r\n\r\n<!--#    You should have received a copy of the GNU General Public License-->\r\n<!--#    along with this program.  If not, see <http://www.gnu.org/licenses/>.-->\r\n{% load tags %}\r\n<html>\r\n<style>\r\n    body{line-height:16px;}\r\n    td.numero {text-align:left;}\r\n    td.texto {text-align:left;}\r\n    table {border:solid;height:200px;}\r\n@page {\r\n    size:letter;\r\n  {% if watermark_filename %}\r\nbackground-image: url({{watermark_filename}});\r\n{% endif %}\r\n  top: 3.2cm;\r\n  left: 1.7cm;\r\n      @frame header{\r\n        top:3.4cm;\r\n        height: 1.3cm;\r\n        left: 3.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: headerContent;\r\n      }\r\n      @frame table{\r\n        top:5.3cm;\r\n        height: 5.8cm;\r\n        left: 1.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: tableContent;\r\n      }\r\n      @frame totals{\r\n        top:11cm;\r\n        height: 2.3cm;\r\n        left: 2.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: totalsContent;\r\n      }\r\n  right: 1.7cm;\r\n  }\r\n</style>\r\n<body>\r\n    <table id=\"headerContent\">\r\n        <tr>\r\n            <td style=\"width:11.5cm;\">{{doc.client.name}}</td>\r\n            <td>{{doc.date|date:\"m/d/Y\"}}</td>\r\n        </tr>\r\n        <tr><td colspan=\"2\">{{doc.client.address}}</td></tr>\r\n        <tr>\r\n            <td>{{doc.client.tax_number}}</td>\r\n            <td>{{doc.form_of_payment}}</td>\r\n        </tr>\r\n    </table>\r\n    <table id=\"tableContent\">\r\n         {% for sale in doc.lines %}\r\n            {% if sale.tipo == \'SaleDiscount\' %}\r\n              <tr><td/><td> Descuento</td><td/><td/><td/><td>(${{sale.value|floatformat:2}})</td></tr>\r\n            {% else %}\r\n            <tr>\r\n                <td class=\"numero\" style=\"width:68px;\">{{sale.quantity|floatformat:-2}}</td>\r\n                <td class=\"texto\" style=\"width:387px;\">{{sale.item.name}}</td>\r\n                <td class=\"numero\" style=\"width:58px;\">${{sale.unit_value|floatformat:2}}</td>\r\n                <td class=\"numero\" style=\"width:47px;\"> </td>\r\n                <td class=\"numero\" style=\"width:47px;\"> </td>\r\n                <td class=\"numero\">${{sale.value|floatformat:2}}</td>\r\n            </tr>\r\n           {% endif %}\r\n        {%endfor%}\r\n    </table>\r\n    <table id=\"totalsContent\">\r\n        <tr>\r\n            <td style=\"width:15.2cm;\">{{doc.total|money2word}}</td>\r\n            <td>${{doc.subtotal|floatformat:2}}</td>\r\n        </tr>\r\n        <tr>\r\n            <td></td>\r\n            <td>${{ doc|tax:\'Impuestos de Ventas de Consumidor Final\' }}</td>\r\n        </tr>\r\n        <tr>\r\n            <td></td>\r\n            <td>${{ doc|tax:\'Percepcion\' }}</td>\r\n        </tr>\r\n<tr/>\r\n        <tr>\r\n            <td></td>\r\n            <td>${{ doc.total|floatformat:2 }}</td>\r\n        </tr>\r\n\r\n    </table>\r\n</body>','uploaded_images/receipt1.jpg'),(6,'Factura de Credito Fiscal','<html>\r\n<style>\r\n    body{line-height:16px;}\r\n    td.numero {text-align:left;}\r\n    td.texto {text-align:left;}\r\n    table {border:solid;height:200px;}\r\n@page {\r\n    size:letter;\r\n  {% if watermark_filename %}\r\nbackground-image: url({{watermark_filename}});\r\n{% endif %}\r\n  top: 3.2cm;\r\n  left: 1.7cm;\r\n      @frame header{\r\n        top:3.4cm;\r\n        height: 1.3cm;\r\n        left: 3.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: headerContent;\r\n      }\r\n      @frame table{\r\n        top:5.3cm;\r\n        height: 5.8cm;\r\n        left: 1.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: tableContent;\r\n      }\r\n      @frame totals{\r\n        top:11cm;\r\n        height: 2.3cm;\r\n        left: 2.7cm;\r\n        right: 1.7cm;\r\n        -pdf-frame-content: totalsContent;\r\n      }\r\n  right: 1.7cm;\r\n  }\r\n</style>\r\n<body>\r\n    <table id=\"headerContent\">\r\n        <tr>\r\n            <td style=\"width:11.5cm;\">{{doc.0.client.name}}</td>\r\n            <td>{{doc.0.date|date:\"m/d/Y\"}}</td>\r\n        </tr>\r\n        <tr><td colspan=\"2\">{{doc.0.client.address}}</td></tr>\r\n        <tr>\r\n            <td>{{doc.0.client.tax_number}}</td>\r\n            <td>{{doc.0.form_of_payment}}</td>\r\n        </tr>\r\n    </table>\r\n    <table id=\"tableContent\">\r\n         {% for sale in doc %}\r\n            <tr>\r\n                <td class=\"numero\" style=\"width:68px;\">{{sale.quantity|floatformat:-2}}</td>\r\n                <td class=\"texto\" style=\"width:387px;\">{{sale.item.name}}</td>\r\n                <td class=\"numero\" style=\"width:58px;\">${{sale.unit_charge|floatformat:2}}</td>\r\n                <td class=\"numero\" style=\"width:47px;\"> </td>\r\n                <td class=\"numero\" style=\"width:47px;\"> </td>\r\n                <td class=\"numero\">${{sale.charge|floatformat:2}}</td>\r\n            </tr>\r\n        {%endfor%}\r\n    </table>\r\n    <table id=\"totalsContent\">\r\n        <tr>\r\n            <td style=\"width:15.2cm;\">${{charge|floatformat:2}}</td>\r\n            <td>${{charge|floatformat:2}}</td>\r\n        </tr>\r\n        <tr>\r\n            <td></td>\r\n            <td>${{charge|floatformat:2}}</td>\r\n        </tr>\r\n        <tr/><tr/>\r\n        <tr>\r\n            <td></td>\r\n            <td>${{charge|floatformat:2}}</td>\r\n        </tr>\r\n\r\n    </table>\r\n</body>',''),(7,'Hoja de Precios','<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\r\n<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Lista de Precios</h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th>Nombre</th><th>Description</th><th>Precio</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for object in items %}\r\n                    <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td class=\"texto\">{{object.name}}</td><td class=\"texto\">{{object.description}}</td><td class=\"numero\">${{object.price|default:0|floatformat:2}}</td></tr>\r\n                    \r\n                {%endfor%}\r\n            </tbody>\r\n            \r\n        </table>\r\n    </body>\r\n</html>',''),(8,'Reporte de Inventario','<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">\r\n<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Lista de Inventario</h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th>Nombre</th><th>Locacion</th><th>Cantidad</th><th>Unidad</th><th>Costo</th><th>Total</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for object in items %}\r\n                     <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td>{{object.name}}</td><td>{{object.location}}</td><td>{{object.stock}}</td><td>{{object.unit}}</td><td>${{object.cost|default:0|floatformat:2}}</td><td>${{object.total_cost|default:0|floatformat:2}}</td></tr>                    \r\n                {%endfor%}\r\n            </tbody>            \r\n        </table>\r\n    </body>\r\n</html>',''),(12,'Reporte de Baja Inventario','<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                text-align:center;\r\n                padding-top:20px;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            .company_name {\r\n                height: 20px;\r\n                font-size:20px;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n                @frame pagenum {\r\n                  -pdf-frame-content: pagenum;\r\n                  bottom: 2cm;\r\n                  right: 1cm;\r\n                  height: .5cm;\r\n                }\r\n                @frame printdate {\r\n                  -pdf-frame-content: printdate;\r\n                  bottom: 2cm; \r\n                  left:1cm;\r\n                  height: .5cm;\r\n                }\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>\r\n            <span class=\"company_name\">{{company_name}}</span><br>\r\n            Lista de Inventario Baja\r\n        </h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th>Nombre</th><th>Locacion</th><th>Unidad</th><th>Min</th><th>Max</th><th>Surgerido</th><th>Inventario</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for object in items %}\r\n                     <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td>{{object.name}}</td><td>{{object.location}}</td><td>{{object.unit}}</td><td>{{object.minimum}}</td><td>{{object.maximum}}</td><td>{{object.recommended}}</td><td>{{object.stock}}</td></tr>                    \r\n                {%endfor%}\r\n<tr class=\"{% cycle \"row1\" \"row2\" %}\"><th>Total de productos: {{count}}</th></tr>   \r\n\r\n<tr class=\"{% cycle \"row1\" \"row2\" %}\"><th>Total</th><th></th><th>{{total_stock}}</th><th></th><th>${{total_cost|default:0|floatformat:2}}</th><th>${{total_total_cost|default:0|floatformat:2}}</th></tr>  \r\n            </tbody>            \r\n        </table>\r\n    <div id=\"printdate\" style=\"text-align:left;\">{{date_printed|date:\"d/m/Y\"}}</div>\r\n    <div id=\"pagenum\" style=\"text-align:right;\"> <pdf:pagenumber> </div>\r\n\r\n\r\n    </body>\r\n</html>',''),(9,'Hoja de Cuentas Fisicas','{% load tags %}\r\n<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Cuenta Fisica {{doc.0.doc_number}}</h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th>Producto</th><th>Locacion</th><th>Unidad</th><th>Costo</th><th>Actual</th><th>Cuenta</th><th>Valor de Diferencia</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for count in doc %}\r\n                    <tr class=\"{% cycle \"row1\" \"row2\" %}\">\r\n                        <td class=\"texto\" style=\"width:50%;\">{{count.item.name}}</td>\r\n                        <td class=\"texto\" >{{count.item.location}}</td>\r\n                        <td class=\"texto\" >{{count.item.unit}}</td>\r\n                        <td class=\"numero\" >{{count.item.unit_cost}}</td>\r\n                        <td class=\"numero\" >${{count.count|minus:count.item.stock|mult:count.unit_cost|floatformat:2}}</td>\r\n                        <td class=\"numero\" >{{count.item.stock|floatformat:-2}}</td>\r\n                        <td class=\"numero\" >{% if count.count %}{{count.count|floatformat:-2}}{% else %}__________{% endif %}</td>\r\n                    </tr>\r\n                {%endfor%}\r\n            </tbody>\r\n            \r\n        </table>\r\n    </body>\r\n</html>',''),(10,'Corte de Caja','{% load tags %}\r\n<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            h2 {\r\n                padding-left:10px;\r\n                font-size:16px;\r\n            }\r\n            h3 {\r\n                padding-left:20px;\r\n                font-size:14px;\r\n            }\r\n            h4 {\r\n                padding-left:30px;\r\n                font-size:12px;\r\n            }\r\n            th{text-align:left;}\r\n            .toprow{  \r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            .row1{  \r\n                padding-top:3px;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                padding-top:3px;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            .bottomrow{\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;border-width:2px;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Corte de Caja {{start|date:\"m/d/Y\"}}{% if end != start %}-{{ end|date:\"m/d/Y\" }}{% endif %}</h1>\r\n<h2>Ventas:</h2>\r\n{% if groups_by_series %}\r\n        <h3>Ventas canceladas inmediatamente:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for group in groups_by_series %}\r\n            <tr class=\"toprow\"><td class=\"texto\"><b>{{group.0.0.client.account_group.name}}</b></td><td/><td/></tr>\r\n                {% for series in group %}\r\n                    {% if series.first == series.last %}\r\n                        <tr class=\"{% cycle \'row1\' \'row2\' as rowcolors %}\r\n\"><td/><td class=\"texto\">{{series.first}}</td><td class=\"numero\">${{series.value|floatformat:2}}</td></tr>\r\n                    {% else %}\r\n                        <tr class=\"{% cycle \'row1\' \'row2\' as rowcolors %}\r\n\"><td/><td class=\"texto\">{{series.first}} - {{series.last}}</td><td class=\"numero\">${{series.value|floatformat:2}}</td></tr>\r\n                    {% endif %}\r\n                {% endfor %}\r\n              <tr class=\"bottomrow {% cycle rowcolors %}\"><td /><td class=\"texto\"><b>Total</b></td><td class=\"numero\"><b>{% total_value group %}</b></td></tr>\r\n          {%endfor %}\r\n<tr class=\"bottomrow\"{% cycle rowcolors %}><td class=\"texto\"><b>Total:</b></td><td /><td class=\"numero\"><b>{% total_value paid_sales %}</b>\r\n        </tbody></table>\r\n{% endif %}\r\n{% if unpaid_sales %}\r\n        <h3>Ventas a credito:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for doc in unpaid_sales %}\r\n             <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td/><td class=\"numero\">{{doc.doc_number}}</td><td class=\"texto\">{{doc.client.name}}</td><td class=\"numero\"> ${{doc.value|floatformat:2}}</td></tr>\r\n          {% endfor %}\r\n          <tr class=\"bottomrow\"><td /><td class=\"texto\"><b>Total</b></td><td/><td class=\"numero\"><b>{% total_value unpaid_sales %}</b></td></tr>\r\n        </tbody></table>\r\n{% endif %}\r\n<h4>Total de todas las Ventas: ${{revenue|floatformat:2}} {% if discount %} Descuentos: ${{discount|floatformat:2}} Total: ${{totalrevenue|floatformat:2}} {% endif %}</h4>\r\n<hr>\r\n{% if grouped_payments.Late %}\r\n        <h3>Pagos a credito:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for payment in grouped_payments.Late %}\r\n             <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td/><td class=\"numero\">{{payment.doc_number}}</td><td class=\"texto\">{{payment.account.name}}</td><td class=\"numero\"> ${{payment.value|floatformat:2}}</td></tr>\r\n          {% endfor %}\r\n          <tr class=\"bottomrow\"><td /><td class=\"texto\"><b>Total</b></td><td/><td class=\"numero\"><b>{% total_value grouped_payments.Late %}</b></td></tr>\r\n        </tbody></table>\r\n<hr>\r\n{% endif %}\r\n{% if grouped_payments.Down %}\r\n        <h3>Abonos a cuenta:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for payment in grouped_payments.Down %}\r\n             <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td/><td class=\"numero\">{{payment.doc_number}}</td><td class=\"texto\">{{payment.account.name}}</td><td class=\"numero\"> ${{payment.value|floatformat:2}}</td></tr>\r\n          {% endfor %}\r\n          <tr class=\"bottomrow\"><td /><td class=\"texto\"><b>Total</b></td><td/><td class=\"numero\"><b>{% total_value grouped_payments.Down %}</b></td></tr>\r\n        </tbody></table>\r\n<hr>\r\n{% endif %}\r\n\r\n{% if grouped_payments.Early %}\r\n        <h3>Anicipos:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for payment in grouped_payments.Early %}\r\n             <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td/><td class=\"numero\">{{payment.doc_number}}</td><td class=\"texto\">{{payment.account.name}}</td><td class=\"numero\"> ${{payment.value|floatformat:2}}</td></tr>\r\n          {% endfor %}\r\n          <tr class=\"bottomrow\"><td /><td class=\"texto\"><b>Total</b></td><td/><td class=\"numero\"><b>{% total_value grouped_payments.Early %}</b></td></tr>\r\n        </tbody></table>\r\n<hr>\r\n{% endif %}\r\n{% if grouped_payments.Over %}\r\n        <h3>Excedente de pago:</h3>\r\n        <table id=\"tableContent\"><tbody>\r\n          {% for payment in grouped_payments.Over %}\r\n             <tr class=\"{% cycle \"row1\" \"row2\" %}\"><td/><td class=\"numero\">{{payment.doc_number}}</td><td class=\"texto\">{{payment.account.name}}</td><td class=\"numero\"> ${{payment.value|floatformat:2}}</td></tr>\r\n          {% endfor %}\r\n          <tr class=\"bottomrow\"><td /><td class=\"texto\"><b>Total</b></td><td/><td class=\"numero\"><b>{% total_value grouped_payments.Over %}</b></td></tr>\r\n        </tbody></table>\r\n<hr>\r\n{% endif %}\r\n<h2>Resumen:</h2>\r\n<table id=\"cashContent\"><tbody>\r\n    <tr class=\"row1\">\r\n        <td class=\"texto\">Efectivo al inicio del dia:</td><td>${{initial_cash|floatformat:2}}</td>\r\n        <td class=\"texto\">Ingresos:</td><td>${{revenue|floatformat:2}}</td>\r\n    </tr>\r\n    <tr class=\"row2\">\r\n        <td class=\"texto\">Total de Pagos Recibidos</td><td>${{paymentstotal|floatformat:2}}</td>\r\n        <td class=\"texto\">Descuentos:</td><td>(${{discount|floatformat:2}})</td>\r\n    </tr>\r\n    <tr class=\"row1\">\r\n        <td class=\"texto\">Total de Corte:</td><td>(${{paymentstotal|floatformat:2}})</td>\r\n        <td class=\"texto\">Impuestos:</td><td>${{tax|floatformat:2}}</td>\r\n    </tr>\r\n    <tr class=\"row2\">\r\n        <td class=\"texto\">Efectivo al fin del dia:</td><td>(${{final_cash|floatformat:2}})</td>\r\n       <td class=\"texto\">Gastos:</td><td>(${{expense|floatformat:2}})</td>\r\n    </tr>\r\n    <tr class=\"row1\">\r\n        <th class=\"texto\">Suma:</th><th>${{cash_check|floatformat:2}}</th>\r\n      <td class=\"texto\">Ganacia:</td><td>(${{earnings|floatformat:2}})</td>\r\n    </tr>\r\n    <tr class=\"row2\">\r\n        <td class=\"texto\"></td><td></td>\r\n        <th class=\"texto\">Suma:</th><th>${{revenue_check|floatformat:2}}</th>\r\n    </tr>\r\n</tbody><table>\r\n    </body>\r\n</html>',''),(11,'Estado de Cuentas','<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Estado de Cuentas para {{account.name}}</h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th>Fecha</th><th>Tipo</th><th>Producto</th><th>Cantidad</th><th>Valor</th><th>Saldo</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for entry in entries %}\r\n                    <tr class=\"{% cycle \"row1\" \"row2\" %}\">\r\n                        <td class=\"texto\" >{{entry.date}}</td>\r\n                        <td class=\"texto\" >{{entry.transaction.tipo}}</td>\r\n                        <td class=\"texto\" >{{entry.item.name}}</td>\r\n                        <td class=\"numero\" >{{entry.quantity|floatformat:-2}}</td>\r\n                        <td class=\"numero\" >${{entry.value|floatformat:2}}</td>\r\n                        <td class=\"numero\" >${{entry.total|floatformat:2}}</td>\r\n                    </tr>\r\n                {%endfor%}\r\n            </tbody>\r\n            \r\n        </table>\r\n    </body>\r\n</html>',''),(13,'Cotizacion','{% load tags %}\r\n<html>\r\n    <head>\r\n        <title></title>\r\n        <meta http-equiv=\"Content-Type\" content=\"text/html;charset=ISO-8859-1\" >\r\n        <meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\" >\r\n        <meta http-equiv=\"Content-Style-Type\" content=\"text/css\" >\r\n        <style type=\"text/css\">\r\n            h1 {\r\n                height: 60px;\r\n                min-width: 960px;\r\n                background: #e4f2fd;\r\n                border-bottom: 1px solid #c6d9e9;\r\n                font-family:Georgia,Times,\"Times New Roman\",serif;\r\n                font-weight:normal;\r\n                color:#555555;\r\n                font-size:36px;\r\n                line-height:1em;\r\n                min-width:500px;\r\n                padding-top:34px;\r\n                text-align:center;\r\n                text-shadow:0 1px 0 #E4F2FD;\r\n            }\r\n            th{text-align:left;}\r\n            .row1{  \r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:#EDF3FE none repeat scroll 0 0;\r\n            }\r\n            .row2{\r\n                -moz-background-clip:border;\r\n                -moz-background-inline-policy:continuous;\r\n                -moz-background-origin:padding;\r\n                background:white none repeat scroll 0 0;\r\n            }\r\n            body{line-height:16px;}\r\n            td.numero {text-align:left;}\r\n            td.texto {text-align:left;}\r\n            table {border:solid;height:200px;}\r\n            @page {\r\n                size:letter;\r\n                {% if watermark_filename %}\r\n                    background-image: url({{watermark_filename}});\r\n                {% endif %}\r\n                top: 1cm;\r\n                left: 1cm;\r\n                right: 1.7cm;\r\n            }\r\n        </style>\r\n    </head>\r\n    <body>\r\n        <h1>Cotizacion {{doc.0.doc_number}}</h1>\r\n        <table id=\"tableContent\">\r\n            <thead>\r\n                <tr><th></th><th>Descripcion</th><th>Cantidad</th><th>Unidad</th><th>Valor</th></tr>\r\n            </thead>\r\n            <tbody>\r\n                {% for sale in doc.lines %}\r\n            {% if sale.tipo == \'SaleDiscount\' %}\r\n              <tr><td/><td> Descuento</td><td/><td/><td>(${{sale.value|floatformat:2}})</td></tr>\r\n            {% else %}\r\n            <tr>\r\n                <td class=\"numero\">{% if sale.item.image %}<img src=\"{{sale.item.image.url_75x75}}\">{% endif %}</td>\r\n                <td class=\"texto\">{{sale.item.name}}</td>\r\n                <td class=\"numero\">{{sale.quantity|floatformat:-2}}</td>\r\n                <td class=\"texto\">{{sale.item.unit}}</td>\r\n                <td class=\"numero\">${{sale.value|floatformat:2}}</td>\r\n            </tr>\r\n           {% endif %}\r\n        {%endfor%}\r\n            </tbody>\r\n            \r\n        </table>\r\n    </body>\r\n</html>','');
/*!40000 ALTER TABLE `inventory_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_sale`
--

DROP TABLE IF EXISTS `inventory_sale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_sale` (
  `transaction_ptr_id` int(11) NOT NULL,
  `related_cost_id` int(11) DEFAULT NULL,
  `calculated_cost` decimal(8,2) DEFAULT NULL,
  PRIMARY KEY (`transaction_ptr_id`),
  KEY `inventory_sale_59e9bd39` (`related_cost_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_sale`
--

LOCK TABLES `inventory_sale` WRITE;
/*!40000 ALTER TABLE `inventory_sale` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_sale` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_salereturn`
--

DROP TABLE IF EXISTS `inventory_salereturn`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_salereturn` (
  `sale_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`sale_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_salereturn`
--

LOCK TABLES `inventory_salereturn` WRITE;
/*!40000 ALTER TABLE `inventory_salereturn` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_salereturn` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_saletax`
--

DROP TABLE IF EXISTS `inventory_saletax`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_saletax` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_saletax`
--

LOCK TABLES `inventory_saletax` WRITE;
/*!40000 ALTER TABLE `inventory_saletax` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_saletax` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_setting`
--

DROP TABLE IF EXISTS `inventory_setting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `tipo` varchar(64) NOT NULL,
  `_value` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=60 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_setting`
--

LOCK TABLES `inventory_setting` WRITE;
/*!40000 ALTER TABLE `inventory_setting` DISABLE KEYS */;
INSERT INTO `inventory_setting` VALUES (43,'Default credit days','__builtin__.int','30'),(40,'Default receipt','jade.inventory.models.Report','1'),(23,'Tax account','jade.inventory.models.Account','9'),(21,'Vendors account','jade.inventory.models.Account','7'),(20,'Liabilities account','jade.inventory.models.Account','6'),(19,'Clients account','jade.inventory.models.Account','5'),(18,'Bank account','jade.inventory.models.Account','4'),(17,'Inventory account','jade.inventory.models.Account','3'),(15,'Assets account','jade.inventory.models.Account','1'),(16,'Cash account','jade.inventory.models.Account','2'),(24,'Sales Tax account','jade.inventory.models.Account','10'),(25,'Default sales tax account','jade.inventory.models.Account','11'),(26,'Purchase tax account','jade.inventory.models.Account','12'),(27,'Default purchase tax account','jade.inventory.models.Account','13'),(28,'Equity account','jade.inventory.models.Account','14'),(29,'Revenue account','jade.inventory.models.Account','15'),(30,'Sub revenue account','jade.inventory.models.Account','16'),(31,'Default revenue account','jade.inventory.models.Account','17'),(32,'Default discounts account','jade.inventory.models.Account','18'),(33,'Default returns account','jade.inventory.models.Account','19'),(34,'Expense account','jade.inventory.models.Account','20'),(35,'Inventory expense account','jade.inventory.models.Account','21'),(36,'Counts expense account','jade.inventory.models.Account','22'),(37,'Transfer expense account','jade.inventory.models.Account','23'),(38,'Production expense account','jade.inventory.models.Account','24'),(39,'Default account group','jade.inventory.models.AccountGroup','1'),(41,'Company name','__builtin__.str','ACME Industrias Inc.'),(45,'Login redirect url','__builtin__.str','/inventory/sales/'),(46,'Default unit','jade.inventory.models.Unit','1'),(42,'Date format','__builtin__.str','d/m/Y'),(47,'Default fixed price','__builtin__.int','0'),(48,'Default relative price','__builtin__.int','1'),(49,'Quote report','jade.inventory.models.Report','13'),(50,'Autocreate vendors','__builtin__.bool','True'),(51,'Autocreate clients','__builtin__.bool','True'),(52,'Last automatic barcode','__builtin__.str','1001'),(53,'Payments made account','jade.inventory.models.Account','2'),(54,'Count sheet report','jade.inventory.models.Report','9'),(55,'Account statement report','jade.inventory.models.Report','11'),(56,'Price report','jade.inventory.models.Report','7'),(57,'Low stock report','jade.inventory.models.Report','12'),(58,'Inventory report','jade.inventory.models.Report','8'),(59,'Payments received account','jade.inventory.models.Account','2'),(1,'Default price group','jade.inventory.models.PriceGroup','1'),(44,'Default client','jade.inventory.models.Client','33'),(22,'Default Vendor','jade.inventory.models.Vendor','8');
/*!40000 ALTER TABLE `inventory_setting` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_tab`
--

DROP TABLE IF EXISTS `inventory_tab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_tab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `url` varchar(32) NOT NULL,
  `perm` varchar(32) NOT NULL,
  `klass` varchar(32) NOT NULL,
  `keywords` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_tab`
--

LOCK TABLES `inventory_tab` WRITE;
/*!40000 ALTER TABLE `inventory_tab` DISABLE KEYS */;
INSERT INTO `inventory_tab` VALUES (1,'Items','/inventory/items/','inventory.view_item','Tab',''),(2,'Transactions','/inventory/transactions/','inventory.view_transaction','Tab',''),(3,'Accounts','/inventory/accounts/','inventory.view_account','Tab',''),(4,'Production','/inventory/production/','inventory.view_production','Tab','');
/*!40000 ALTER TABLE `inventory_tab` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_taxrate`
--

DROP TABLE IF EXISTS `inventory_taxrate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_taxrate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `value` decimal(3,2) NOT NULL,
  `sales_account_id` int(11) NOT NULL,
  `purchases_account_id` int(11) NOT NULL,
  `price_includes_tax` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `inventory_taxrate_59b3992f` (`sales_account_id`),
  KEY `inventory_taxrate_70141dd` (`purchases_account_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_taxrate`
--

LOCK TABLES `inventory_taxrate` WRITE;
/*!40000 ALTER TABLE `inventory_taxrate` DISABLE KEYS */;
INSERT INTO `inventory_taxrate` VALUES (1,'Consumidor Final','0.13',11,13,1),(2,'Credito Fiscal','0.13',25,26,1),(3,'Retencion Consumidor Final','0.01',27,27,1),(4,'Retencion Credito Fiscal','0.01',28,28,1);
/*!40000 ALTER TABLE `inventory_taxrate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_transaction`
--

DROP TABLE IF EXISTS `inventory_transaction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `_date` datetime NOT NULL,
  `doc_number` varchar(32) NOT NULL,
  `comments` varchar(200) NOT NULL,
  `tipo` varchar(16) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_transaction`
--

LOCK TABLES `inventory_transaction` WRITE;
/*!40000 ALTER TABLE `inventory_transaction` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_transaction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_transaction_sites`
--

DROP TABLE IF EXISTS `inventory_transaction_sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_transaction_sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `transaction_id` int(11) NOT NULL,
  `site_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `transaction_id` (`transaction_id`,`site_id`),
  KEY `site_id_refs_id_78894c66` (`site_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_transaction_sites`
--

LOCK TABLES `inventory_transaction_sites` WRITE;
/*!40000 ALTER TABLE `inventory_transaction_sites` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_transaction_sites` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_transactiontipo`
--

DROP TABLE IF EXISTS `inventory_transactiontipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_transactiontipo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  `obj` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=22 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_transactiontipo`
--

LOCK TABLES `inventory_transactiontipo` WRITE;
/*!40000 ALTER TABLE `inventory_transactiontipo` DISABLE KEYS */;
INSERT INTO `inventory_transactiontipo` VALUES (1,'Sale','jade.inventory.models.Sale'),(2,'Purchase','jade.inventory.models.Purchase'),(3,'Count','jade.inventory.models.Count'),(4,'ClientPayment','jade.inventory.models.ClientPayment'),(5,'VendorPayment','jade.inventory.models.VendorPayment'),(6,'VendorGarantee','jade.inventory.models.VendorGarantee'),(7,'ClientGarantee','jade.inventory.models.ClientGarantee'),(8,'SaleReturn','jade.inventory.models.SaleReturn'),(9,'PurchaseReturn','jade.inventory.models.PurchaseReturn'),(10,'ClientRefund','jade.inventory.models.ClientRefund'),(11,'VendorRefund','jade.inventory.models.VendorRefund'),(12,'Production','jade.production.models.Production'),(13,'Process','jade.production.models.Process'),(14,'Job','jade.production.models.Job'),(15,'Transfer','jade.inventory.models.Transfer'),(16,'Accounting','jade.inventory.models.Accounting'),(17,'SaleTax','jade.inventory.models.SaleTax'),(18,'SaleDiscount','jade.inventory.models.SaleDiscount'),(19,'PurchaseTax','jade.inventory.models.PurchaseTax'),(20,'PurchaseDiscount','jade.inventory.models.PurchaseDiscount'),(21,'CashClosing','jade.inventory.models.CashClosing');
/*!40000 ALTER TABLE `inventory_transactiontipo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_unit`
--

DROP TABLE IF EXISTS `inventory_unit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_unit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_unit`
--

LOCK TABLES `inventory_unit` WRITE;
/*!40000 ALTER TABLE `inventory_unit` DISABLE KEYS */;
INSERT INTO `inventory_unit` VALUES (1,'Cada Uno');
/*!40000 ALTER TABLE `inventory_unit` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_userprofile`
--

DROP TABLE IF EXISTS `inventory_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_userprofile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `price_group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  KEY `inventory_userprofile_2f5f464c` (`price_group_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_userprofile`
--

LOCK TABLES `inventory_userprofile` WRITE;
/*!40000 ALTER TABLE `inventory_userprofile` DISABLE KEYS */;
INSERT INTO `inventory_userprofile` VALUES (1,1,1);
/*!40000 ALTER TABLE `inventory_userprofile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_userprofile_tabs`
--

DROP TABLE IF EXISTS `inventory_userprofile_tabs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_userprofile_tabs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userprofile_id` int(11) NOT NULL,
  `tab_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userprofile_id` (`userprofile_id`,`tab_id`),
  KEY `tab_id_refs_id_50cd03de` (`tab_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_userprofile_tabs`
--

LOCK TABLES `inventory_userprofile_tabs` WRITE;
/*!40000 ALTER TABLE `inventory_userprofile_tabs` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_userprofile_tabs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_vendor`
--

DROP TABLE IF EXISTS `inventory_vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_vendor` (
  `contact_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`contact_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_vendor`
--

LOCK TABLES `inventory_vendor` WRITE;
/*!40000 ALTER TABLE `inventory_vendor` DISABLE KEYS */;
INSERT INTO `inventory_vendor` VALUES (8);
/*!40000 ALTER TABLE `inventory_vendor` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_vendorpayment`
--

DROP TABLE IF EXISTS `inventory_vendorpayment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_vendorpayment` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_vendorpayment`
--

LOCK TABLES `inventory_vendorpayment` WRITE;
/*!40000 ALTER TABLE `inventory_vendorpayment` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_vendorpayment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventory_vendorrefund`
--

DROP TABLE IF EXISTS `inventory_vendorrefund`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `inventory_vendorrefund` (
  `transaction_ptr_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_ptr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventory_vendorrefund`
--

LOCK TABLES `inventory_vendorrefund` WRITE;
/*!40000 ALTER TABLE `inventory_vendorrefund` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventory_vendorrefund` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `updates_updatesrun`
--

DROP TABLE IF EXISTS `updates_updatesrun`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `updates_updatesrun` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=12 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `updates_updatesrun`
--

LOCK TABLES `updates_updatesrun` WRITE;
/*!40000 ALTER TABLE `updates_updatesrun` DISABLE KEYS */;
INSERT INTO `updates_updatesrun` VALUES (11,'ListItems'),(10,'HelloWorld'),(9,'HelloAgain');
/*!40000 ALTER TABLE `updates_updatesrun` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2011-01-12 14:36:23
