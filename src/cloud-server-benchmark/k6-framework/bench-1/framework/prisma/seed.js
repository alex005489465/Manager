const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 開始初始化測試數據...');

  // 清理現有數據
  await prisma.requestLog.deleteMany();
  await prisma.testSession.deleteMany();
  await prisma.performanceData.deleteMany();
  await prisma.benchmarkTest.deleteMany();

  console.log('🧹 清理舊數據完成');

  // 插入基本測試數據
  const benchmarkData = [];
  for (let i = 1; i <= 10; i++) {
    benchmarkData.push({
      name: `test_${i}`,
      value: i * 100,
    });
  }

  await prisma.benchmarkTest.createMany({
    data: benchmarkData,
  });

  console.log('✅ 基本測試數據插入完成 (10 筆)');

  // 插入性能測試數據
  const performanceData = [];
  for (let i = 1; i <= 250; i++) {
    performanceData.push({
      category: `category_${(i % 10) + 1}`,
      dataValue: Math.round(Math.random() * 1000 * 100) / 100, // 保留兩位小數
      description: `Test data entry number ${i}`,
    });
  }

  await prisma.performanceData.createMany({
    data: performanceData,
  });

  console.log('✅ 性能測試數據插入完成 (250 筆)');

  // 創建測試會話範例
  const testSession = await prisma.testSession.create({
    data: {
      sessionName: 'initialization-test',
      startTime: new Date(),
      testType: 'setup',
      status: 'completed',
      metadata: {
        framework: 'express',
        database: 'mysql',
        orm: 'prisma',
        processManager: 'pm2',
        version: '1.0.0',
      },
    },
  });

  console.log('✅ 測試會話範例創建完成');

  // 統計結果
  const benchmarkCount = await prisma.benchmarkTest.count();
  const performanceCount = await prisma.performanceData.count();
  const sessionCount = await prisma.testSession.count();

  console.log('📊 數據初始化摘要:');
  console.log(`   ├── 基本測試數據: ${benchmarkCount} 筆`);
  console.log(`   ├── 性能測試數據: ${performanceCount} 筆`);
  console.log(`   └── 測試會話: ${sessionCount} 筆`);

  console.log('🎉 測試數據初始化完成！');
}

main()
  .catch((e) => {
    console.error('❌ 數據初始化失敗:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });