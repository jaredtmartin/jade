updates=
{
1001: "alter table inventory_contact add column `account_group_id` integer NOT NULL",
1002:"ALTER TABLE `inventory_contact` ADD CONSTRAINT `account_group_id_refs_id_27bf557a` FOREIGN KEY (`account_group_id`) REFERENCES `inventory_accountgroup` (`id`);",

}

    
