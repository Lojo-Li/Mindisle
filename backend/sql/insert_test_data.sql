-- ===============================================
-- 心理测试数据插入脚本
-- 使用方法：mysql -u root -p123456 soulstation < insert_test_data.sql
-- ===============================================

USE soulstation;

-- 1. 焦虑自评量表 (SAS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value) VALUES
('SAS20', '焦虑自评量表 (SAS-20)', '焦虑自评量表（Self-Rating Anxiety Scale，SAS）是由Zung于1971年编制的，用于评估焦虑程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的焦虑水平。', 'anxiety', '本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"躯体性焦虑": {"questions": [2, 4, 6, 8, 9, 10, 12, 14]}, "精神性焦虑": {"questions": [1, 3, 5, 7, 11, 13, 15, 16, 17, 18, 19, 20]}}, "reverse_questions": [5, 9, 13, 17, 19]}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无焦虑", "desc": "情绪状态良好，无明显焦虑表现"}, "mild": {"min": 31, "max": 45, "title": "轻度焦虑", "desc": "偶尔出现焦虑表现，不影响日常工作与生活"}, "moderate": {"min": 46, "max": 60, "title": "中度焦虑", "desc": "频繁出现焦虑表现，对日常工作与生活有一定影响"}, "severe": {"min": 61, "max": 80, "title": "重度焦虑", "desc": "持续出现严重焦虑表现，严重影响日常工作与生活，建议寻求专业心理咨询"}}}',
1, TRUE, 100);

SET @sas_test_id = LAST_INSERT_ID();

INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order) VALUES
(@sas_test_id, 1, '我感到比往常更加神经过敏和焦虑', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 1),
(@sas_test_id, 2, '我无缘无故感到担心', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 2),
(@sas_test_id, 3, '我容易心烦意乱或感到恐慌', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 3),
(@sas_test_id, 4, '我感到身体疲乏无力', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 4),
(@sas_test_id, 5, '我感到平静，能安静坐着', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', TRUE, 5),
(@sas_test_id, 6, '我感到心跳加快或呼吸不畅', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 6),
(@sas_test_id, 7, '我感到头痛或胃痛', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 7),
(@sas_test_id, 8, '我感到手脚麻木或刺痛', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 8),
(@sas_test_id, 9, '我感到平静和放松', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', TRUE, 9),
(@sas_test_id, 10, '我感到尿频或排便频繁', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 10),
(@sas_test_id, 11, '我感到害怕，好像有什么可怕的事情发生', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 11),
(@sas_test_id, 12, '我感到手脚发抖或颤抖', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 12),
(@sas_test_id, 13, '我感到自信和愉快', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', TRUE, 13),
(@sas_test_id, 14, '我感到容易入睡和睡眠安稳', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体性焦虑', FALSE, 14),
(@sas_test_id, 15, '我感到做噩梦或惊醒', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 15),
(@sas_test_id, 16, '我感到面部潮红或发热', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 16),
(@sas_test_id, 17, '我感到高兴和愉快', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', TRUE, 17),
(@sas_test_id, 18, '我感到口干舌燥', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 18),
(@sas_test_id, 19, '我感到事情都在我的掌控之中', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', TRUE, 19),
(@sas_test_id, 20, '我感到难以集中注意力', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '精神性焦虑', FALSE, 20);

-- 2. 抑郁自评量表 (SDS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value) VALUES
('SDS20', '抑郁自评量表 (SDS-20)', '抑郁自评量表（Self-Rating Depression Scale，SDS）是由Zung于1965年编制的，用于评估抑郁程度的自评工具。本版本为20题简化版，能够快速有效地评估个体的抑郁水平。', 'depression', '本测试共20题，每题有4个选项。请根据您最近一周的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"情绪低落": {"questions": [1, 3, 5, 7, 9, 15, 17, 19]}, "兴趣减退": {"questions": [2, 4, 6, 11, 14]}, "躯体症状": {"questions": [8, 10, 12, 13, 16, 18, 20]}}, "reverse_questions": [2, 5, 6, 11, 12, 14, 16, 17, 18, 20]}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无抑郁", "desc": "情绪状态良好，无明显抑郁表现"}, "mild": {"min": 31, "max": 45, "title": "轻度抑郁", "desc": "偶尔出现抑郁表现，可通过自我调节缓解"}, "moderate": {"min": 46, "max": 60, "title": "中度抑郁", "desc": "频繁出现抑郁表现，自我调节效果有限，建议寻求心理疏导"}, "severe": {"min": 61, "max": 80, "title": "重度抑郁", "desc": "持续出现严重抑郁表现，影响正常生活，需及时寻求专业心理咨询与治疗"}}}',
2, TRUE, 95);

SET @sds_test_id = LAST_INSERT_ID();

INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order) VALUES
(@sds_test_id, 1, '我感到情绪沮丧，郁闷', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 1),
(@sds_test_id, 2, '我感到早晨心情最好', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', TRUE, 2),
(@sds_test_id, 3, '我要哭或想哭', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 3),
(@sds_test_id, 4, '我夜间睡眠不好', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', FALSE, 4),
(@sds_test_id, 5, '我吃饭像平时一样多', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', TRUE, 5),
(@sds_test_id, 6, '我的性功能正常', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', TRUE, 6),
(@sds_test_id, 7, '我感到体重减轻', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 7),
(@sds_test_id, 8, '我为便秘烦恼', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', FALSE, 8),
(@sds_test_id, 9, '我的心跳比平时快', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 9),
(@sds_test_id, 10, '我无故感到疲劳', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', FALSE, 10),
(@sds_test_id, 11, '我的头脑像往常一样清楚', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', TRUE, 11),
(@sds_test_id, 12, '我做事情像平时一样不感到困难', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', TRUE, 12),
(@sds_test_id, 13, '我坐卧不安，难以保持平静', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', FALSE, 13),
(@sds_test_id, 14, '我对未来感到有希望', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '兴趣减退', TRUE, 14),
(@sds_test_id, 15, '我比平时更容易激怒', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 15),
(@sds_test_id, 16, '我觉得决定什么事很容易', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', TRUE, 16),
(@sds_test_id, 17, '我感到自己是有用的和不可缺少的人', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', TRUE, 17),
(@sds_test_id, 18, '我的生活很有意义', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', TRUE, 18),
(@sds_test_id, 19, '我感到若是我死了别人会过得更好', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '情绪低落', FALSE, 19),
(@sds_test_id, 20, '我依旧喜爱平时喜爱的事物', '[{"value": 1, "label": "完全没有"}, {"value": 2, "label": "偶尔出现"}, {"value": 3, "label": "经常出现"}, {"value": 4, "label": "总是出现"}]', '躯体症状', TRUE, 20);

-- 3. 大五人格简版量表 (BIG5-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value) VALUES
('BIG5_20', '大五人格简版量表 (20题)', '大五人格量表（Big Five Inventory）是国际公认的人格测评工具，从开放性、责任心、外倾性、宜人性、神经质五个维度全面评估人格特质。本版本为20题简版，快速准确地了解您的人格特征。', 'personality', '本测试共20题，每题有5个选项。请根据您的真实情况，选择最符合的选项。', 20, 'dimension', '5选项',
'{"type": "dimension_sum", "dimensions": {"开放性(O)": {"questions": {"1": false, "6": false, "11": false, "16": true}}, "责任心(C)": {"questions": {"2": false, "7": false, "12": false, "17": true}}, "外倾性(E)": {"questions": {"3": false, "8": false, "13": false, "18": true}}, "宜人性(A)": {"questions": {"4": false, "9": false, "14": false, "19": true}}, "神经质(N)": {"questions": {"5": false, "10": false, "15": false, "20": true}}}}',
'{"levels": {"low": {"min": 4, "max": 8, "desc": "该维度人格特质极不明显"}, "medium": {"min": 9, "max": 16, "desc": "该维度人格特质中等，表现均衡"}, "high": {"min": 17, "max": 20, "desc": "该维度人格特质非常明显"}}}',
3, TRUE, 80);

SET @big5_test_id = LAST_INSERT_ID();

INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order) VALUES
(@big5_test_id, 1, '我喜欢尝试新的食物和旅行', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '开放性', FALSE, 1),
(@big5_test_id, 2, '我做事总是有条不紊', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '责任心', FALSE, 2),
(@big5_test_id, 3, '我善于与人交谈', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '外倾性', FALSE, 3),
(@big5_test_id, 4, '我倾向于信任他人', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '宜人性', FALSE, 4),
(@big5_test_id, 5, '我容易紧张和焦虑', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '神经质', FALSE, 5),
(@big5_test_id, 6, '我对抽象概念感兴趣', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '开放性', FALSE, 6),
(@big5_test_id, 7, '我做事总是尽心尽力', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '责任心', FALSE, 7),
(@big5_test_id, 8, '我能在社交场合中活跃气氛', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '外倾性', FALSE, 8),
(@big5_test_id, 9, '我乐于帮助他人', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '宜人性', FALSE, 9),
(@big5_test_id, 10, '我情绪波动较大', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '神经质', FALSE, 10),
(@big5_test_id, 11, '我喜欢思考复杂的理论问题', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '开放性', FALSE, 11),
(@big5_test_id, 12, '我做事总是会提前计划', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '责任心', FALSE, 12),
(@big5_test_id, 13, '我喜欢与人打交道', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '外倾性', FALSE, 13),
(@big5_test_id, 14, '我容易体谅他人的感受', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '宜人性', FALSE, 14),
(@big5_test_id, 15, '我容易感到沮丧', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '神经质', FALSE, 15),
(@big5_test_id, 16, '我更喜欢熟悉的事物而非新事物', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '开放性', TRUE, 16),
(@big5_test_id, 17, '我做事比较随意，不太注重细节', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '责任心', TRUE, 17),
(@big5_test_id, 18, '我更喜欢独处而非社交', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '外倾性', TRUE, 18),
(@big5_test_id, 19, '我倾向于怀疑他人的动机', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '宜人性', TRUE, 19),
(@big5_test_id, 20, '我的情绪非常稳定', '[{"value": 1, "label": "完全不符合"}, {"value": 2, "label": "不太符合"}, {"value": 3, "label": "一般"}, {"value": 4, "label": "比较符合"}, {"value": 5, "label": "完全符合"}]', '神经质', TRUE, 20);

-- 4. 工作生活压力量表 (STRESS-20)
INSERT INTO psychological_tests (test_code, title, description, category, intro_text, total_questions, score_type, option_type, scoring_rules, result_rules, sort_order, is_active, hot_value) VALUES
('STRESS20', '工作生活压力量表 (20题)', '工作生活压力量表用于全面评估个体在工作/学习、生活、人际关系三大维度的压力状况，帮助识别压力来源并采取有效的应对措施。', 'stress', '本测试共20题，每题有4个选项。请根据您最近一个月的实际感受，选择最符合的选项。', 20, 'total', '4选项',
'{"type": "sum_with_dimensions", "dimensions": {"工作/学习压力": {"questions": [1, 4, 7, 10, 13, 16, 19]}, "生活压力": {"questions": [2, 5, 8, 11, 14, 17]}, "人际关系压力": {"questions": [3, 6, 9, 12, 15, 18, 20]}}, "reverse_questions": []}',
'{"levels": {"none": {"min": 20, "max": 30, "title": "无压力", "desc": "整体状态轻松，各方面无明显压力，身心状态良好"}, "mild": {"min": 31, "max": 45, "title": "轻微压力", "desc": "偶尔出现压力表现，可通过自我调节（如运动、休息）快速缓解"}, "moderate": {"min": 46, "max": 60, "title": "中度压力", "desc": "频繁感受到压力，对日常工作/生活有一定影响，需通过合理的方式疏导压力"}, "severe": {"min": 61, "max": 80, "title": "重度压力", "desc": "长期处于高压状态，身心俱疲，严重影响工作/生活与人际关系，建议寻求心理疏导与压力调节指导"}}}',
4, TRUE, 85);

SET @stress_test_id = LAST_INSERT_ID();

INSERT INTO test_questions (test_id, question_number, question_text, options, dimension, is_reverse, sort_order) VALUES
(@stress_test_id, 1, '工作任务/学习负担过重', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 1),
(@stress_test_id, 2, '经济状况紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 2),
(@stress_test_id, 3, '与家人关系紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 3),
(@stress_test_id, 4, '工作/学习时间过长', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 4),
(@stress_test_id, 5, '家务负担过重', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 5),
(@stress_test_id, 6, '与同事/同学关系紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 6),
(@stress_test_id, 7, '对工作/学习表现感到焦虑', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 7),
(@stress_test_id, 8, '照顾家庭责任过重', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 8),
(@stress_test_id, 9, '社交压力较大', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 9),
(@stress_test_id, 10, '面临职业/学业发展压力', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 10),
(@stress_test_id, 11, '居住环境不佳', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 11),
(@stress_test_id, 12, '与伴侣/配偶关系紧张', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 12),
(@stress_test_id, 13, '工作/学习目标不明确', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 13),
(@stress_test_id, 14, '缺乏个人时间', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 14),
(@stress_test_id, 15, '感到孤独或被排斥', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 15),
(@stress_test_id, 16, '担心工作/学习稳定性', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 16),
(@stress_test_id, 17, '家庭期望过高', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '生活压力', FALSE, 17),
(@stress_test_id, 18, '人际冲突处理困难', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 18),
(@stress_test_id, 19, '工作/学习与生活平衡困难', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '工作/学习压力', FALSE, 19),
(@stress_test_id, 20, '缺乏社会支持系统', '[{"value": 1, "label": "无压力"}, {"value": 2, "label": "轻微压力"}, {"value": 3, "label": "中度压力"}, {"value": 4, "label": "重度压力"}]', '人际关系压力', FALSE, 20);

-- ===============================================
-- 验证插入结果
-- ===============================================
SELECT '========================================' AS '';
SELECT '✓ 心理测试数据初始化完成！' AS '';
SELECT '========================================' AS '';
SELECT
    test_code AS '测试代码',
    title AS '测试名称',
    total_questions AS '题目数量',
    category AS '分类'
FROM psychological_tests
ORDER BY sort_order;

SELECT
    COUNT(*) AS '总测试套数'
FROM psychological_tests;

SELECT
    COUNT(*) AS '总题目数'
FROM test_questions;
