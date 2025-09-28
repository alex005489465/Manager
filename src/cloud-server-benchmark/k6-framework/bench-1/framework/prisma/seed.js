const { PrismaClient } = require('@prisma/client');

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 開始初始化測試數據...');

  // 清理現有數據
  await prisma.benchmarkTest.deleteMany();

  console.log('🧹 清理舊數據完成');

  // 插入基本測試數據 (10萬條)
  console.log('⏳ 正在插入 100,000 筆測試數據...');

  const batchSize = 1000;
  const totalRecords = 100000;

  for (let batch = 0; batch < totalRecords / batchSize; batch++) {
    const benchmarkData = [];
    const startId = batch * batchSize + 1;

    for (let i = 0; i < batchSize; i++) {
      const id = startId + i;
      benchmarkData.push({
        name: `test_${id}`,
        value: id * 10,
      });
    }

    await prisma.benchmarkTest.createMany({
      data: benchmarkData,
    });

    if ((batch + 1) % 10 === 0) {
      console.log(`   進度: ${((batch + 1) * batchSize).toLocaleString()} / ${totalRecords.toLocaleString()} 筆`);
    }
  }

  console.log('✅ 基本測試數據插入完成 (100,000 筆)');

  // 統計結果
  const benchmarkCount = await prisma.benchmarkTest.count();

  console.log('📊 數據初始化摘要:');
  console.log(`   └── 基本測試數據: ${benchmarkCount} 筆`);

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