CREATE TABLE IF NOT EXISTS STORAGE (
    `namespace` VARCHAR(255) NOT NULL,
    `key` VARCHAR(255) NOT NULL,
    `value` VARCHAR(255) NOT NULL        
) ENGINE=InnoDB;                                 
-- InnoDB for enhanced performance, especially if expecting heavy concurrent reads and writes in the future


-- Creates index for faster lookups on (namespace, key)
CREATE INDEX idx_namespace_key ON STORAGE (`namespace`, `key`);
