-- ===============================================
-- SoulStation 心理咨询服务平台数据库初始化脚本
-- 完全匹配 Python SQLAlchemy 模型定义
-- 数据库: soulstation
-- 版本: 2.0 (模型对齐版)
-- ===============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS soulstation DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE soulstation;

-- ===============================================
-- 1. 用户表 (模型: app.models.user.User → users)
-- ===============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    email VARCHAR(255) NOT NULL UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(100) DEFAULT NULL COMMENT '昵称',
    avatar VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    gender ENUM('male', 'female', 'secret') DEFAULT 'secret' COMMENT '性别',
    birth_date DATE DEFAULT NULL COMMENT '出生日期',
    phone VARCHAR(20) DEFAULT NULL COMMENT '手机号',
    bio VARCHAR(200) DEFAULT NULL COMMENT '个人简介',
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active' COMMENT '状态',
    is_verified BOOLEAN DEFAULT FALSE COMMENT '邮箱是否验证',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    role ENUM('user', 'admin', 'counselor') DEFAULT 'user' COMMENT '用户角色',

    -- 隐私设置
    save_chat_history BOOLEAN DEFAULT TRUE COMMENT '保存对话历史',
    allow_ai_analysis BOOLEAN DEFAULT FALSE COMMENT '允许AI分析对话',
    chat_only_visible BOOLEAN DEFAULT FALSE COMMENT '对话仅自己可见',
    save_test_records BOOLEAN DEFAULT TRUE COMMENT '保存测试记录',
    test_only_visible BOOLEAN DEFAULT FALSE COMMENT '测试结果仅自己可见',
    allow_trend_analysis BOOLEAN DEFAULT TRUE COMMENT '允许查看趋势分析',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    deleted_at TIMESTAMP NULL DEFAULT NULL COMMENT '删除时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login_at TIMESTAMP NULL DEFAULT NULL COMMENT '最后登录时间',

    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='普通用户表';

