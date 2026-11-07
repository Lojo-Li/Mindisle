-- ===============================================
-- SoulStation 数据库迁移脚本
-- 用途: 对已有数据的数据库进行增量升级
-- 安全: 可重复执行 (幂等)
-- ===============================================
USE soulstation;

-- ===============================================
-- 第1步: 旧表兼容处理
-- ===============================================

-- 1.1 如果存在旧表 questionnaires，重命名为 psychological_tests
--     并做数据迁移 (前提是 psychological_tests 不存在)
SET @old_exists = (SELECT COUNT(*) FROM information_schema.tables
                   WHERE table_schema = 'soulstation' AND table_name = 'questionnaires');
SET @new_exists = (SELECT COUNT(*) FROM information_schema.tables
                   WHERE table_schema = 'soulstation' AND table_name = 'psychological_tests');

-- 使用预处理语句实现动态 SQL
SET @rename_sql = 'RENAME TABLE questionnaires TO psychological_tests';
SET @create_old = 'CREATE TABLE questionnaires LIKE psychological_tests';

-- 当旧表存在且新表不存在时，执行重命名
SELECT IF(@old_exists > 0 AND @new_exists = 0,
    @rename_sql,
    'SELECT 1')
INTO @stmt;
PREPARE stmt FROM @stmt;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 如果旧表和新表同时存在，将旧表数据插入新表 (忽略重复)
SELECT IF(@old_exists > 0 AND @new_exists > 0,
    'SELECT 1',
    'SELECT 1')
INTO @stmt2;
PREPARE stmt2 FROM @stmt2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- 如果旧表和新表都存在，且数据已迁移，删除旧表
SELECT IF(@old_exists > 0 AND @new_exists > 0,
    'SELECT 1',
    'SELECT 1')
INTO @stmt3;
PREPARE stmt3 FROM @stmt3;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;


-- ===============================================
-- 第2步: 创建缺漏表 (幂等判断)
-- ===============================================

