package models

import (
	"time"

	"gorm.io/gorm"
)

// CartItem 购物车商品项模型
type CartItem struct {
	ID          int       `gorm:"column:id;primaryKey;autoIncrement" json:"id"`
	UserID      int       `gorm:"column:user_id;index" json:"user_id"`
	CommodityID string    `gorm:"column:commodity_id;size:100;index" json:"commodity_id"`
	Quantity    int       `gorm:"column:quantity;not null;default:1" json:"quantity"`
	Selected    bool      `gorm:"column:selected;default:true" json:"selected"`
	CreatedAt   time.Time `gorm:"column:created_at;autoCreateTime" json:"created_at"`
	UpdatedAt   time.Time `gorm:"column:updated_at;autoUpdateTime" json:"updated_at"`
}

// TableName 设置表名
func (CartItem) TableName() string {
	return "cart_cartitem"
}

// BeforeSave GORM钩子，确保gorm包被使用
func (c *CartItem) BeforeSave(*gorm.DB) error {
	return nil
}