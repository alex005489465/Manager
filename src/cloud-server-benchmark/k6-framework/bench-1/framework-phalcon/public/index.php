<?php

use Phalcon\Di\FactoryDefault;
use Phalcon\Mvc\Application;
use Phalcon\Mvc\Router;
use Phalcon\Db\Adapter\Pdo\Mysql;
use Phalcon\Config\Config;

error_reporting(E_ALL);

define('BASE_PATH', dirname(__DIR__));
define('APP_PATH', BASE_PATH . '/src');

try {
    // 自動載入器
    require_once BASE_PATH . '/vendor/autoload.php';

    // DI 容器
    $di = new FactoryDefault();

    // 載入配置
    $config = include APP_PATH . '/config/config.php';
    $di->setShared('config', $config);

    // 設定資料庫連接
    $di->setShared('db', function () use ($config) {
        return new Mysql([
            'host'     => $config->database->host,
            'username' => $config->database->username,
            'password' => $config->database->password,
            'dbname'   => $config->database->dbname,
            'port'     => $config->database->port,
            'charset'  => $config->database->charset,
            'options'  => $config->database->options->toArray()
        ]);
    });

    // 路由設定
    $di->setShared('router', function () {
        $router = new Router(false);

        // 移除尾部斜線
        $router->removeExtraSlashes(true);

        // API 路由
        $router->addPost('/api/health', [
            'controller' => 'Api',
            'action'     => 'health'
        ]);

        $router->addPost('/api/query', [
            'controller' => 'Api',
            'action'     => 'query'
        ]);

        // 404 處理
        $router->notFound([
            'controller' => 'Api',
            'action'     => 'notFound'
        ]);

        return $router;
    });

    // 控制器處理 404
    $di->setShared('dispatcher', function () {
        $dispatcher = new \Phalcon\Mvc\Dispatcher();

        $dispatcher->setDefaultNamespace('App\\Controllers');

        // 404 錯誤處理
        $eventsManager = new \Phalcon\Events\Manager();
        $eventsManager->attach('dispatch:beforeException', function ($event, $dispatcher, $exception) {
            if ($exception instanceof \Phalcon\Mvc\Dispatcher\Exception) {
                $dispatcher->forward([
                    'controller' => 'Api',
                    'action'     => 'notFound'
                ]);
                return false;
            }
            return true;
        });

        $dispatcher->setEventsManager($eventsManager);
        return $dispatcher;
    });

    // 應用程式
    $application = new Application($di);

    // 處理請求
    echo $application->handle($_SERVER['REQUEST_URI'])->getContent();

} catch (\Exception $e) {
    // 錯誤處理
    error_log('Application error: ' . $e->getMessage());

    http_response_code(500);
    header('Content-Type: application/json');
    echo json_encode([
        'error' => 'Internal server error',
        'timestamp' => date('c')
    ]);
}