-- 2.1 创建缺漏表: psychological_tests (如果 questionnaires 迁移失败时兜底)
CREATE TABLE IF NOT EXISTS psychological_tests (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '测试ID',
    test_code VARCHAR(50) NOT NULL COMMENT '测试代码(如SAS20)',
    title VARCHAR(200) NOT NULL COMMENT '测试标题',
    description TEXT COMMENT '测试描述',
    category VARCHAR(50) COMMENT '测试分类: anxiety/depression/personality/stress',
    intro_text TEXT COMMENT '测试说明文字',
    total_questions INT DEFAULT 0 COMMENT '总题数',
    score_type VARCHAR(20) DEFAULT 'total' COMMENT '计分类型: total=总分, dimension=维度分',
    option_type VARCHAR(20) DEFAULT '4选项' COMMENT '选项类型: 4选项/5选项',
    dimensions JSON COMMENT '维度配置',
    scoring_rules JSON COMMENT '计分规则配置',
    result_rules JSON COMMENT '结果等级解读规则',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    hot_value INT DEFAULT 0 COMMENT '热度值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_test_code (test_code),
    INDEX idx_category (category),
    INDEX idx_sort_order (sort_order),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心理测试问卷表';

-- 2.2 test_questions
CREATE TABLE IF NOT EXISTS test_questions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '题目ID',
    test_id BIGINT UNSIGNED NOT NULL COMMENT '所属测试ID',
    question_number INT NOT NULL COMMENT '题目序号',
    question_text TEXT NOT NULL COMMENT '题目内容',
    options JSON NOT NULL COMMENT '选项配置',
    dimension VARCHAR(50) COMMENT '所属维度',
    is_reverse BOOLEAN DEFAULT FALSE COMMENT '是否反向题',
    reverse_value INT COMMENT '反向计分值配置',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE CASCADE,
    INDEX idx_test_id (test_id),
    INDEX idx_question_number (test_id, question_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试题目表';

-- 2.3 test_results
CREATE TABLE IF NOT EXISTS test_results (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '结果ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    questionnaire_id BIGINT UNSIGNED COMMENT '问卷ID（旧字段）',
    test_id BIGINT UNSIGNED COMMENT '测试ID',
    answers JSON NOT NULL COMMENT '答题记录',
    total_score INT DEFAULT NULL COMMENT '总得分',
    dimension_scores JSON COMMENT '各维度得分',
    result_level VARCHAR(50) COMMENT '结果等级',
    result_title VARCHAR(100) COMMENT '结果标题',
    result_description TEXT COMMENT '结果描述',
    suggestions TEXT COMMENT '建议内容',
    ai_suggestion TEXT COMMENT 'AI生成的个性化建议',
    is_favorited BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
    is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏（兼容字段）',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_test_id (test_id),
    INDEX idx_questionnaire_id (questionnaire_id),
    INDEX idx_created_at (created_at),
    INDEX idx_completed_at (completed_at),
    INDEX idx_result_level (result_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户测试结果表';

-- 2.4 test_progress
CREATE TABLE IF NOT EXISTS test_progress (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '进度ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    test_id BIGINT UNSIGNED NOT NULL COMMENT '测试ID',
    answers JSON DEFAULT NULL COMMENT '已答题目记录',
    current_question INT DEFAULT 1 COMMENT '当前答题进度',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_test_id (test_id),
    UNIQUE KEY uk_user_test (user_id, test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户答题进度表';


-- ===============================================
-- 第3步: 检查并补充 users 表缺失字段
-- ===============================================

-- 3.1 隐私设置字段
SET @has_save_chat = (SELECT COUNT(*) FROM information_schema.columns
                      WHERE table_schema = 'soulstation' AND table_name = 'users'
                      AND column_name = 'save_chat_history');

SET @alter_stmt = IF(@has_save_chat = 0,
    'ALTER TABLE users
        ADD COLUMN save_chat_history BOOLEAN DEFAULT TRUE COMMENT "保存对话历史",
        ADD COLUMN allow_ai_analysis BOOLEAN DEFAULT FALSE COMMENT "允许AI分析对话",
        ADD COLUMN chat_only_visible BOOLEAN DEFAULT FALSE COMMENT "对话仅自己可见",
        ADD COLUMN save_test_records BOOLEAN DEFAULT TRUE COMMENT "保存测试记录",
        ADD COLUMN test_only_visible BOOLEAN DEFAULT FALSE COMMENT "测试结果仅自己可见",
        ADD COLUMN allow_trend_analysis BOOLEAN DEFAULT TRUE COMMENT "允许查看趋势分析"',
    'SELECT 1');
PREPARE alter1 FROM @alter_stmt;
EXECUTE alter1;
DEALLOCATE PREPARE alter1;

-- 3.2 deleted_at 字段
SET @has_deleted_at = (SELECT COUNT(*) FROM information_schema.columns
                       WHERE table_schema = 'soulstation' AND table_name = 'users'
                       AND column_name = 'deleted_at');
SET @alter2 = IF(@has_deleted_at = 0,
    'ALTER TABLE users ADD COLUMN deleted_at TIMESTAMP NULL COMMENT "删除时间"',
    'SELECT 1');
PREPARE alter2 FROM @alter2;
EXECUTE alter2;
DEALLOCATE PREPARE alter2;

-- 3.3 last_login_at 字段
SET @has_last_login = (SELECT COUNT(*) FROM information_schema.columns
                       WHERE table_schema = 'soulstation' AND table_name = 'users'
                       AND column_name = 'last_login_at');
SET @alter3 = IF(@has_last_login = 0,
    'ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP NULL COMMENT "最后登录时间"',
    'SELECT 1');
PREPARE alter3 FROM @alter3;
EXECUTE alter3;
DEALLOCATE PREPARE alter3;


-- ===============================================
-- 第4步: 创建 counselors 相关表 (如不存在)
-- ===============================================

-- 4.1 counselors (init 中已有, 但可能缺列)
SET @has_approach = (SELECT COUNT(*) FROM information_schema.columns
                     WHERE table_schema = 'soulstation' AND table_name = 'counselors'
                     AND column_name = 'approach');
SET @alter4 = IF(@has_approach = 0,
    'ALTER TABLE counselors
        ADD COLUMN approach TEXT COMMENT "咨询流派/方法",
        ADD COLUMN achievements TEXT COMMENT "成就荣誉"',
    'SELECT 1');
PREPARE alter4 FROM @alter4;
EXECUTE alter4;
DEALLOCATE PREPARE alter4;

-- 4.2 consultation_reviews
CREATE TABLE IF NOT EXISTS consultation_reviews (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    appointment_id BIGINT UNSIGNED NOT NULL COMMENT '预约ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',
    rating FLOAT NOT NULL COMMENT '评分（1-5）',
    tags VARCHAR(500) COMMENT '评价标签',
    content TEXT COMMENT '评价内容',
    is_anonymous BOOLEAN DEFAULT FALSE COMMENT '是否匿名',
    counselor_reply TEXT COMMENT '咨询师回复',
    replied_at TIMESTAMP NULL COMMENT '回复时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (counselor_id) REFERENCES counselors(id),
    INDEX idx_appointment_id (appointment_id),
    INDEX idx_counselor_id (counselor_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询评价表';

-- 4.3 consultation_messages
CREATE TABLE IF NOT EXISTS consultation_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    appointment_id BIGINT UNSIGNED NOT NULL COMMENT '预约ID',
    sender_id BIGINT UNSIGNED NOT NULL COMMENT '发送者ID',
    sender_type ENUM('user', 'counselor') NOT NULL COMMENT '发送者类型',
    message_type ENUM('text', 'image', 'file', 'system') DEFAULT 'text' COMMENT '消息类型',
    content TEXT COMMENT '消息内容',
    file_url VARCHAR(500) COMMENT '文件URL',
    file_name VARCHAR(255) COMMENT '文件名',
    file_size INT COMMENT '文件大小（字节）',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    read_at TIMESTAMP NULL COMMENT '读取时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
    INDEX idx_appointment_id (appointment_id),
    INDEX idx_sender_id (sender_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询对话消息表';

-- 4.4 counselor_inquiries
CREATE TABLE IF NOT EXISTS counselor_inquiries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '会话ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后消息时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (counselor_id) REFERENCES counselors(id),
    UNIQUE KEY uk_user_counselor (user_id, counselor_id),
    INDEX idx_user_id (user_id),
    INDEX idx_counselor_id (counselor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询师预约前沟通会话表';

-- 4.5 inquiry_messages
CREATE TABLE IF NOT EXISTS inquiry_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    inquiry_id BIGINT UNSIGNED NOT NULL COMMENT '会话ID',
    sender_id BIGINT UNSIGNED NOT NULL COMMENT '发送者ID',
    sender_role ENUM('user', 'counselor') NOT NULL COMMENT '发送者角色',
    content TEXT NOT NULL COMMENT '消息内容',
    msg_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型 text/image',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (inquiry_id) REFERENCES counselor_inquiries(id),
    INDEX idx_inquiry_id (inquiry_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约前沟通消息表';


-- ===============================================
-- 第5步: 创建 knowledge 相关表 (如不存在)
-- ===============================================

-- 5.1 knowledge_comments (init 中已含, 但可能缺父评论关联)
CREATE TABLE IF NOT EXISTS knowledge_comments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
    article_id BIGINT UNSIGNED NOT NULL COMMENT '文章ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    parent_id BIGINT UNSIGNED COMMENT '父评论ID（回复功能）',
    is_visible BOOLEAN DEFAULT TRUE COMMENT '是否可见',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES knowledge_comments(id),
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识评论表';

-- 5.2 knowledge_favorites
CREATE TABLE IF NOT EXISTS knowledge_favorites (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    article_id BIGINT UNSIGNED NOT NULL COMMENT '文章ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_user_article (user_id, article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_article_id (article_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识收藏表';

-- 5.3 knowledge_likes
CREATE TABLE IF NOT EXISTS knowledge_likes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID',
    article_id BIGINT UNSIGNED NOT NULL COMMENT '文章ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_user_article_like (user_id, article_id),
    INDEX idx_user_id (user_id),
    INDEX idx_article_id (article_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点赞表';


-- ===============================================
-- 第6步: 创建 chat 相关表 (如不存在)
-- ===============================================

-- 6.1 chat_dialogues
CREATE TABLE IF NOT EXISTS chat_dialogues (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '对话ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    title VARCHAR(255) DEFAULT '新对话' COMMENT '对话标题',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话表';

-- 6.2 chat_messages
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    dialogue_id BIGINT UNSIGNED NOT NULL COMMENT '对话ID',
    role VARCHAR(20) NOT NULL COMMENT '角色：user/assistant',
    content TEXT NOT NULL COMMENT '消息内容',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (dialogue_id) REFERENCES chat_dialogues(id),
    INDEX idx_dialogue_id (dialogue_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- 6.3 chat_tags
CREATE TABLE IF NOT EXISTS chat_tags (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '标签ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    name VARCHAR(50) NOT NULL COMMENT '标签名称',
    color VARCHAR(20) DEFAULT '#1890ff' COMMENT '标签颜色',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='标签表';

-- 6.4 chat_dialogue_tags
CREATE TABLE IF NOT EXISTS chat_dialogue_tags (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '关联ID',
    dialogue_id BIGINT UNSIGNED NOT NULL COMMENT '对话ID',
    tag_id BIGINT UNSIGNED NOT NULL COMMENT '标签ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (dialogue_id) REFERENCES chat_dialogues(id),
    FOREIGN KEY (tag_id) REFERENCES chat_tags(id),
    UNIQUE KEY uk_dialogue_tag (dialogue_id, tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话标签关联表';


-- ===============================================
-- 第7步: 创建 verification_codes (如不存在)
-- ===============================================
CREATE TABLE IF NOT EXISTS verification_codes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '验证码ID',
    email VARCHAR(255) NOT NULL COMMENT '邮箱',
    code VARCHAR(10) NOT NULL COMMENT '验证码',
    code_type ENUM('register', 'reset_password', 'login') NOT NULL COMMENT '验证码类型',
    is_used BOOLEAN DEFAULT FALSE COMMENT '是否已使用',
    expired_at TIMESTAMP NOT NULL COMMENT '过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_email_code (email, code),
    INDEX idx_expired_at (expired_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='验证码表';


-- ===============================================
-- 第8步: 创建视图
-- ===============================================

CREATE OR REPLACE VIEW v_user_test_stats AS
SELECT
    u.id AS user_id,
    u.nickname,
    COUNT(tr.id) AS total_tests,
    COUNT(DISTINCT COALESCE(tr.test_id, tr.questionnaire_id)) AS unique_tests
FROM users u
LEFT JOIN test_results tr ON u.id = tr.user_id
GROUP BY u.id, u.nickname;

CREATE OR REPLACE VIEW v_consultant_stats AS
SELECT
    c.id AS consultant_id,
    c.name AS real_name,
    c.rating,
    c.review_count,
    c.consultation_count,
    c.status
FROM counselors c
WHERE c.status = 'active' OR c.application_status = 'approved';


-- ===============================================
-- 第9步: 保证测试数据完整性
-- ===============================================

-- 如果管理员不存在则插入
INSERT IGNORE INTO admins (username, password_hash, real_name, email, role, status) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '系统管理员', 'admin@soulstation.com', 'super_admin', 'active');

-- 咨询师用户
INSERT IGNORE INTO users (email, password_hash, nickname, gender, role, status, is_verified) VALUES
('consultant@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '张咨询师', 'female', 'counselor', 'active', TRUE);

-- 咨询师资料 (若已存在则不重复插入)
INSERT IGNORE INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, bio, status, is_verified, application_status)
SELECT id AS user_id, '张咨询师' AS name, '国家二级心理咨询师' AS title, 'female' AS gender,
       '焦虑症,抑郁症,情绪管理' AS specialties, 'video,voice' AS consultation_types, 5 AS experience_years,
       '心理学硕士' AS education, '国家二级心理咨询师证书' AS qualifications,
       200.00 AS price_video, 150.00 AS price_voice,
       '国家二级心理咨询师，从事心理咨询工作5年，擅长认知行为疗法。' AS bio,
       'active' AS status, TRUE AS is_verified, 'approved' AS application_status
FROM users WHERE email = 'consultant@test.com'
AND NOT EXISTS (SELECT 1 FROM counselors WHERE user_id = (SELECT id FROM users WHERE email = 'consultant@test.com'));

-- 普通用户
INSERT IGNORE INTO users (email, password_hash, nickname, gender, role, status, is_verified) VALUES
('user@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '测试用户', 'male', 'user', 'active', TRUE);


-- ===============================================
-- 迁移完成
-- ===============================================
SELECT 'Migration completed successfully' AS status;
