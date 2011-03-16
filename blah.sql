BEGIN;CREATE TABLE `inventory_tab` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `url` varchar(32) NOT NULL,
    `perm` varchar(32) NOT NULL,
    `klass` varchar(32) NOT NULL,
    `keywords` varchar(32) NOT NULL
)
;
CREATE TABLE `inventory_setting` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `tipo` varchar(64) NOT NULL,
    `_value` varchar(64) NOT NULL
)
;
CREATE TABLE `inventory_transactiontipo` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `obj` varchar(64) NOT NULL
)
;
CREATE TABLE `inventory_report` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `body` longtext NOT NULL,
    `image` varchar(100)
)
;
CREATE TABLE `inventory_unit` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
CREATE TABLE `inventory_category` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
CREATE TABLE `inventory_item` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(200) NOT NULL UNIQUE,
    `bar_code` varchar(64) NOT NULL,
    `image` varchar(100),
    `minimum` numeric(8, 2) NOT NULL,
    `maximum` numeric(8, 2) NOT NULL,
    `default_cost` numeric(8, 2) NOT NULL,
    `location` varchar(32) NOT NULL,
    `description` varchar(1024) NOT NULL,
    `unit_id` integer NOT NULL,
    `auto_bar_code` bool NOT NULL,
    `tipo` varchar(16) NOT NULL
)
;
ALTER TABLE `inventory_item` ADD CONSTRAINT `unit_id_refs_id_2e72e2ee` FOREIGN KEY (`unit_id`) REFERENCES `inventory_unit` (`id`);
CREATE TABLE `inventory_linkeditem` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer NOT NULL,
    `child_id` integer NOT NULL,
    `quantity` numeric(8, 2) NOT NULL,
    `fixed` numeric(8, 2) NOT NULL,
    `relative` numeric(8, 2) NOT NULL
)
;
ALTER TABLE `inventory_linkeditem` ADD CONSTRAINT `parent_id_refs_id_1abda29a` FOREIGN KEY (`parent_id`) REFERENCES `inventory_item` (`id`);
ALTER TABLE `inventory_linkeditem` ADD CONSTRAINT `child_id_refs_id_1abda29a` FOREIGN KEY (`child_id`) REFERENCES `inventory_item` (`id`);
CREATE TABLE `inventory_pricegroup` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
CREATE TABLE `inventory_price` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `group_id` integer NOT NULL,
    `item_id` integer NOT NULL,
    `site_id` integer NOT NULL,
    `fixed_discount` numeric(8, 2) NOT NULL,
    `relative_discount` numeric(8, 2) NOT NULL,
    `fixed` numeric(8, 2) NOT NULL,
    `relative` numeric(8, 2) NOT NULL
)
;
ALTER TABLE `inventory_price` ADD CONSTRAINT `item_id_refs_id_1032c852` FOREIGN KEY (`item_id`) REFERENCES `inventory_item` (`id`);
ALTER TABLE `inventory_price` ADD CONSTRAINT `site_id_refs_id_607b0270` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
ALTER TABLE `inventory_price` ADD CONSTRAINT `group_id_refs_id_67254e73` FOREIGN KEY (`group_id`) REFERENCES `inventory_pricegroup` (`id`);
CREATE TABLE `inventory_account` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(200) NOT NULL,
    `number` varchar(32) NOT NULL,
    `multiplier` integer NOT NULL,
    `tipo` varchar(16) NOT NULL,
    `site_id` integer NOT NULL
)
;
ALTER TABLE `inventory_account` ADD CONSTRAINT `site_id_refs_id_5c90b614` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
CREATE TABLE `inventory_taxrate` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `value` numeric(3, 2) NOT NULL,
    `sales_account_id` integer NOT NULL,
    `purchases_account_id` integer NOT NULL,
    `price_includes_tax` bool NOT NULL
)
;
ALTER TABLE `inventory_taxrate` ADD CONSTRAINT `sales_account_id_refs_id_53c164a1` FOREIGN KEY (`sales_account_id`) REFERENCES `inventory_account` (`id`);
ALTER TABLE `inventory_taxrate` ADD CONSTRAINT `purchases_account_id_refs_id_53c164a1` FOREIGN KEY (`purchases_account_id`) REFERENCES `inventory_account` (`id`);
CREATE TABLE `inventory_accountgroup` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `revenue_account_id` integer NOT NULL,
    `discounts_account_id` integer NOT NULL,
    `returns_account_id` integer NOT NULL,
    `default_tax_rate_id` integer NOT NULL,
    `site_id` integer NOT NULL
)
;
ALTER TABLE `inventory_accountgroup` ADD CONSTRAINT `default_tax_rate_id_refs_id_57e9ff5` FOREIGN KEY (`default_tax_rate_id`) REFERENCES `inventory_taxrate` (`id`);
ALTER TABLE `inventory_accountgroup` ADD CONSTRAINT `site_id_refs_id_2c0f596` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
ALTER TABLE `inventory_accountgroup` ADD CONSTRAINT `revenue_account_id_refs_id_5762e4c7` FOREIGN KEY (`revenue_account_id`) REFERENCES `inventory_account` (`id`);
ALTER TABLE `inventory_accountgroup` ADD CONSTRAINT `discounts_account_id_refs_id_5762e4c7` FOREIGN KEY (`discounts_account_id`) REFERENCES `inventory_account` (`id`);
ALTER TABLE `inventory_accountgroup` ADD CONSTRAINT `returns_account_id_refs_id_5762e4c7` FOREIGN KEY (`returns_account_id`) REFERENCES `inventory_account` (`id`);
CREATE TABLE `inventory_contact` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `tax_group_name` varchar(32) NOT NULL,
    `price_group_id` integer NOT NULL,
    `receipt_id` integer NOT NULL,
    `account_group_id` integer NOT NULL,
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
    `user_id` integer,
    `account_id` integer NOT NULL UNIQUE,
    `credit_days` integer NOT NULL
)
;
ALTER TABLE `inventory_contact` ADD CONSTRAINT `receipt_id_refs_id_2c8de6c0` FOREIGN KEY (`receipt_id`) REFERENCES `inventory_report` (`id`);
ALTER TABLE `inventory_contact` ADD CONSTRAINT `account_group_id_refs_id_27bf557a` FOREIGN KEY (`account_group_id`) REFERENCES `inventory_accountgroup` (`id`);
ALTER TABLE `inventory_contact` ADD CONSTRAINT `user_id_refs_id_1d7d464c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `inventory_contact` ADD CONSTRAINT `price_group_id_refs_id_ea132fa` FOREIGN KEY (`price_group_id`) REFERENCES `inventory_pricegroup` (`id`);
ALTER TABLE `inventory_contact` ADD CONSTRAINT `account_id_refs_id_7a04302c` FOREIGN KEY (`account_id`) REFERENCES `inventory_account` (`id`);
CREATE TABLE `inventory_garanteeoffer` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `months` integer NOT NULL,
    `price` numeric(8, 2) NOT NULL,
    `item_id` integer NOT NULL,
    `site_id` integer NOT NULL
)
;
ALTER TABLE `inventory_garanteeoffer` ADD CONSTRAINT `site_id_refs_id_3eb383a0` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
ALTER TABLE `inventory_garanteeoffer` ADD CONSTRAINT `item_id_refs_id_54569e7e` FOREIGN KEY (`item_id`) REFERENCES `inventory_item` (`id`);
CREATE TABLE `inventory_userprofile_tabs` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `userprofile_id` integer NOT NULL,
    `tab_id` integer NOT NULL,
    UNIQUE (`userprofile_id`, `tab_id`)
)
;
ALTER TABLE `inventory_userprofile_tabs` ADD CONSTRAINT `tab_id_refs_id_50cd03de` FOREIGN KEY (`tab_id`) REFERENCES `inventory_tab` (`id`);
CREATE TABLE `inventory_userprofile` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL UNIQUE,
    `price_group_id` integer NOT NULL
)
;
ALTER TABLE `inventory_userprofile` ADD CONSTRAINT `price_group_id_refs_id_1293e92` FOREIGN KEY (`price_group_id`) REFERENCES `inventory_pricegroup` (`id`);
ALTER TABLE `inventory_userprofile` ADD CONSTRAINT `user_id_refs_id_114f884c` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
ALTER TABLE `inventory_userprofile_tabs` ADD CONSTRAINT `userprofile_id_refs_id_7d3f5b8b` FOREIGN KEY (`userprofile_id`) REFERENCES `inventory_userprofile` (`id`);
CREATE TABLE `inventory_transaction_sites` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `transaction_id` integer NOT NULL,
    `site_id` integer NOT NULL,
    UNIQUE (`transaction_id`, `site_id`)
)
;
ALTER TABLE `inventory_transaction_sites` ADD CONSTRAINT `site_id_refs_id_78894c66` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
CREATE TABLE `inventory_transaction` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `_date` datetime NOT NULL,
    `doc_number` varchar(32) NOT NULL,
    `comments` varchar(200) NOT NULL,
    `tipo` varchar(16) NOT NULL
)
;
ALTER TABLE `inventory_transaction_sites` ADD CONSTRAINT `transaction_id_refs_id_4f0bb58` FOREIGN KEY (`transaction_id`) REFERENCES `inventory_transaction` (`id`);
CREATE TABLE `inventory_entry` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `transaction_id` integer NOT NULL,
    `value` numeric(8, 2) NOT NULL,
    `account_id` integer NOT NULL,
    `delivered` bool NOT NULL,
    `quantity` numeric(8, 2) NOT NULL,
    `item_id` integer,
    `active` bool NOT NULL,
    `tipo` varchar(16) NOT NULL,
    `serial` varchar(32),
    `date` datetime NOT NULL,
    `site_id` integer NOT NULL
)
;
ALTER TABLE `inventory_entry` ADD CONSTRAINT `account_id_refs_id_442a724a` FOREIGN KEY (`account_id`) REFERENCES `inventory_account` (`id`);
ALTER TABLE `inventory_entry` ADD CONSTRAINT `site_id_refs_id_7db017ab` FOREIGN KEY (`site_id`) REFERENCES `django_site` (`id`);
ALTER TABLE `inventory_entry` ADD CONSTRAINT `item_id_refs_id_2c6f98e9` FOREIGN KEY (`item_id`) REFERENCES `inventory_item` (`id`);
ALTER TABLE `inventory_entry` ADD CONSTRAINT `transaction_id_refs_id_30158179` FOREIGN KEY (`transaction_id`) REFERENCES `inventory_transaction` (`id`);
CREATE TABLE `inventory_extravalue` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL,
    `value` numeric(8, 2),
    `transaction_id` integer NOT NULL
)
;
ALTER TABLE `inventory_extravalue` ADD CONSTRAINT `transaction_id_refs_id_4f7f065f` FOREIGN KEY (`transaction_id`) REFERENCES `inventory_transaction` (`id`);COMMIT;
