DROP DATABASE IF EXISTS `t1`;
DROP DATABASE IF EXISTS `t2`;
CREATE DATABASE `t1`;
CREATE DATABASE `t2`;

USE t1
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `user1`;
CREATE TABLE `user1` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户编号',
	  `username` varchar(20) NOT NULL COMMENT '用户名',
	  `password` char(32) NOT NULL COMMENT '密码',
	  `email` varchar(50) NOT NULL COMMENT '邮箱',
	  `age` tinyint(3) unsigned NOT NULL DEFAULT 18 COMMENT '年龄',
	  `sex` enum('man','woman','baomi') NOT NULL DEFAULT 'baomi' COMMENT '性别',
	  `tel` char(11) NOT NULL COMMENT '电话',
	  `addr` varchar(50) NOT NULL DEFAULT 'beijing' COMMENT '地址',
	  `card` char(18) NOT NULL COMMENT '身份证号',
	  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `user2`;
CREATE TABLE `user2` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户编号',
	  `username` varchar(20) NOT NULL COMMENT '用户名',
	  `password` char(32) NOT NULL COMMENT '密码',
	  `email` varchar(50) NOT NULL COMMENT '邮箱',
	  `age` tinyint(3) unsigned NOT NULL DEFAULT 18 COMMENT '年龄',
	  `sex` enum('man','woman','baomi') NOT NULL DEFAULT 'baomi' COMMENT '性别',
	  `tel` char(11) NOT NULL COMMENT '电话',
	  `addr` varchar(50) NOT NULL DEFAULT 'beijing' COMMENT '地址',
	  `card` char(18) NOT NULL COMMENT '身份证号',
	  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;


INSERT INTO `user1` VALUES ('1', 'A', 'A', 'A', '18', 'baomi', '123', 'beijing', '1');
INSERT INTO `user1` VALUES ('2', 'B', 'B', 'B', '18', 'baomi', '456', 'beijing', '2');
INSERT INTO `user1` VALUES ('3', 'CCC', 'CCC', 'CCC', '18', 'baomi', '678', 'beijing', '5');
INSERT INTO `user2` VALUES ('1', 'A', 'A', 'A', '18', 'baomi', '123', 'beijing', '1');
INSERT INTO `user2` VALUES ('2', 'B', 'B', 'B', '18', 'baomi', '456', 'beijing', '2');
INSERT INTO `user2` VALUES ('3', 'CCC', 'CCC', 'CCC', '18', 'baomi', '678', 'beijing', '5');

USE t2
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `cold1`;
CREATE TABLE `cold1` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户编号',
	  `username` varchar(20) NOT NULL COMMENT '用户名',
	  `password` char(32) NOT NULL COMMENT '密码',
	  `email` varchar(50) NOT NULL COMMENT '邮箱',
	  `age` tinyint(3) unsigned NOT NULL DEFAULT 18 COMMENT '年龄',
	  `sex` enum('man','woman','baomi') NOT NULL DEFAULT 'baomi' COMMENT '性别',
	  `tel` char(11) NOT NULL COMMENT '电话',
	  `addr` varchar(50) NOT NULL DEFAULT 'beijing' COMMENT '地址',
	  `card` char(18) NOT NULL COMMENT '身份证号',
	  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS `cold2`;
CREATE TABLE `cold2` (
	  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT '用户编号',
	  `username` varchar(20) NOT NULL COMMENT '用户名',
	  `password` char(32) NOT NULL COMMENT '密码',
	  `email` varchar(50) NOT NULL COMMENT '邮箱',
	  `age` tinyint(3) unsigned NOT NULL DEFAULT 18 COMMENT '年龄',
	  `sex` enum('man','woman','baomi') NOT NULL DEFAULT 'baomi' COMMENT '性别',
	  `tel` char(11) NOT NULL COMMENT '电话',
	  `addr` varchar(50) NOT NULL DEFAULT 'beijing' COMMENT '地址',
	  `card` char(18) NOT NULL COMMENT '身份证号',
	  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

INSERT INTO `cold1` VALUES ('1', 'A', 'A', 'A', '18', 'baomi', '123', 'beijing', '1');
INSERT INTO `cold1` VALUES ('2', 'B', 'B', 'B', '18', 'baomi', '456', 'beijing', '2');
INSERT INTO `cold1` VALUES ('3', 'CCC', 'CCC', 'CCC', '18', 'baomi', '678', 'beijing', '5');
INSERT INTO `cold2` VALUES ('1', 'A', 'A', 'A', '18', 'baomi', '123', 'beijing', '1');
INSERT INTO `cold2` VALUES ('2', 'B', 'B', 'B', '18', 'baomi', '456', 'beijing', '2');
INSERT INTO `cold2` VALUES ('3', 'CCC', 'CCC', 'CCC', '18', 'baomi', '678', 'beijing', '5');

