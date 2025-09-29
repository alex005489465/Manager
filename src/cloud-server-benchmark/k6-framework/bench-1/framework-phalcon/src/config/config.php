<?php

use Phalcon\Config\Config;

return new Config([
    'database' => [
        'adapter'  => 'Mysql',
        'host'     => parse_url(getenv('DATABASE_URL'), PHP_URL_HOST) ?: 'localhost',
        'username' => parse_url(getenv('DATABASE_URL'), PHP_URL_USER) ?: 'root',
        'password' => parse_url(getenv('DATABASE_URL'), PHP_URL_PASS) ?: '',
        'dbname'   => ltrim(parse_url(getenv('DATABASE_URL'), PHP_URL_PATH) ?: '/benchmark', '/'),
        'port'     => parse_url(getenv('DATABASE_URL'), PHP_URL_PORT) ?: 3306,
        'charset'  => 'utf8mb4',
        'options'  => [
            \PDO::ATTR_TIMEOUT => 5,
            \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION,
            \PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        ]
    ],
    'application' => [
        'controllersDir' => __DIR__ . '/../controllers/',
        'modelsDir'      => __DIR__ . '/../models/',
        'baseUri'        => '/',
        'publicUrl'      => '/'
    ]
]);