package models

import (
	"time"
	"gorm.io/gorm"
)

// Address 用户地址模型
type Address struct {
	ID              int       `gorm:"column:id;primaryKey;autoIncrement" json:"id"`
	UserID          int       `gorm:"column:user_id;index" json:"user_id"`
	ReceiverName    string    `gorm:"column:receiver_name;size:100;not null" json:"receiver_name"`
	ReceiverPhone   string    `gorm:"column:receiver_phone;size:11;not null" json:"receiver_phone"`
	Province        string    `gorm:"column:province;size:50;not null" json:"province"`
	City            string    `gorm:"column:city;size:50;not null" json:"city"`
	County          string    `gorm:"column:county;size:50;not null" json:"county"`
	DetailedAddress string    `gorm:"column:detailed_address;size:255;not null" json:"detailed_address"`
	IsDefault       bool      `gorm:"column:is_default;default:false" json:"is_default"`
	CreatedAt       time.Time `gorm:"column:created_at;autoCreateTime" json:"created_at"`
	UpdatedAt       time.Time `gorm:"column:updated_at;autoUpdateTime" json:"updated_at"`
}

// TableName 设置表名
func (Address) TableName() string {
	return "address_address"
}