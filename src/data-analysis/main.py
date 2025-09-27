#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商機發現分析工具 - 主程式

提供簡化的入口點，使用新的分層架構
"""

import sys
import os
import logging
import warnings
from orchestration.workflows.analysis_workflow import AnalysisWorkflow

# 忽略所有警告
warnings.filterwarnings('ignore')

# 確保 output 目錄存在（於日誌設定前）
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(output_dir, 'analysis.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """主執行函數"""
    print(">> Manager 餐廳評論商機發現分析工具")
    print("=" * 50)

    try:
        # 初始化分析工作流程
        workflow = AnalysisWorkflow()

        # 執行完整分析流程
        success = workflow.run_complete_analysis()

        if success:
            print("\n>> 分析完成！請查看 output 目錄中的結果檔案。")
            return 0
        else:
            print("\n>> 分析過程中發生錯誤，請查看日誌了解詳情。")
            return 1

    except KeyboardInterrupt:
        print("\n>> 分析被使用者中斷")
        return 1
    except Exception as e:
        print(f"\n>> 程式執行錯誤: {e}")
        logger.error(f"程式執行錯誤: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())