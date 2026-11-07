-- SoulStation 心理测试数据初始化SQL脚本
-- 使用方法：mysql -u root -p123456 soulstation < init_tests.sql

-- ============================================
-- 1. 插入测试基础数据
-- ============================================

-- 焦虑自评量表 (SAS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value, created_at, updated_at) VALUES
('SAS20', '焦虑自评量表 (SAS-20)', '焦虑自评量表（Self-Rating Anxiety Scale，SAS）是由Zung于1971年编制的，用于评估焦虑程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的焦虑水平。', 'anxiety', '本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"躯体性焦虑": {"questions": [2, 4, 6, 8, 9, 10, 12, 14]}, "精神性焦虑": {"questions": [1, 3, 5, 7, 11, 13, 15, 16, 17, 18, 19, 20]}}, "reverse_questions": [5, 9, 13, 17, 19]}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无焦虑", "desc": "情绪状态良好，无明显焦虑表现"}, "mild": {"min": 31, "max": 45, "title": "轻度焦虑", "desc": "偶尔出现焦虑表现，不影响日常工作与生活"}, "moderate": {"min": 46, "max": 60, "title": "中度焦虑", "desc": "频繁出现焦虑表现，对日常工作与生活有一定影响"}, "severe": {"min": 61, "max": 80, "title": "重度焦虑", "desc": "持续出现严重焦虑表现，严重影响日常工作与生活，建议寻求专业心理咨询"}}}',
1, 1, 100, NOW(), NOW());

-- 获取刚才插入的测试ID
SET @sas_test_id = LAST_INSERT_ID();

