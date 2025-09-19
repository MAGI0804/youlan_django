package routes

import (
	"django_to_go/controllers"

	"github.com/gin-gonic/gin"
)

// InitRoutes 初始化路由配置 - 完全匹配Django版本
func InitRoutes(router *gin.Engine) {
	// 初始化控制器
	userController := &controllers.UserController{}
	commodityController := &controllers.CommodityController{}
	orderController := &controllers.OrderController{}
	accessTokenController := &controllers.AccessTokenController{}
	operationUserController := &controllers.OperationUserController{}
	activityController := &controllers.ActivityController{}
	addressController := &controllers.AddressController{}
	cartController := &controllers.CartController{}

	// JWT 令牌相关路由 - 与Django版本完全匹配
	router.POST("api/token/obtain/", accessTokenController.TokenObtainPair)
	router.POST("api/token/refresh/", accessTokenController.TokenRefresh)

	// Ordinary User 相关路由 - 完全匹配Django users.urls
	router.POST("ordinary_user/add_data", userController.UserRegistration)
	router.POST("ordinary_user/find_data", userController.UserQuery)
	router.POST("ordinary_user/Modify_data", userController.UserModify)
	router.GET("ordinary_user/get_user_id", userController.UserGetID)
	router.POST("ordinary_user/verification_status", userController.VerificationStatus)
	router.POST("ordinary_user/wechat_login", userController.WechatLogin)

	// Commodity 相关路由 - 完全匹配Django commodity.urls
	router.GET("commodity/get_all_categories", commodityController.GetAllCategories)
	router.GET("commodity/search_style_codes", commodityController.SearchStyleCodes)
	router.POST("commodity/add_goods", commodityController.AddGoods)
	router.POST("commodity/delete_goods", commodityController.DeleteGoods)
	router.GET("commodity/search_commodity_data", commodityController.SearchCommodityData)
	router.GET("commodity/goods_query", commodityController.GoodsQuery)
	router.POST("commodity/change_commodity_data", commodityController.ChangeCommodityData)
	router.POST("commodity/change_commodity_status_online", commodityController.ChangeCommodityStatusOnline)
	router.POST("commodity/change_commodity_status_offline", commodityController.ChangeCommodityStatusOffline)
	router.GET("commodity/get_commodity_status", commodityController.GetCommodityStatus)
	router.GET("commodity/search_products_by_name", commodityController.SearchProductsByName)
	router.POST("commodity/batch_get_products_by_ids", commodityController.BatchGetProductsByIDs)
	router.POST("commodity/style-code/status/online", commodityController.ChangeStyleCodeStatusOnline)
	router.POST("commodity/style-code/status/offline", commodityController.ChangeStyleCodeStatusOffline)
	router.GET("commodity/style-code/commodities", commodityController.GetCommoditiesByStyleCode)

	// Order 相关路由 - 完全匹配Django order.urls
	router.POST("order/add_order", orderController.AddOrder)
	router.GET("order/query_order_data", orderController.QueryOrderData)
	router.POST("order/change_receiving_data", orderController.ChangeReceivingData)
	router.POST("order/change_status", orderController.ChangeStatus)
	router.GET("order/orders_query", orderController.OrdersQuery)
	router.POST("order/batch_orders_query", orderController.BatchOrdersQuery)
	router.POST("order/update_express_info", orderController.UpdateExpressInfo)
	router.POST("order/sync_logistics_info", orderController.SyncLogisticsInfo)

	// Access Token 相关路由 - 完全匹配Django access_token.urls
	router.POST("access_token/get_token", accessTokenController.GetToken)
	router.POST("access_token/get_ips", accessTokenController.GetIPs)

	// OperationUser 相关路由
	router.POST("OperationUser/add_service_user", operationUserController.AddServiceUser)
	router.POST("OperationUser/add_operation_user", operationUserController.AddOperationUser)
	router.POST("OperationUser/verification_status", operationUserController.VerificationStatus)
	router.POST("OperationUser/change_password", operationUserController.ChangePassword)

	// Activity 相关路由
	router.POST("activity/add_activity_img", activityController.AddActivityImg)
	router.POST("activity/update_activity_image_relations", activityController.UpdateActivityImageRelations)
	router.POST("activity/activity_image_online", activityController.ActivityImageOnline)
	router.POST("activity/activity_image_offline", activityController.ActivityImageOffline)
	router.POST("activity/batch_query_activity_images", activityController.BatchQueryActivityImages)

	// Address 相关路由
	router.POST("address/add_address", addressController.AddAddress)
	router.POST("address/delete_address", addressController.DeleteAddress)
	router.POST("address/update_address", addressController.UpdateAddress)
	router.POST("address/set_default_address", addressController.SetDefaultAddress)
	router.POST("address/get_addresses", addressController.GetAddresses)
	router.POST("address/get_address_by_id", addressController.GetAddressByID)

	// Cart 相关路由
	router.POST("cart/add_to_cart", cartController.AddToCart)
	router.POST("cart/batch_delete_from_cart", cartController.BatchDeleteFromCart)
	router.POST("cart/query_cart_items", cartController.QueryCartItems)
	router.POST("cart/update_cart_item_quantity", cartController.UpdateCartItemQuantity)
	router.POST("cart/increase_cart_item_quantity", cartController.IncreaseCartItemQuantity)
	router.POST("cart/decrease_cart_item_quantity", cartController.DecreaseCartItemQuantity)
	router.POST("cart/clear_cart", cartController.ClearCart)

	// 测试路由
	router.GET("api/test/", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "Server is running"})
	})

	// 健康检查路由
	router.GET("api/health/", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// 404 路由 - 完全匹配Django的自定义404视图
	router.NoRoute(func(c *gin.Context) {
		c.JSON(404, gin.H{"error": "页面不存在"})
	})

	// 405 路由
	router.NoMethod(func(c *gin.Context) {
		c.JSON(405, gin.H{"error": "请求方法不允许"})
	})
}
