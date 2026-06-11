-- Создаю базу wallets
CREATE DATABASE "wallets"
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LOCALE_PROVIDER = 'libc'
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Создаю таблицу alembic_version
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32)
);

-- Гарантирую, что таблица пустая
TRUNCATE alembic_version;