CREATE TABLE `auditEvents` (
	`id` int AUTO_INCREMENT NOT NULL,
	`eventType` varchar(64) NOT NULL,
	`emailKey` varchar(48),
	`detail` json NOT NULL,
	`actorId` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `auditEvents_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `emailRevisions` (
	`id` int AUTO_INCREMENT NOT NULL,
	`emailKey` varchar(48) NOT NULL,
	`sourceDigest` varchar(64) NOT NULL,
	`provider` varchar(32) NOT NULL DEFAULT 'beefree',
	`providerDocument` longtext NOT NULL,
	`renderedHtml` longtext,
	`subject` text,
	`previewText` text,
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `emailRevisions_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `exportPackages` (
	`id` int AUTO_INCREMENT NOT NULL,
	`emailKey` varchar(48) NOT NULL,
	`sourceDigest` varchar(64) NOT NULL,
	`checksum` varchar(64) NOT NULL,
	`renderedHtml` longtext NOT NULL,
	`manifest` json NOT NULL,
	`qaSummary` text NOT NULL,
	`status` varchar(32) NOT NULL DEFAULT 'exported',
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `exportPackages_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `qaRuns` (
	`id` int AUTO_INCREMENT NOT NULL,
	`emailKey` varchar(48) NOT NULL,
	`revisionId` int,
	`status` varchar(32) NOT NULL,
	`summary` text NOT NULL,
	`checks` json NOT NULL,
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `qaRuns_id` PRIMARY KEY(`id`)
);
--> statement-breakpoint
CREATE TABLE `shopifyHandoffEvidence` (
	`id` int AUTO_INCREMENT NOT NULL,
	`emailKey` varchar(48) NOT NULL,
	`targetSurface` varchar(32) NOT NULL,
	`shopifyDraftUrl` text NOT NULL,
	`evidenceNote` text NOT NULL,
	`status` varchar(32) NOT NULL DEFAULT 'shopify_draft_verified',
	`createdBy` int,
	`createdAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `shopifyHandoffEvidence_id` PRIMARY KEY(`id`)
);