-- ===============================================
-- 2. 咨询师表 (模型: app.models.counselor.Counselor → counselors)
-- ===============================================
CREATE TABLE IF NOT EXISTS counselors (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '咨询师ID',
    user_id BIGINT UNSIGNED DEFAULT NULL COMMENT '关联用户ID',

    -- 基本信息
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    avatar VARCHAR(500) DEFAULT NULL COMMENT '头像URL',
    gender ENUM('male', 'female', 'secret') DEFAULT 'secret' COMMENT '性别',
    title VARCHAR(100) DEFAULT NULL COMMENT '职称',

    -- 专业信息
    specialties VARCHAR(500) DEFAULT NULL COMMENT '擅长领域（多个用逗号分隔）',
    consultation_types VARCHAR(200) DEFAULT NULL COMMENT '咨询方式（video/voice/offline）',
    experience_years INT DEFAULT NULL COMMENT '从业年限',
    education VARCHAR(200) DEFAULT NULL COMMENT '学历背景',
    qualifications VARCHAR(500) DEFAULT NULL COMMENT '资质证书',

    -- 定价信息
    price_video FLOAT DEFAULT NULL COMMENT '视频咨询价格（元/小时）',
    price_voice FLOAT DEFAULT NULL COMMENT '语音咨询价格（元/小时）',
    price_offline FLOAT DEFAULT NULL COMMENT '线下咨询价格（元/小时）',

    -- 统计信息
    rating FLOAT DEFAULT 5.0 COMMENT '评分（0-5）',
    review_count INT DEFAULT 0 COMMENT '评价数量',
    consultation_count INT DEFAULT 0 COMMENT '咨询次数',

    -- 详细信息
    bio TEXT COMMENT '个人简介',
    approach TEXT COMMENT '咨询流派/方法',
    achievements TEXT COMMENT '成就荣誉',

    -- 状态
    status ENUM('pending_review', 'active', 'inactive', 'suspended') DEFAULT 'pending_review' COMMENT '状态',
    is_verified BOOLEAN DEFAULT FALSE COMMENT '是否认证',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',

    -- 申请相关
    application_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '申请状态',
    rejection_reason TEXT COMMENT '拒绝原因',
    reviewed_at DATETIME DEFAULT NULL COMMENT '审核时间',
    reviewed_by BIGINT DEFAULT NULL COMMENT '审核人ID（管理员）',

    -- 时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted_at DATETIME DEFAULT NULL COMMENT '删除时间',

    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询师表';

-- ===============================================
-- 3. 管理员表 (模型: app.models.admin.Admin → admins)
-- ===============================================
CREATE TABLE IF NOT EXISTS admins (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '管理员ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(100) DEFAULT NULL COMMENT '真实姓名',
    email VARCHAR(100) DEFAULT NULL COMMENT '邮箱',
    role ENUM('super_admin', 'admin', 'moderator') DEFAULT 'admin' COMMENT '角色',
    permissions TEXT COMMENT '权限列表（JSON格式）',
    status ENUM('active', 'inactive') DEFAULT 'active' COMMENT '状态',
    last_login_at DATETIME DEFAULT NULL COMMENT '最后登录时间',
    last_login_ip VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    deleted_at DATETIME DEFAULT NULL COMMENT '删除时间',
    INDEX idx_username (username),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员表';

-- ===============================================
-- 4. 心理测试问卷表 (模型: app.models.test.PsychologicalTest → psychological_tests)
-- ===============================================
CREATE TABLE IF NOT EXISTS psychological_tests (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '测试ID',
    test_code VARCHAR(50) NOT NULL UNIQUE COMMENT '测试代码(如SAS20)',
    title VARCHAR(200) NOT NULL COMMENT '测试标题',
    description TEXT COMMENT '测试描述',
    category VARCHAR(50) DEFAULT NULL COMMENT '测试分类: anxiety/depression/personality/stress',
    intro_text TEXT COMMENT '测试说明文字',
    total_questions INT DEFAULT 0 COMMENT '总题数',
    score_type VARCHAR(20) DEFAULT 'total' COMMENT '计分类型: total=总分, dimension=维度分',
    option_type VARCHAR(20) DEFAULT '4选项' COMMENT '选项类型: 4选项/5选项',
    scoring_rules JSON COMMENT '计分规则配置',
    result_rules JSON COMMENT '结果等级解读规则',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    hot_value INT DEFAULT 0 COMMENT '热度值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_test_code (test_code),
    INDEX idx_category (category),
    INDEX idx_sort_order (sort_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心理测试问卷表';

-- ===============================================
-- 5. 测试题目表 (模型: app.models.test.TestQuestion → test_questions)
-- ===============================================
CREATE TABLE IF NOT EXISTS test_questions (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '题目ID',
    test_id BIGINT UNSIGNED NOT NULL COMMENT '所属测试ID',
    question_number INT NOT NULL COMMENT '题目序号',
    question_text TEXT NOT NULL COMMENT '题目内容',
    options JSON NOT NULL COMMENT '选项配置',
    dimension VARCHAR(50) DEFAULT NULL COMMENT '所属维度',
    is_reverse BOOLEAN DEFAULT FALSE COMMENT '是否反向题',
    reverse_value INT DEFAULT NULL COMMENT '反向计分值配置',
    sort_order INT DEFAULT 0 COMMENT '排序序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE CASCADE,
    INDEX idx_test_id (test_id),
    UNIQUE KEY uk_test_question (test_id, question_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试题目表';

-- ===============================================
-- 6. 测试结果表 (模型: app.models.test.TestResult → test_results)
-- ===============================================
CREATE TABLE IF NOT EXISTS test_results (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '结果ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    questionnaire_id BIGINT UNSIGNED DEFAULT NULL COMMENT '问卷ID（旧字段，兼容用）',
    test_id BIGINT UNSIGNED DEFAULT NULL COMMENT '测试ID（新字段）',
    answers JSON NOT NULL COMMENT '答题记录',
    total_score INT DEFAULT NULL COMMENT '总得分',
    dimension_scores JSON COMMENT '各维度得分',
    result_level VARCHAR(50) DEFAULT NULL COMMENT '结果等级: none/mild/moderate/severe',
    result_title VARCHAR(100) DEFAULT NULL COMMENT '结果标题',
    result_description TEXT COMMENT '结果描述',
    suggestions TEXT COMMENT '建议内容',
    ai_suggestion TEXT COMMENT 'AI生成的个性化建议',
    is_favorited BOOLEAN DEFAULT FALSE COMMENT '是否收藏',
    is_favorite BOOLEAN DEFAULT FALSE COMMENT '是否收藏（兼容字段）',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (questionnaire_id) REFERENCES psychological_tests(id) ON DELETE SET NULL,
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_questionnaire_id (questionnaire_id),
    INDEX idx_test_id (test_id),
    INDEX idx_completed_at (completed_at),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户测试结果表';

-- ===============================================
-- 7. 测试进度表 (模型: app.models.test.TestProgress → test_progress)
-- ===============================================
CREATE TABLE IF NOT EXISTS test_progress (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '进度ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    test_id BIGINT UNSIGNED NOT NULL COMMENT '测试ID',
    answers JSON DEFAULT '{}' COMMENT '已答题目记录',
    current_question INT DEFAULT 1 COMMENT '当前答题进度',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (test_id) REFERENCES psychological_tests(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_test_id (test_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户答题进度表';

-- ===============================================
-- 8. 预约订单表 (模型: app.models.counselor.Appointment → appointments)
-- ===============================================
CREATE TABLE IF NOT EXISTS appointments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '预约ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',

    -- 预约信息
    appointment_no VARCHAR(50) NOT NULL UNIQUE COMMENT '预约编号',
    consultation_type ENUM('video', 'voice', 'offline') NOT NULL COMMENT '咨询方式',
    appointment_date DATETIME NOT NULL COMMENT '预约日期时间',
    duration INT DEFAULT 60 COMMENT '咨询时长（分钟）',

    -- 用户信息
    user_name VARCHAR(100) DEFAULT NULL COMMENT '预约人姓名',
    user_contact VARCHAR(50) DEFAULT NULL COMMENT '联系方式',
    problem_description TEXT COMMENT '问题描述',

    -- 价格信息
    price FLOAT NOT NULL COMMENT '咨询费用',
    paid_amount FLOAT DEFAULT 0 COMMENT '已付金额',

    -- 状态
    status ENUM('pending', 'confirmed', 'in_progress', 'completed', 'cancelled', 'refunded') DEFAULT 'pending' COMMENT '订单状态',
    cancel_reason TEXT COMMENT '取消原因',

    -- 咨询师备注
    counselor_notes TEXT COMMENT '咨询师备注',

    -- 提醒标记
    reminder_sent BOOLEAN DEFAULT FALSE COMMENT '是否已发送提醒邮件',
    reminder_sent_at DATETIME DEFAULT NULL COMMENT '提醒发送时间',

    -- 时间字段
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    confirmed_at DATETIME DEFAULT NULL COMMENT '确认时间',
    completed_at DATETIME DEFAULT NULL COMMENT '完成时间',
    cancelled_at DATETIME DEFAULT NULL COMMENT '取消时间',

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (counselor_id) REFERENCES counselors(id),
    INDEX idx_user_id (user_id),
    INDEX idx_counselor_id (counselor_id),
    INDEX idx_status (status),
    INDEX idx_appointment_date (appointment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约订单表';

-- ===============================================
-- 9. 咨询评价表 (模型: app.models.counselor.ConsultationReview → consultation_reviews)
-- ===============================================
CREATE TABLE IF NOT EXISTS consultation_reviews (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '评价ID',
    appointment_id BIGINT UNSIGNED NOT NULL COMMENT '预约ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',
    rating FLOAT NOT NULL COMMENT '评分（1-5）',
    tags VARCHAR(500) DEFAULT NULL COMMENT '评价标签（多个用逗号分隔）',
    content TEXT COMMENT '评价内容',
    is_anonymous BOOLEAN DEFAULT FALSE COMMENT '是否匿名',
    counselor_reply TEXT COMMENT '咨询师回复',
    replied_at DATETIME DEFAULT NULL COMMENT '回复时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (counselor_id) REFERENCES counselors(id),
    UNIQUE KEY uk_appointment_review (appointment_id),
    INDEX idx_counselor_id (counselor_id),
    INDEX idx_rating (rating)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询评价表';

-- ===============================================
-- 10. 咨询对话消息表 (模型: app.models.counselor.ConsultationMessage → consultation_messages)
-- ===============================================
CREATE TABLE IF NOT EXISTS consultation_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    appointment_id BIGINT UNSIGNED NOT NULL COMMENT '预约ID',
    sender_id BIGINT NOT NULL COMMENT '发送者ID',
    sender_type ENUM('user', 'counselor') NOT NULL COMMENT '发送者类型',
    message_type VARCHAR(30) DEFAULT 'text' COMMENT '消息类型',
    content TEXT COMMENT '消息内容',
    file_url VARCHAR(500) DEFAULT NULL COMMENT '文件URL',
    file_name VARCHAR(255) DEFAULT NULL COMMENT '文件名',
    file_size INT DEFAULT NULL COMMENT '文件大小（字节）',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    read_at DATETIME DEFAULT NULL COMMENT '读取时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (appointment_id) REFERENCES appointments(id),
    INDEX idx_appointment_id (appointment_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询对话消息表';

-- ===============================================
-- 11. 咨询师预约前沟通会话表 (模型: app.models.counselor.CounselorInquiry → counselor_inquiries)
-- ===============================================
CREATE TABLE IF NOT EXISTS counselor_inquiries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '会话ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后消息时间',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (counselor_id) REFERENCES counselors(id),
    INDEX idx_user_id (user_id),
    INDEX idx_counselor_id (counselor_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询师预约前沟通会话表';

-- ===============================================
-- 12. 预约前沟通消息表 (模型: app.models.counselor.InquiryMessage → inquiry_messages)
-- ===============================================
CREATE TABLE IF NOT EXISTS inquiry_messages (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '消息ID',
    inquiry_id BIGINT UNSIGNED NOT NULL COMMENT '会话ID',
    sender_id BIGINT NOT NULL COMMENT '发送者ID',
    sender_role ENUM('user', 'counselor') NOT NULL COMMENT '发送者角色',
    content TEXT NOT NULL COMMENT '消息内容',
    msg_type VARCHAR(20) DEFAULT 'text' COMMENT '消息类型 text/image',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
    FOREIGN KEY (inquiry_id) REFERENCES counselor_inquiries(id),
    INDEX idx_inquiry_id (inquiry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约前沟通消息表';

-- ===============================================
-- 13. 通知表 (用户/咨询师通知中心)
-- ===============================================
CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '通知ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '接收用户ID',
    type VARCHAR(50) NOT NULL COMMENT '通知类型',
    title VARCHAR(200) NOT NULL COMMENT '通知标题',
    content TEXT NOT NULL COMMENT '通知内容',
    related_id BIGINT UNSIGNED DEFAULT NULL COMMENT '关联业务ID',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_user_is_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='通知表';

-- ===============================================
-- 14. 心理知识文章表 (模型: app.models.knowledge.KnowledgeArticle → knowledge_articles)
-- ===============================================
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '文章ID',
    title VARCHAR(200) NOT NULL COMMENT '文章标题',
    summary VARCHAR(500) DEFAULT NULL COMMENT '文章摘要',
    cover_image VARCHAR(500) DEFAULT NULL COMMENT '封面图片URL',
    content TEXT NOT NULL COMMENT '文章内容（HTML或Markdown）',
    content_type ENUM('markdown', 'html') DEFAULT 'markdown' COMMENT '内容类型',
    category VARCHAR(50) DEFAULT NULL COMMENT '分类（anxiety/depression/emotion/career/family等）',
    tags VARCHAR(500) DEFAULT NULL COMMENT '标签（多个用逗号分隔）',
    author_id BIGINT UNSIGNED DEFAULT NULL COMMENT '作者ID',
    author_name VARCHAR(100) DEFAULT NULL COMMENT '作者名称',
    view_count INT DEFAULT 0 COMMENT '浏览次数',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    favorite_count INT DEFAULT 0 COMMENT '收藏数',
    comment_count INT DEFAULT 0 COMMENT '评论数',
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft' COMMENT '状态',
    is_featured BOOLEAN DEFAULT FALSE COMMENT '是否精选',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    seo_keywords VARCHAR(200) DEFAULT NULL COMMENT 'SEO关键词',
    seo_description VARCHAR(500) DEFAULT NULL COMMENT 'SEO描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    published_at DATETIME DEFAULT NULL COMMENT '发布时间',
    FOREIGN KEY (author_id) REFERENCES users(id),
    INDEX idx_category (category),
    INDEX idx_status (status),
    INDEX idx_view_count (view_count),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='心理知识文章表';

-- ===============================================
-- 15. 知识评论表 (模型: app.models.knowledge.KnowledgeComment → knowledge_comments)
-- ===============================================
CREATE TABLE IF NOT EXISTS knowledge_comments (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
    article_id BIGINT UNSIGNED NOT NULL COMMENT '文章ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    parent_id BIGINT UNSIGNED DEFAULT NULL COMMENT '父评论ID（回复功能）',
    is_visible BOOLEAN DEFAULT TRUE COMMENT '是否可见',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES knowledge_comments(id),
    INDEX idx_article_id (article_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识评论表';

-- ===============================================
-- 16. 知识收藏表 (模型: app.models.knowledge.KnowledgeFavorite → knowledge_favorites)
-- ===============================================
CREATE TABLE IF NOT EXISTS knowledge_favorites (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
    article_id BIGINT UNSIGNED NOT NULL COMMENT '文章ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
    FOREIGN KEY (article_id) REFERENCES knowledge_articles(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_user_article (article_id, user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_article_id (article_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识收藏表';

-- ===============================================
-- 17. 知识点赞表 (模型: app.models.knowledge.KnowledgeLike → knowledge_likes)
-- ===============================================
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
-- 18. 对话表 (模型: app.models.chat.ChatDialogue → chat_dialogues)
-- ===============================================
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

-- ===============================================
-- 19. 消息表 (模型: app.models.chat.ChatMessage → chat_messages)
-- ===============================================
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

-- ===============================================
-- 20. 标签表 (模型: app.models.chat.ChatTag → chat_tags)
-- ===============================================
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

-- ===============================================
-- 21. 对话标签关联表 (模型: app.models.chat.ChatDialogueTag → chat_dialogue_tags)
-- ===============================================
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
-- 22. 验证码表 (无 SQLAlchemy 模型，直接使用)
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
-- 插入初始数据
-- ===============================================
-- 密码均为 123456 (BCrypt加密后: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i)
-- 生产环境请务必修改密码！
-- ===============================================

-- 1. 插入默认管理员
INSERT INTO admins (username, password_hash, real_name, email, role, status) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '系统管理员', 'admin@soulstation.com', 'super_admin', 'active');

-- 2. 插入咨询师/用户测试账号
INSERT INTO users (email, password_hash, nickname, gender, role, status, is_verified) VALUES
('consultant@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '张咨询师', 'female', 'counselor', 'active', TRUE);

INSERT INTO counselors (user_id, name, title, gender, specialties, consultation_types, experience_years, education, qualifications, price_video, price_voice, bio, status, is_verified, application_status)
SELECT id AS user_id, '张咨询师' AS name, '国家二级心理咨询师' AS title, 'female' AS gender, '焦虑症,抑郁症,情绪管理' AS specialties, 'video,voice' AS consultation_types, 5 AS experience_years, '心理学硕士' AS education, '国家二级心理咨询师证书' AS qualifications, 200.00 AS price_video, 150.00 AS price_voice, '国家二级心理咨询师，从事心理咨询工作5年，擅长认知行为疗法。' AS bio, 'active' AS status, TRUE AS is_verified, 'approved' AS application_status
FROM users WHERE email = 'consultant@test.com';

-- 3. 插入普通用户测试账号
INSERT INTO users (email, password_hash, nickname, gender, role, status, is_verified) VALUES
('user@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', '测试用户', 'male', 'user', 'active', TRUE);

-- ===============================================
-- 创建视图
-- ===============================================

-- 用户测试结果统计视图
CREATE OR REPLACE VIEW v_user_test_stats AS
SELECT
    u.id AS user_id,
    u.nickname,
    COUNT(tr.id) AS total_tests,
    COUNT(DISTINCT COALESCE(tr.test_id, tr.questionnaire_id)) AS unique_tests
FROM users u
LEFT JOIN test_results tr ON u.id = tr.user_id
GROUP BY u.id, u.nickname;

-- 咨询师统计视图
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
-- 数据库初始化完成
-- ===============================================
SELECT '========================================' AS '';
SELECT '✓ SoulStation 数据库初始化完成！' AS '';
SELECT '========================================' AS '';

