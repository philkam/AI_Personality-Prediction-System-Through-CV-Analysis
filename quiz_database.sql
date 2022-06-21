-- phpMyAdmin SQL Dump
-- version 4.8.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Jun 20, 2022 at 07:56 PM
-- Server version: 5.7.24
-- PHP Version: 7.2.14

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `quiz_database`
--

-- --------------------------------------------------------

--
-- Table structure for table `active_question_paper`
--

CREATE SCHEMA quiz_database;
DROP TABLE IF EXISTS `active_question_paper`;
CREATE TABLE IF NOT EXISTS `active_question_paper` (
  `question_paper_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `question_type` varchar(255) DEFAULT NULL,
  `stud_id` int(11) NOT NULL,
  `attend` int(11) NOT NULL
);

--
-- Dumping data for table `active_question_paper`
--


-- --------------------------------------------------------

--
-- Table structure for table `answer_details`
--

DROP TABLE IF EXISTS `answer_details`;
CREATE TABLE IF NOT EXISTS `answer_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_paper_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `stud_id` int(11) NOT NULL,
  `response` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

--
-- Dumping data for table `answer_details`
--

-- --------------------------------------------------------

--
-- Table structure for table `instructor_details`
--

DROP TABLE IF EXISTS `instructor_details`;
CREATE TABLE IF NOT EXISTS `instructor_details` (
  `data` int(11) NOT NULL AUTO_INCREMENT,
  `firstnme` varchar(255) DEFAULT NULL,
  `lst_nme` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `cntno` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `qualification` varchar(255) DEFAULT NULL,
  `house` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `pin` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`data`)
) ENGINE=MyISAM AUTO_INCREMENT=106 DEFAULT CHARSET=latin1;

--
-- Dumping data for table `instructor_details`
--


-- --------------------------------------------------------

--
-- Table structure for table `login`
--

DROP TABLE IF EXISTS `login`;
CREATE TABLE IF NOT EXISTS `login` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `u_email` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `user_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

--
-- Dumping data for table `login`
--


-- Table structure for table `question_details`
--

DROP TABLE IF EXISTS `question_details`;
CREATE TABLE IF NOT EXISTS `question_details` (
  `question_id` int(11) NOT NULL AUTO_INCREMENT,
  `question` varchar(255) DEFAULT NULL,
  `value1` varchar(255) DEFAULT NULL,
  `value2` varchar(255) DEFAULT NULL,
  `value3` varchar(255) DEFAULT NULL,
  `value4` varchar(255) DEFAULT NULL,
  `answer` varchar(255) DEFAULT NULL,
  `question_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`question_id`)
);

--
-- Dumping data for table `question_details`
--


-- --------------------------------------------------------

--
-- Table structure for table `question_paper`
--

DROP TABLE IF EXISTS `question_paper`;
CREATE TABLE IF NOT EXISTS `question_paper` (
  `question_paper_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `question_type` varchar(255) DEFAULT NULL,
  `science` int(11) DEFAULT NULL,
  `commerce` int(11) DEFAULT NULL,
  `humanities` int(11) DEFAULT NULL,
  `apt` int(11) DEFAULT NULL
);

--
-- Dumping data for table `question_paper`
--



-- --------------------------------------------------------

--
-- Table structure for table `student_description`
--

DROP TABLE IF EXISTS `student_description`;
CREATE TABLE IF NOT EXISTS `student_description` (
  `stud_id` int(11) NOT NULL,
  `descrip1` varchar(255) DEFAULT NULL,
  `descrip2` varchar(255) DEFAULT NULL,
  `descrip3` varchar(255) DEFAULT NULL
);

--
-- Dumping data for table `student_description`
--

-- --------------------------------------------------------

--
-- Table structure for table `student_profile`
--

DROP TABLE IF EXISTS `student_profile`;
CREATE TABLE IF NOT EXISTS `student_profile` (
  `stud_id` int(11) NOT NULL,
  `stud_first_name` varchar(255) DEFAULT NULL,
  `stud_last_name` varchar(255) DEFAULT NULL,
  `stud_dob` date DEFAULT NULL,
  `stud_gender` varchar(255) DEFAULT NULL,
  `cnt_number` varchar(255) DEFAULT NULL,
  `stud_email` varchar(255) DEFAULT NULL,
  `stud_inst` varchar(255) DEFAULT NULL,
  `stud_class` varchar(255) DEFAULT NULL,
  `stud_house` varchar(255) DEFAULT NULL,
  `stud_city` varchar(255) DEFAULT NULL,
  `stud_country` varchar(255) DEFAULT NULL,
  `pin_code` varchar(255) DEFAULT NULL,
  `science` varchar(255) DEFAULT NULL,
  `commerce` varchar(255) DEFAULT NULL,
  `humanities` varchar(255) DEFAULT NULL,
  `aptitude` varchar(255) DEFAULT NULL,
  `total` int(11) DEFAULT NULL
);

--
-- Dumping data for table `student_profile`
--

-- --------------------------------------------------------

--
-- Table structure for table `user_data`
--

DROP TABLE IF EXISTS `user_data`;
CREATE TABLE IF NOT EXISTS `user_data` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Email_ID` varchar(50) NOT NULL,
  `Page_no` varchar(5) NOT NULL,
  `Actual_skills` varchar(5000) NOT NULL,
  `stud_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `stud_id` (`stud_id`)
);

CREATE UNIQUE INDEX uidx_pid
ON user_data (stud_id);

--
-- Dumping data for table `user_data`
--



/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
