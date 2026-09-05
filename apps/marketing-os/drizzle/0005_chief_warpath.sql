CREATE TABLE `exportPackageScreenshotManifests` (
	`id` int AUTO_INCREMENT NOT NULL,
	`exportPackageId` int NOT NULL,
	`checksum` varchar(64) NOT NULL,
	`manifest` json NOT NULL,
	`artifactKey` varchar(512) NOT NULL,
	`artifactUrl` text NOT NULL,
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `exportPackageScreenshotManifests_id` PRIMARY KEY(`id`)
);
