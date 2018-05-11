create database titanBox;

use titanBox;

grant all on titanBox.* to 'admin' identified by '551996';


CREATE TABLE `Files` (
  `Id` int(16) AUTO_INCREMENT,
  `Name` varchar(200) DEFAULT NULL,
  `Tag` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `Blocks` (
  `Id` int(16) NOT NULL AUTO_INCREMENT,
  `Block` mediumtext,
  `Tag` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `EncryptionKeys` (
  `Id` int(16) NOT NULL AUTO_INCREMENT,
  `EncryptionKey` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `LoginDetails` (
  `id` int(16) NOT NULL AUTO_INCREMENT,
  `username` varchar(32) DEFAULT NULL,
  `password_hash` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

CREATE TABLE `LoggedIn` (
  `id` int(16) DEFAULT NULL,
  `ipv4_addr` varchar(40) DEFAULT NULL,
  KEY `id` (`id`),
  CONSTRAINT `LoggedIn_ibfk_1` FOREIGN KEY (`id`) REFERENCES `LoginDetails` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `BlockBelongsTo` (
  `FileId` int(16) DEFAULT NULL,
  `BlockId` longtext,
  KEY `FileId` (`FileId`),
  CONSTRAINT `BlockBelongsTo_ibfk_1` FOREIGN KEY (`FileId`) REFERENCES `Files` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `FileBelongsTo` (
  `userId` int(16) NOT NULL,
  `FileId` int(16) NOT NULL,
  PRIMARY KEY (`userId`,`FileId`),
  KEY `FileId` (`FileId`),
  CONSTRAINT `FileBelongsTo_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `LoginDetails` (`id`),
  CONSTRAINT `FileBelongsTo_ibfk_2` FOREIGN KEY (`FileId`) REFERENCES `Files` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `KeyStore` (
  `userId` int(16) NOT NULL,
  `blockId` int(16) NOT NULL,
  `keyId` int(16) NOT NULL,
  PRIMARY KEY (`userId`,`blockId`,`keyId`),
  KEY `blockId` (`blockId`),
  KEY `keyId` (`keyId`),
  CONSTRAINT `KeyStore_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `LoginDetails` (`id`),
  CONSTRAINT `KeyStore_ibfk_2` FOREIGN KEY (`blockId`) REFERENCES `Blocks` (`Id`),
  CONSTRAINT `KeyStore_ibfk_3` FOREIGN KEY (`keyId`) REFERENCES `EncryptionKeys` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

