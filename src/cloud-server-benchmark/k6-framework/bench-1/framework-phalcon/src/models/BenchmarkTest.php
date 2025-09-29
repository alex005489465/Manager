<?php

namespace App\Models;

use Phalcon\Mvc\Model;

class BenchmarkTest extends Model
{
    public int $id;
    public string $name;
    public int $value;
    public string $timestamp;

    public function initialize()
    {
        $this->setSource('benchmark_test');
    }

    public function getSource(): string
    {
        return 'benchmark_test';
    }
}