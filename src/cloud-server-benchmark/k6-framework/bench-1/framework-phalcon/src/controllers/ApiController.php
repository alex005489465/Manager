<?php

namespace App\Controllers;

use Phalcon\Mvc\Controller;
use App\Models\BenchmarkTest;

class ApiController extends Controller
{
    public function healthAction()
    {
        $this->response->setContentType('application/json', 'UTF-8');
        $this->response->setJsonContent(['status' => 'OK']);
        return $this->response;
    }

    public function notFoundAction()
    {
        $this->response->setStatusCode(404, 'Not Found');
        $this->response->setContentType('application/json', 'UTF-8');
        $this->response->setJsonContent([
            'error' => 'Not found',
            'path' => $this->request->getURI(),
            'timestamp' => date('c')
        ]);
        return $this->response;
    }

    public function queryAction()
    {
        try {
            $this->response->setContentType('application/json', 'UTF-8');

            // 取得請求體資料
            $rawBody = $this->request->getRawBody();
            $requestData = json_decode($rawBody, true);

            // 生成請求 ID
            $requestId = substr(str_shuffle('0123456789abcdefghijklmnopqrstuvwxyz'), 0, 9);

            // 取得查詢 ID，如果沒有提供則使用隨機 ID
            $queryId = $requestData['id'] ?? (random_int(1, 100000));

            // 查詢資料庫
            $benchmarkData = BenchmarkTest::findFirst([
                'conditions' => 'id = :id:',
                'bind' => ['id' => $queryId]
            ]);

            $response = [
                'id' => $queryId,
                'found' => $benchmarkData !== null,
                'data' => $benchmarkData ? $benchmarkData->toArray() : null
            ];

            $this->response->setJsonContent($response);
            return $this->response;

        } catch (\Exception $error) {
            error_log('Database query error: ' . $error->getMessage());

            $this->response->setStatusCode(500, 'Internal Server Error');
            $this->response->setJsonContent([
                'error' => 'Database query failed',
                'id' => $queryId ?? null,
                'message' => $error->getMessage()
            ]);
            return $this->response;
        }
    }
}