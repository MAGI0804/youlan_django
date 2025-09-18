package routes

import (
	"github.com/youlan-kids/youlan_kids_go/django_to_go/controllers"
	"github.com/gin-gonic/gin"
)

// InitRoutes 初始化路由配置
func InitRoutes(router *gin.Engine) {
	// 初始化控制器
	userController := &controllers.UserController{}
	commodityController := &controllers.CommodityController{}
	orderController := &controllers.OrderController{}

	// 公共路由
	public := router.Group("/")
	{
		// 用户相关路由
		public.POST("api/users/registration/", userController.UserRegistration)
		public.POST("api/users/query/", userController.UserQuery)
		public.POST("api/users/modify/", userController.UserModify)
		public.GET("api/users/get_id/", userController.UserGetID)
		public.POST("api/users/verification/", userController.VerificationStatus)
		public.POST("api/users/wechat_login/", userController.WechatLogin)

		// 商品相关路由
		public.GET("api/commodity/list/", commodityController.CommodityList)
		public.GET("api/commodity/detail/:id", commodityController.CommodityDetail)
		public.POST("api/commodity/create/", commodityController.CommodityCreate)
		public.PUT("api/commodity/update/:id", commodityController.CommodityUpdate)
		public.DELETE("api/commodity/delete/:id", commodityController.CommodityDelete)

		// 订单相关路由
		public.GET("api/order/list/", orderController.OrderList)
		public.GET("api/order/detail/:id", orderController.OrderDetail)
		public.POST("api/order/create/", orderController.OrderCreate)
		public.PUT("api/order/update/:id", orderController.OrderUpdate)
		public.PUT("api/order/cancel/:id", orderController.OrderCancel)
		public.PUT("api/order/pay/:id", orderController.OrderPay)
		public.PUT("api/order/deliver/:id", orderController.OrderDeliver)

		// 测试路由
		public.GET("api/test/", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "Server is running"})
		})

		// 健康检查路由
		public.GET("api/health/", func(c *gin.Context) {
			c.JSON(200, gin.H{"status": "ok"})
		})

		// 404 路由
		router.NoRoute(func(c *gin.Context) {
			c.JSON(404, gin.H{"error": "Route not found"})
		})

		// 405 路由
		router.NoMethod(func(c *gin.Context) {
			c.JSON(405, gin.H{"error": "Method not allowed"})
		})
	}
}