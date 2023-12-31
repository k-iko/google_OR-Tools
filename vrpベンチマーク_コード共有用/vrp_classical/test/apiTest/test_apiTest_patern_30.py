# -*- coding: utf-8 -*-
# !/usr/bin/env python3

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
#
# APIテスト環境
#

import sys
import os
import pprint

import json
import traceback
import random
import time
import datetime
import logging
from io import StringIO
import re
import numpy as np
import copy
import pytest
import test_apiTest_driver as driver

#-----------------------------------------------------------------
# テスト30(大量輸送モード bulk-shipping)
#-----------------------------------------------------------------
# 指定のないものは距離は1000、時間は1で固定、荷作業時間は1、配送時間枠は2000/1/1 9:00:00～2000/1/1 17:00:00で固定
# *但し拠点と最終訪問先の配送時間枠は1000/1/1 0:00:00～3000/1/1 0:00:00

test_args=[
    # ■正常系
    # 1. 車両数 : 1、配送先数 : 2(SPOTID 1、1)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→0または0→2→1→0(1と2はtie-up)となることを確認
    ('30_1_1', '30_1_1_request.json','2x2_cost.json', True),

    # 2. 車両数 : 2、配送先数 : 4(SPOTID 1、1、1、1、荷物量 全て120)、初期解生成モード、bulk-shippingモードとした場合に
    # 配送先が2つずつ(それぞれtie-up)となることを確認(積載量違反)
    ('30_1_2', '30_1_2_request.json','2x2_cost.json', True),

    # 3. 車両数 : 2、配送先数 : 4(SPOTID 1、1、1、1、第2荷物量 全て120)、初期解生成モード、bulk-shippingモードとした場合に
    # 配送先が2つずつ(それぞれtie-up)となることを確認(第2積載量違反)
    ('30_1_3', '30_1_3_request.json','2x2_cost.json', True),

    # 4. 車両数 : 2、配送先数 : 3(SPOTID 1、1、1、荷物量(第1および第2) 全て120)、初期解生成モード、bulk-shippingモードとした場合に
    # 配送先が2つと1つ(2つの方はtie-up)となることを確認(積載量違反、奇数拠点)
    ('30_1_4', '30_1_4_request.json','2x2_cost.json', True),

    # 5. 車両数 : 1、配送先数 : 2(SPOTID 1、1)、初期解 0→1→2→0、bulk-shippingモードとした場合に
    # 初期解のまま(1と2はtie-up)となることを確認(初期解入力)
    ('30_1_5', '30_1_5_request.json','2x2_cost.json', True),

    # 6. 車両数 : 1、配送先数 : 2(SPOTID 1、1、配送時間枠 2000/1/1 9:00:00～2000/1/1 10:00:00、2000/1/1 10:00:00～2000/1/1 11:00:00)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→0となることを確認(配送時間枠が異なる場合はtie-upしない)
    ('30_1_6', '30_1_6_request.json','2x2_cost.json', True),

    # 7. 車両数 : 1、配送先数 : 2(SPOTID 1、1、配送時間枠 2000/1/1 9:00:00～2000/1/1 10:00:00、2000/1/1 10:00:00～2000/1/1 11:00:00)、初期解 0→2→1→0、bulk-shippingモードとした場合に
    # 0→1→2→0となることを確認(配送時間枠が異なる場合はtie-upしない、初期解入力)
    ('30_1_7', '30_1_7_request.json','2x2_cost.json', True),

    # 8. 車両数 : 2、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 全て120(集荷))、初期解生成モード、bulk-shippingモードとした場合に
    # 配送先が2つずつ(それぞれtie-up)となることを確認(積載量違反、集荷)
    ('30_1_8', '30_1_8_request.json','2x2_cost.json', True),

    # 9. 車両数 : 1、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 120、120、120(集荷)、120(集荷))、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→3→4→0(1と2は順不同、3と4は順不同、1と2および3と4はtie-up)となることを確認(配送と集荷は別々にtie-up)
    ('30_1_9', '30_1_9_request.json','2x2_cost.json', True),

    # 10. 車両数 : 1、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 120、120、120(集荷)、120(集荷))、初期解 0→1→2→3→4→0、bulk-shippingモードとした場合に
    # 初期解のまま(1と2および3と4はtie-up)となることを確認(配送と集荷は別々にtie-up、初期解入力)
    ('30_1_10', '30_1_10_request.json','2x2_cost.json', True),

    # 11. 車両数 : 1、配送先数 : 3(SPOTID 1、1、2、配送時間枠 2000/1/1 9:00:00～2000/1/1 12:00:00、2000/1/1 9:00:00～2000/1/1 12:00:00、2000/1/1 15:00:00～2000/1/1 17:00:00)、初期解 0→1→3→2→0、bulk-shippingモードとした場合に
    # 0→1→2→3→0(1と2は順不同)となることを確認(初期解入力で連続していない場合はtie-upしない)
    ('30_1_11', '30_1_11_request.json','3x3_cost.json', True),

    # 12. 車両数 : 1、配送先数 : 4(SPOTID 1、1、1、1、荷物量 10、280、140(集荷)、140(集荷)、第2荷物量 280、10、140(集荷)、140(集荷))、初期解 0→1→3→2→4→0、bulk-shippingモードとした場合に
    # 0→1→2→3→4→0(1と2は順不同、3と4は順不同)となることを確認(配送(集荷)が連続していない場合はtie-upしない)
    ('30_1_12', '30_1_12_request.json','2x2_cost.json', True),

    # 13. 車両数 : 1、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 120、0、120(集荷)、120(集荷))、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→3→4→0(1と2は順不同、3と4は順不同、1と2および3と4はtie-up)となることを確認(配送と集荷は別々にtie-up、0は配送として扱う)
    ('30_1_13', '30_1_13_request.json','2x2_cost.json', True),

    # 14. 車両数 : 1、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 120、0、120(集荷)、120(集荷))、初期解 0→1→2→3→4→0、bulk-shippingモードとした場合に
    # 初期解のまま(1と2および3と4はtie-up)となることを確認(配送と集荷は別々にtie-up、初期解入力、0は配送として扱う)
    ('30_1_14', '30_1_14_request.json','2x2_cost.json', True),

    # 15. 車両数 : 1、配送先数 : 3(SPOTID 1、1、2、配送時間枠 2000/1/1 9:00:00～2000/1/1 17:00:00、2000/1/1 9:00:00～2000/1/1 17:00:00、2000/1/1 9:00:00～2000/1/1 12:00:00、
    # 荷作業時間 40、30、1、移動距離 2→1は10000)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→3→1→2→0または0→3→2→1→0(1と2はtie-up)となることを確認(荷作業時間は合計値となるため配送時間枠違反)
    ('30_1_15', '30_1_15_request.json','3x3_cost_30_1_15.json', True),

    # 16. 車両数 : 2、配送先数 : 4(SPOTID 1、1、1、1、荷物量(第1および第2) 400、50、50、50)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→0および0→2→3→4→0(2、3、4は順不同)となることを確認(積載量違反、分割できない場合)
    ('30_1_16', '30_1_16_request.json','2x2_cost.json', True),

    # 17. 車両数 : 2、配送先数 : 8(SPOTID 1、1、2、2、3、3、4、4、荷物量(第1および第2) 50、50、100(集荷)、100(集荷)、80(集荷)、80(集荷)、120(集荷)、120(集荷))、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→3→5→7→0および0→4→6→8→0(1と2はtie-upしない、3、5、7は順不同、4、6、8は順不同、3と4および5と6および7と8は交換可能)となることを確認(絶対値最大の荷物量を分割)
    ('30_1_17', '30_1_17_request.json','5x5_cost.json', True),

    # 18. 車両数 : 1、配送先数 : 2(SPOTID 1、1、荷物量(第1および第2) 全て200)、初期解 0→1→2→0、bulk-shippingモードとした場合に
    # 初期解のまま(1と2はtie-up)となることを確認(積載量違反、初期解入力)
    ('30_1_18', '30_1_18_request.json','2x2_cost.json', True),

    # 19. 車両数 : 2、配送先数 : 2(SPOTID 1、1)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→0および0→2→0となることを確認(tie-upすると初期解作成不可)
    ('30_1_19', '30_1_19_request.json','2x2_cost.json', True),

    # 20. 車両数 : 1、配送先数 : 3(SPOTID 1、1、2、0→2および2→0は通行不可)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→3→2→0となることを確認(1と2は順不同、tie-upすると初期解作成不可)
    ('30_1_20', '30_1_20_request.json','3x3_cost_30_1_20.json', True),

    # 21. 車両数 : 2、配送先数 : 8(SPOTID 1、1、2、2、3、3、4、4、荷物量 50、50、100(集荷)、100(集荷)、80(集荷)、80(集荷)、120(集荷)、120(集荷))、第2荷物量 250、250、100(集荷)、100(集荷)、80(集荷)、80(集荷)、120(集荷)、120(集荷))、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→3→5→7→0および0→2→4→6→8→0(1と2は交換可能、3、5、7は順不同、4、6、8は順不同、3と4および5と6および7と8は交換可能)となることを確認(第1および第2荷物量のうち絶対値最大の荷物量を分割)
    ('30_1_21', '30_1_21_request.json','5x5_cost.json', True),

    # 22. 車両数 : 3、配送先数 : 8(SPOTID 1、1、1、1、1、1、1、1、荷物量(第1および第2) 150、150、100、100、70、70、120、120)、初期解生成モード、bulk-shippingモードとした場合に
    # 0→1→2→0(直送便)および0→3→5→7→0および0→4→6→8→0(1と2はtie-up、3、5、7は順不同(tie-up)、4、6、8は順不同(tie-up)、3と4および5と6および7と8は交換可能)となることを確認(直送便+tie-up)
    ('30_1_22', '30_1_22_request.json','2x2_cost.json', True),

    # 23. 車両数 : 1、配送先数 : 2(SPOTID 1、1、最終訪問先 custno=3、spotid=1、最終訪問先の配送時間枠は2000/1/1 9:00:00～2000/1/1 17:00:00)、初期解 0→1→2→0、bulk-shippingモードとした場合に
    # 0→1→2→3(1と2はtie-up)となることを確認(最終訪問先はtie-upしない)
    ('30_1_23', '30_1_23_request.json','2x2_cost.json', True),
]
