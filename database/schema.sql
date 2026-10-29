-- =============================================================
-- Business Listings Dashboard - MySQL schema
-- =============================================================
-- Creates the database and the listing_master table required by
-- the assignment. Safe to run more than once (IF NOT EXISTS).
--
--   mysql -u root -p < database/schema.sql
-- =============================================================

CREATE DATABASE IF NOT EXISTS business_listings
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE business_listings;

CREATE TABLE IF NOT EXISTS listing_master (
    id             INT UNSIGNED  NOT NULL AUTO_INCREMENT,
    business_name  VARCHAR(255)  NOT NULL,
    category       VARCHAR(100)  NOT NULL,
    city           VARCHAR(100)  NOT NULL,
    address        VARCHAR(500)  NULL,
    phone          VARCHAR(30)   NULL,
    source         VARCHAR(50)   NOT NULL,
    -- SHA-256 of normalised (name | city | address). Lets MySQL reject
    -- duplicates without a huge composite index on long text columns.
    listing_hash   CHAR(64)      NOT NULL,
    created_at     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    UNIQUE KEY uq_listing_hash (listing_hash),
    -- The dashboard runs GROUP BY on these three columns
    KEY idx_city (city),
    KEY idx_category (category),
    KEY idx_source (source)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
