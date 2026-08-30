CREATE TABLE `productSnapshots` (
	`id` int AUTO_INCREMENT NOT NULL,
	`emailKey` varchar(48) NOT NULL,
	`productId` varchar(128) NOT NULL,
	`title` text NOT NULL,
	`handle` varchar(255) NOT NULL,
	`status` varchar(32) NOT NULL,
	`featuredImageUrl` text,
	`price` varchar(48),
	`capturedBy` int,
	`capturedAt` timestamp NOT NULL DEFAULT (now()),
	CONSTRAINT `productSnapshots_id` PRIMARY KEY(`id`)
);
