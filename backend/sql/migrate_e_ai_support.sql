-- ===============================================
-- E 线（AI 心理支持）增量迁移脚本
-- 对应模型: app/models/risk.py
-- 幂等：可重复执行，已存在的表不会被改动
--
-- 执行方式：
--   mysql -u root -p soulstation < backend/sql/migrate_e_ai_support.sql
--
-- 说明：
--   外键统一写在这里，而不是交给 SQLAlchemy 的 create_all。
--   因为 init.sql 的主键是 BIGINT UNSIGNED，SQLAlchemy 的 BigInteger 是有符号的，
--   如果让 create_all 建表会因外键类型不兼容直接报错。
-- ===============================================

USE soulstation;

-- -----------------------------------------------
-- 1. 风险事件表
--    记录"危险信号被识别"这件事本身，是分流的证据链
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS risk_events (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '事件ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    dialogue_id BIGINT UNSIGNED DEFAULT NULL COMMENT '对话ID',
    message_id BIGINT UNSIGNED DEFAULT NULL COMMENT '触发消息ID',

    level SMALLINT NOT NULL COMMENT '风险等级：1关注 2警示 3紧急',
    keywords VARCHAR(300) DEFAULT NULL COMMENT '命中的关键词，逗号分隔',
    detected_by ENUM('keyword', 'model', 'manual') DEFAULT 'keyword' COMMENT '识别来源',
    action_taken VARCHAR(200) DEFAULT NULL COMMENT '已执行的处置动作',

    handled_status ENUM('pending', 'contacted', 'closed') DEFAULT 'pending' COMMENT '处置状态',
    handled_by BIGINT UNSIGNED DEFAULT NULL COMMENT '处置人',
    note VARCHAR(500) DEFAULT NULL COMMENT '处置备注',
    handled_at DATETIME DEFAULT NULL COMMENT '处置时间',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    KEY idx_risk_level_status (level, handled_status),
    KEY idx_risk_user (user_id, created_at),

    CONSTRAINT fk_risk_user FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT fk_risk_dialogue FOREIGN KEY (dialogue_id) REFERENCES chat_dialogues (id),
    CONSTRAINT fk_risk_message FOREIGN KEY (message_id) REFERENCES chat_messages (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '风险事件表';

-- -----------------------------------------------
-- 2. AI 回答引用来源表
--    回答 -> 知识条目，让"有依据"可查证
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS ai_message_sources (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    message_id BIGINT UNSIGNED NOT NULL COMMENT 'AI 消息ID',
    vector_id VARCHAR(64) DEFAULT NULL COMMENT 'ChromaDB 中的向量ID',
    doc_title VARCHAR(200) DEFAULT NULL COMMENT '知识条目标题',
    snippet TEXT COMMENT '引用片段',
    score FLOAT DEFAULT NULL COMMENT '相似度 0~1',
    rank SMALLINT DEFAULT NULL COMMENT '排序，1 为最相关',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    KEY idx_source_message (message_id),
    CONSTRAINT fk_source_message FOREIGN KEY (message_id) REFERENCES chat_messages (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'AI 回答引用来源表';

-- -----------------------------------------------
-- 3. AI 回答反馈表
--    差评答案 -> 补知识，形成运营闭环
-- -----------------------------------------------
CREATE TABLE IF NOT EXISTS ai_feedback (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    message_id BIGINT UNSIGNED NOT NULL COMMENT 'AI 消息ID',
    user_id BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
    rating SMALLINT DEFAULT NULL COMMENT '1 有用 / -1 没用',
    reason VARCHAR(200) DEFAULT NULL COMMENT '原因',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    UNIQUE KEY uq_feedback_message_user (message_id, user_id),
    CONSTRAINT fk_feedback_message FOREIGN KEY (message_id) REFERENCES chat_messages (id),
    CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES users (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'AI 回答反馈表';
