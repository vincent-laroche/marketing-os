CREATE TABLE `canonicalCampaigns` (
	`emailKey` varchar(48) NOT NULL,
	`sourceDigest` varchar(64) NOT NULL,
	`sourcePath` varchar(255) NOT NULL,
	`series` varchar(32) NOT NULL,
	`shopifySurface` varchar(32) NOT NULL,
	`sourceStatus` varchar(32) NOT NULL,
	`canonicalDocument` json NOT NULL,
	`syncedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `canonicalCampaigns_emailKey` PRIMARY KEY(`emailKey`)
);
--> statement-breakpoint
CREATE TABLE `flowRecipeVersions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`journey` varchar(96) NOT NULL,
	`version` varchar(32) NOT NULL,
	`checksum` varchar(64) NOT NULL,
	`definition` json NOT NULL,
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `flowRecipeVersions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
ALTER TABLE `exportPackages` ADD `artifactKey` varchar(512) NOT NULL;--> statement-breakpoint
ALTER TABLE `exportPackages` ADD `artifactUrl` text NOT NULL;