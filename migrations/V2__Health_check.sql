
-- to OPTIMIZE and check health of table, this will be particularly helpful as table grows. OPTIMIZE will check for unused indices, reclaim unused disk space
-- Note: Since we're using an InnoDB engine instead of MyISAM, we will see message `Table does not support optimize, doing recreate + analyze instead` which will perform the equivalent for InnoDB tables.
OPTIMIZE TABLE STORAGE;
CHECK TABLE STORAGE;
