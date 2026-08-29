CREATE TABLE `marketingSyncReceipts` (
	`runId` varchar(64) NOT NULL,
	`source` varchar(48) NOT NULL,
	`status` varchar(32) NOT NULL,
	`recordCount` int NOT NULL,
	`changedCount` int NOT NULL,
	`blockedCount` int NOT NULL,
	`completedAt` timestamp NOT NULL,
	`receivedAt` timestamp NOT NULL DEFAULT (now()) ON UPDATE CURRENT_TIMESTAMP,
	CONSTRAINT `marketingSyncReceipts_runId` PRIMARY KEY(`runId`)
);