-- 插入SAS的20道题目
INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order, created_at) VALUES
(@sas_test_id, 1, '我感到比往常更加神经过敏和焦虑', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 1, NOW()),
(@sas_test_id, 2, '我无缘无故感到担心', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 2, NOW()),
(@sas_test_id, 3, '我容易心烦意乱或感到恐慌', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 3, NOW()),
(@sas_test_id, 4, '我感到身体疲乏无力', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 4, NOW()),
(@sas_test_id, 5, '我感到平静，能安静坐着', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 1, 5, NOW()),
(@sas_test_id, 6, '我感到心跳加快或呼吸不畅', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 6, NOW()),
(@sas_test_id, 7, '我感到头痛或胃痛', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 7, NOW()),
(@sas_test_id, 8, '我感到手脚麻木或刺痛', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 8, NOW()),
(@sas_test_id, 9, '我感到平静和放松', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 1, 9, NOW()),
(@sas_test_id, 10, '我感到尿频或排便频繁', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 10, NOW()),
(@sas_test_id, 11, '我感到害怕，好像有什么可怕的事情发生', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 11, NOW()),
(@sas_test_id, 12, '我感到手脚发抖或颤抖', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 12, NOW()),
(@sas_test_id, 13, '我感到自信和愉快', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 1, 13, NOW()),
(@sas_test_id, 14, '我感到容易入睡和睡眠安稳', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', 0, 14, NOW()),
(@sas_test_id, 15, '我感到做噩梦或惊醒', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 15, NOW()),
(@sas_test_id, 16, '我感到面部潮红或发热', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 16, NOW()),
(@sas_test_id, 17, '我感到高兴和愉快', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 1, 17, NOW()),
(@sas_test_id, 18, '我感到口干舌燥', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 18, NOW()),
(@sas_test_id, 19, '我感到事情都在我的掌控之中', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 1, 19, NOW()),
(@sas_test_id, 20, '我感到难以集中注意力', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', 0, 20, NOW());

-- 抑郁自评量表 (SDS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value, created_at, updated_at) VALUES
('SDS20', '抑郁自评量表 (SDS-20)', '抑郁自评量表（Self-Rating Depression Scale，SDS）是由Zung于1965年编制的，用于评估抑郁程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的抑郁水平。', 'depression', '本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"情绪低落": {"questions": [1, 3, 5, 7, 9, 15, 17, 19]}, "兴趣减退": {"questions": [2, 4, 6, 11, 14]}, "躯体症状": {"questions": [8, 10, 12, 13, 16, 18, 20]}}, "reverse_questions": [2, 5, 6, 11, 12, 14, 16, 17, 18, 20]}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无抑郁", "desc": "情绪状态良好，无明显抑郁表现"}, "mild": {"min": 31, "max": 45, "title": "轻度抑郁", "desc": "偶尔出现抑郁表现，可通过自我调节缓解"}, "moderate": {"min": 46, "max": 60, "title": "中度抑郁", "desc": "频繁出现抑郁表现，自我调节效果有限，建议寻求心理疏导"}, "severe": {"min": 61, "max": 80, "title": "重度抑郁", "desc": "持续出现严重抑郁表现，影响正常生活，需及时寻求专业心理咨询与治疗"}}}',
2, 1, 95, NOW(), NOW());

SET @sds_test_id = LAST_INSERT_ID();

-- 为节省篇幅，这里只演示插入前5题，完整的20题可以在init_test_data.py中找到
INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order, created_at) VALUES
(@sds_test_id, 1, '我感到情绪沮丧，郁闷', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', 0, 1, NOW()),
(@sds_test_id, 2, '我感到早晨心情最好', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', 1, 2, NOW()),
(@sds_test_id, 3, '我要哭或想哭', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', 0, 3, NOW()),
(@sds_test_id, 4, '我夜间睡眠不好', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', 0, 4, NOW()),
(@sds_test_id, 5, '我吃饭像平时一样多', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', 1, 5, NOW());

-- 大五人格简版量表 (BIG5-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value, created_at, updated_at) VALUES
('BIG5_20', '大五人格简版量表 (20题)', '大五人格量表（Big Five Inventory）是国际公认的人格测评工具，从开放性、责任心、外倾性、宜人性、神经质五个维度全面评估人格特质。本版本为20题简版，快速准确地了解您的人格特征。', 'personality', '本测试共20题，每题有5个选项。请根据您的真实情况，选择最符合的选项。', 20, 'dimension', '5选项',
'{"type": "dimension_sum", "dimensions": {"开放性(O)": {"questions": {"1": false, "6": false, "11": false, "16": true}}, "责任心(C)": {"questions": {"2": false, "7": false, "12": false, "17": true}}, "外倾性(E)": {"questions": {"3": false, "8": false, "13": false, "18": true}}, "宜人性(A)": {"questions": {"4": false, "9": false, "14": false, "19": true}}, "神经质(N)": {"questions": {"5": false, "10": false, "15": false, "20": true}}}}',
'{"levels": {"low": {"min": 4, "max": 8, "desc": "该维度人格特质极不明显"}, "medium": {"min": 9, "max": 16, "desc": "该维度人格特质中等，表现均衡"}, "high": {"min": 17, "max": 20, "desc": "该维度人格特质非常明显"}}}',
3, 1, 80, NOW(), NOW());

SET @big5_test_id = LAST_INSERT_ID();

-- 插入前5题
INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order, created_at) VALUES
(@big5_test_id, 1, '我喜欢尝试新的食物和旅行', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '开放性', 0, 1, NOW()),
(@big5_test_id, 2, '我做事总是有条不紊', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '责任心', 0, 2, NOW()),
(@big5_test_id, 3, '我善于与人交谈', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '外倾性', 0, 3, NOW()),
(@big5_test_id, 4, '我倾向于信任他人', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '宜人性', 0, 4, NOW()),
(@big5_test_id, 5, '我容易紧张和焦虑', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '神经质', 0, 5, NOW());

-- 工作生活压力量表 (STRESS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value, created_at, updated_at) VALUES
('STRESS20', '工作生活压力量表 (20题)', '工作生活压力量表用于全面评估个体在工作/学习、生活、人际关系三大维度的压力状况，帮助识别压力来源并采取有效的应对措施。', 'stress', '本测试共20题，每题有4个选项。请根据您最近一个月的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"工作/学习压力": {"questions": [1, 4, 7, 10, 13, 16, 19]}, "生活压力": {"questions": [2, 5, 8, 11, 14, 17]}, "人际关系压力": {"questions": [3, 6, 9, 12, 15, 18, 20]}, "reverse_questions": []}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无压力", "desc": "整体状态轻松，各方面无明显压力，身心状态良好"}, "mild": {"min": 31, "max": 45, "title": "轻微压力", "desc": "偶尔出现压力表现，可通过自我调节（如运动、休息）快速缓解"}, "moderate": {"min": 46, "max": 60, "title": "中度压力", "desc": "频繁感受到压力，对日常工作/生活有一定影响，需通过合理的方式疏导压力"}, "severe": {"min": 61, "max": 80, "title": "重度压力", "desc": "长期处于高压状态，身心俱疲，严重影响工作/生活与人际关系，建议寻求心理疏导与压力调节指导"}}}',
4, 1, 85, NOW(), NOW());

SET @stress_test_id = LAST_INSERT_ID();

-- 插入前5题
INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order, created_at) VALUES
(@stress_test_id, 1, '工作任务/学习负担过重', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', 0, 1, NOW()),
(@stress_test_id, 2, '经济状况紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', 0, 2, NOW()),
(@stress_test_id, 3, '与家人关系紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', 0, 3, NOW()),
(@stress_test_id, 4, '工作/学习时间过长', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', 0, 4, NOW()),
(@stress_test_id, 5, '家务负担过重', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', 0, 5, NOW());

-- 验证插入结果
SELECT
    test_code AS '测试代码',
    title AS '测试名称',
    total_questions AS '题目数量',
    hot_value AS '热度值'
FROM psychological_tests
ORDER BY sort_order;

SELECT
    COUNT(*) AS '总测试套数'
FROM psychological_tests;

SELECT
    COUNT(*) AS '总题目数'
FROM test_questions;
