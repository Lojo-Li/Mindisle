-- B 线（咨询师与排班）：咨询师可预约时段表
-- 可重复执行（CREATE TABLE IF NOT EXISTS）
-- 用途：咨询师在工作台发布可预约时段，预约成功后对应时段锁定为 booked

CREATE TABLE IF NOT EXISTS counselor_time_slots (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '时段ID',
    counselor_id BIGINT UNSIGNED NOT NULL COMMENT '咨询师ID',
    slot_date DATE NOT NULL COMMENT '时段日期',
    start_time TIME NOT NULL COMMENT '开始时间',
    end_time TIME NOT NULL COMMENT '结束时间',
    status ENUM('available','booked','disabled') NOT NULL DEFAULT 'available' COMMENT '时段状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    KEY idx_slot_counselor_date (counselor_id, slot_date),
    KEY idx_slot_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='咨询师可预约时段表';
