-- ============================================================
-- SoulStation 统一种子数据
-- ============================================================
-- 密码均为 123456
-- BCrypt Hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i
-- ============================================================

USE soulstation;

-- ===============================================
-- 1. 管理员
-- ===============================================
INSERT INTO admins (username, password_hash, real_name, email, role, status) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '系统管理员', 'admin@soulstation.com', 'super_admin', 'active')
ON DUPLICATE KEY UPDATE username = VALUES(username);

-- ===============================================
-- 2. 用户账号 (普通用户 + 咨询师用户)
-- ===============================================
INSERT INTO users (email, password_hash, nickname, gender, role, status, is_verified) VALUES
('user1@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '小明', 'male', 'user', 'active', TRUE),
('user2@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '小红', 'female', 'user', 'active', TRUE),
('user3@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '小华', 'secret', 'user', 'active', TRUE),
('consultant@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '张咨询师', 'female', 'counselor', 'active', TRUE),
('counselor1@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '李医生', 'male', 'counselor', 'active', TRUE),
('counselor2@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '王老师', 'male', 'counselor', 'active', TRUE),
('counselor3@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '张医生', 'male', 'counselor', 'active', TRUE),
('counselor4@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '陈老师', 'female', 'counselor', 'active', TRUE),
('user@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '测试用户', 'male', 'user', 'active', TRUE)
ON DUPLICATE KEY UPDATE nickname = VALUES(nickname);

-- ===============================================
-- 3. 咨询师档案
-- ===============================================
INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, price_offline, rating, review_count, consultation_count, bio, approach, achievements, status, is_verified, application_status)
SELECT u.id, u.nickname, '国家二级心理咨询师', u.gender, '焦虑症,抑郁症,情绪管理', 'video,voice', 5, '心理学硕士', '国家二级心理咨询师证书', 200.00, 150.00, NULL, 4.5, 10, 50, '国家二级心理咨询师，从事心理咨询工作5年，擅长认知行为疗法。', '认知行为疗法(CBT)、人本主义疗法', NULL, 'active', TRUE, 'approved'
FROM users u WHERE u.email = 'consultant@test.com';

INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, price_offline, rating, review_count, consultation_count, bio, approach, achievements, status, is_verified, application_status)
SELECT u.id, '李医生', '心理咨询师', u.gender, '焦虑,抑郁,情绪管理', 'video,voice', 8, '心理学硕士', '国家二级心理咨询师', 300, 200, 500, 4.8, 120, 200, '拥有8年心理咨询经验，擅长焦虑、抑郁等情绪问题的咨询，采用认知行为疗法。', '认知行为疗法(CBT)、人本主义疗法', '帮助超过200名来访者走出心理困境', 'active', TRUE, 'approved'
FROM users u WHERE u.email = 'counselor1@test.com';

INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, price_offline, rating, review_count, consultation_count, bio, approach, achievements, status, is_verified, application_status)
SELECT u.id, '王老师', '高级心理咨询师', u.gender, '婚恋家庭,亲子关系,职业规划', 'video,voice,offline', 12, '心理学博士', '国家二级心理咨询师、婚姻家庭咨询师', 500, 300, 800, 4.9, 280, 450, '12年心理咨询经验，专注于婚恋家庭、亲子关系咨询，拥有丰富的家庭治疗经验。', '家庭治疗、系统式家庭治疗、沙盘疗法', '出版心理学著作3部，举办讲座100余场', 'active', TRUE, 'approved'
FROM users u WHERE u.email = 'counselor2@test.com';

INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, price_offline, rating, review_count, consultation_count, bio, approach, achievements, status, is_verified, application_status)
SELECT u.id, '张医生', '资深心理医生', u.gender, '青少年心理,学习压力,网络成瘾', 'video,voice', 15, '精神医学硕士', '精神科医师、国家二级心理咨询师', 400, 250, 600, 4.7, 180, 320, '15年青少年心理咨询经验，擅长处理学习压力、网络成瘾、青春期心理问题。', '认知行为疗法、家庭治疗、游戏治疗', '治疗成功案例超过500例', 'active', TRUE, 'approved'
FROM users u WHERE u.email = 'counselor3@test.com';

INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, price_offline, rating, review_count, consultation_count, bio, approach, achievements, status, is_verified, application_status)
SELECT u.id, '陈老师', '心理咨询师', u.gender, '情绪管理,压力调节,自我成长', 'video,voice', 6, '应用心理学硕士', '国家二级心理咨询师', 300, 200, 400, 4.6, 85, 150, '6年心理咨询经验，温暖专业，帮助来访者实现自我成长。', '人本主义疗法、正念疗法', '获得"优秀心理咨询师"称号', 'active', TRUE, 'approved'
FROM users u WHERE u.email = 'counselor4@test.com';

-- ===============================================
-- 完成
-- ===============================================
SELECT '========================================' AS '';
SELECT '✓ 种子数据插入完成！' AS '';
SELECT '========================================' AS '';
