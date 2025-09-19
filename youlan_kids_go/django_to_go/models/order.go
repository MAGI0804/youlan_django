package models

import (
	"time"

	"gorm.io/gorm"
)

// Order 订单模型
type Order struct {
	OrderID          string    `gorm:"column:order_id;primaryKey;size:100" json:"order_id"`
	UserID           int       `gorm:"column:user_id;index" json:"user_id"`
	CommodityID      string    `gorm:"column:commodity_id;size:100;index" json:"commodity_id"`
	CommodityName    string    `gorm:"column:commodity_name;size:255;not null" json:"commodity_name"`
	Quantity         int       `gorm:"column:quantity;not null;default:1" json:"quantity"`
	Price            float64   `gorm:"column:price;not null" json:"price"`
	TotalAmount      float64   `gorm:"column:total_amount;not null" json:"total_amount"`
	ReceiverName     string    `gorm:"column:receiver_name;size:100;not null" json:"receiver_name"`
	ReceiverPhone    string    `gorm:"column:receiver_phone;size:11;not null" json:"receiver_phone"`
	Province         string    `gorm:"column:province;size:50;not null" json:"province"`
	City             string    `gorm:"column:city;size:50;not null" json:"city"`
	County           string    `gorm:"column:county;size:50;not null" json:"county"`
	DetailedAddress  string    `gorm:"column:detailed_address;size:255;not null" json:"detailed_address"`
	Status           string    `gorm:"column:status;size:20;not null" json:"status"`
	PaymentMethod    string    `gorm:"column:payment_method;size:50;null" json:"payment_method"`
	PaymentTime      time.Time `gorm:"column:payment_time;null" json:"payment_time"`
	DeliveryMethod   string    `gorm:"column:delivery_method;size:50;null" json:"delivery_method"`
	ExpressCompany   string    `gorm:"column:express_company;size:100;null" json:"express_company"`
	ExpressNumber    string    `gorm:"column:express_number;size:100;null" json:"express_number"`
	LogisticsInfo    string    `gorm:"column:logistics_info;type:text;null" json:"logistics_info"`
	OrderTime        time.Time `gorm:"column:order_time;autoCreateTime" json:"order_time"`
	Remarks          string    `gorm:"column:remarks;type:text;null" json:"remarks"`
}

// TableName 设置表名
func (Order) TableName() string {
	return "order_order"
}

// BeforeSave GORM钩子，确保gorm包被使用
func (o *Order) BeforeSave(*gorm.DB) error {
	return nil
}

// OrderLogistics 订单物流信息模型
type OrderLogistics struct {
	ID             int       `gorm:"column:id;primaryKey;autoIncrement" json:"id"`
	OrderID        string    `gorm:"column:order_id;size:100;index" json:"order_id"`
	ExpressCompany string    `gorm:"column:express_company;size:100;not null" json:"express_company"`
	ExpressNumber  string    `gorm:"column:express_number;size:100;not null" json:"express_number"`
	Status         string    `gorm:"column:status;size:50;not null" json:"status"`
	Details        string    `gorm:"column:details;type:text;not null" json:"details"`
	LastUpdated    time.Time `gorm:"column:last_updated;autoUpdateTime" json:"last_updated"`
}

// TableName 设置表名
func (OrderLogistics) TableName() string {
	return "order_logistics"
}