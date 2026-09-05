CREATE TABLE `exportPackageScreenshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`exportPackageId` int NOT NULL,
	`viewport` varchar(32) NOT NULL,
	`storageKey` varchar(512) NOT NULL,
	`storageUrl` text NOT NULL,
	`capturedBy` int,
	`capturedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `exportPackageScreenshots_id` PRIMARY KEY(`id`)
);
