error detection

negative inventory
-- unbalanced transactions
select transaction_id, total from (select transaction_id, sum(value) total from inventory_entry group by transaction_id) as totals where total!=0;
-- Double prices
select item_id from (select item_id, count(*) count from inventory_price group by item_id, group_id) as dups where count>1;
-- Get a list of value of inventory by item
select item_id, sum(value) from inventory_entry where active=1 and account_id=3 group by item_id;
-- Get quantity of stock by item
select item_id, sum(quantity) from inventory_entry where delivered=1 and account_id=3 group by item_id;
-- Get negative costs
select id, total_cost, stock, cost from
(select id, total_cost, stock, cost.total_cost/stock.stock cost from inventory_item 
inner join (select item_id, sum(quantity) as stock from inventory_entry where delivered=1 and account_id=3 group by item_id) as stock on stock.item_id=inventory_item.id
inner join (select item_id, sum(value) as total_cost from inventory_entry where active=1 and account_id=3 group by item_id) as cost on cost.item_id=inventory_item.id
) as items where cost<0 order by cost;
-- Get negative inventory
select item_id, sum from (select item_id, sum(quantity) sum from inventory_entry where delivered=1 and account_id=3 group by item_id) where sum<0;
-- sales without revenue entries *untested*
select inventory_transaction.id from inventory_transaction left join (select * from inventory_entry where tipo='Revenue') as inventory_entry on inventory_entry.transaction_id=inventory_transaction.id where inventory_transaction.tipo='Sale' and inventory_entry.id is null;
-- sales without client entries *untested*
select inventory_transaction.id from inventory_transaction left join (select * from inventory_entry where tipo='Client') as inventory_entry on inventory_entry.transaction_id=inventory_transaction.id where inventory_transaction.tipo='Sale' and inventory_entry.id is null;
-- sales with negative totals *untested*
select sum(value) from inventory_entry left join inventory_transaction on inventory_transaction.id=transaction_id where inventory_transaction.tipo='Sale'
-- purchases with negative totals

